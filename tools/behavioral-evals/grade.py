#!/usr/bin/env python3
"""Deterministic behavioral grader for the craft-code discipline.

Given a produced git repository and a scenario definition, it mechanically
checks the assertions the craft-code pipeline should have honored — built test-first,
no doubles of owned/in-process code, no non-null-assertion escape hatches,
separate refactor commits, Given/When/Then test names, no detached work left
without a failure owner, and so on
 — and emits a
grading.json in the same shape the existing benchmark aggregator understands.

Assertions whose `check` is "judgment" are left passed=null: they need a human
or model reviewer (immutability, method size nuance, the gate-refusal behavior
that lives in the transcript, not the repo). Everything else is decided here,
cheaply and repeatably, so this can run as a regression guard.

stdlib only; runs on Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from typing import Optional

CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".cs", ".rs", ".go", ".py"}
TEST_NAME = re.compile(r"(\.test\.|\.spec\.|_test\.|_spec\.|Tests?\.)", re.I)
TEST_DIR = re.compile(r"(^|/)(tests?|__tests__|spec|specs)(/|$)", re.I)

MOCK_PATTERNS = [
    r"\bjest\.fn\b", r"\bjest\.mock\b", r"\bjest\.spyOn\b",
    r"\bvi\.fn\b", r"\bvi\.mock\b", r"\bvi\.spyOn\b",
    r"\bsinon\.", r"\bcreateMock\b", r"\bMock<", r"\bnew Mock\b",
    r"\bSubstitute\.For\b", r"\bMoq\b", r"\bmock\(", r"\bstub\(",
    r"\bunittest\.mock\b", r"\bMagicMock\b", r"@patch\b",
]
MOCK_RE = re.compile("|".join(MOCK_PATTERNS))

# non-null assertion / null-forgiving operator: `foo!.`, `foo!)`, `foo!;`, `arr]!,`
# excludes `!=`, `!==`, `!!`, logical-not `!foo`, and TS definite-assignment `x!:`
NONNULL_RE = re.compile(r"[\w\)\]]\s*!(?![=!])(?=\s*[\.\)\];,])")

# detached work: started without a caller waiting on it. Deliberately narrow --
# these five shapes are unambiguous; a floating promise in JS is not detectable
# without type information, so it is left to the judgment assertions.
DETACHED_PATTERNS = [
    r"\basync\s+void\b",                     # C#: throws on the thread pool
    r"^\s*_\s*=\s*[\w\.]+\s*\(",             # C#: discarded task
    r"^\s*void\s+[\w\.]+\s*\(",              # TS: deliberately-ignored promise
    r"^\s*go\s+[\w\.]+\s*\(",                # Go: bare goroutine
    r"^\s*(?:asyncio|loop)\.create_task\s*\(",  # Python: unreferenced task
]
DETACHED_RE = re.compile("|".join(DETACHED_PATTERNS), re.M)
GUARD_RE = re.compile(r"\b(try|catch|except|recover|Catch)\b")

TITLE_RE = re.compile(r"""(?:\bit|\btest|\bdescribe)\s*\(\s*['"`]([^'"`]+)['"`]""")
# naming.md sanctions a describe/it block as surface syntax "but keep the
# Given/When/Then structure intact" -- so the pair is judged composed, the way a
# reader sees it, not as two fragments neither of which reads as a spec alone.
DESCRIBE_RE = re.compile(r"""\bdescribe\s*\(\s*['"`]([^'"`]+)['"`]""")
CASE_RE = re.compile(r"""(?:\bit|\btest)\s*\(\s*['"`]([^'"`]+)['"`]""")
GWT_RE = re.compile(r"(given\b.*\bwhen\b.*\bthen\b)|(\bwhen\b.*\bthen\b)", re.I)


def sh(args: list[str], cwd: str) -> tuple[int, str]:
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=600)
        return p.returncode, (p.stdout + p.stderr)
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def walk_code(repo: str):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist", "build", "bin", "obj", "target", "vendor")]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in CODE_EXT:
                yield os.path.join(root, f)


def is_test_file(path: str) -> bool:
    return bool(TEST_NAME.search(os.path.basename(path)) or TEST_DIR.search(path.replace(os.sep, "/")))


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def rel(repo: str, path: str) -> str:
    return os.path.relpath(path, repo).replace(os.sep, "/")


# --- git history ----------------------------------------------------------

def git_history(repo: str):
    """Return list of commits (chronological) as dicts: subject, files[(status, path)], is_merge."""
    rc, out = sh(["git", "log", "--reverse", "--no-merges", "--format=@@@%H%x1f%s", "--name-status"], repo)
    if rc != 0:
        return []
    commits = []
    cur = None
    for line in out.splitlines():
        if line.startswith("@@@"):
            if cur:
                commits.append(cur)
            h, subj = line[3:].split("\x1f", 1)
            cur = {"hash": h, "subject": subj, "files": []}
        elif line.strip() and cur is not None:
            parts = line.split("\t")
            if len(parts) >= 2:
                cur["files"].append((parts[0][0], parts[-1].replace(os.sep, "/")))
    if cur:
        commits.append(cur)
    return commits


# --- checks ---------------------------------------------------------------

def check_suite_passes(repo: str, cfg: dict, test_cmd: Optional[str]):
    cmd = test_cmd or cfg.get("test_cmd")
    if not cmd:
        return None, "no test command provided (pass --test-cmd or scenario config.test_cmd)"
    rc, out = sh(["bash", "-lc", cmd], repo)
    tail = out.strip().splitlines()[-3:] if out.strip() else []
    return rc == 0, f"`{cmd}` exit={rc}; " + " | ".join(tail)[:200]


def check_test_before_code(repo: str, commits) -> tuple[Optional[bool], str]:
    first_test = None
    first_prod = None
    for i, c in enumerate(commits):
        for status, path in c["files"]:
            if status not in ("A", "M"):
                continue
            ext = os.path.splitext(path)[1]
            if ext not in CODE_EXT:
                continue
            if is_test_file(path):
                if first_test is None:
                    first_test = (i, c["subject"], path)
            else:
                if first_prod is None:
                    first_prod = (i, c["subject"], path)
    if first_prod is None:
        return None, "no production code file found in history"
    if first_test is None:
        return False, f"production code appears (commit '{first_prod[1]}') with no test ever committed"
    ok = first_test[0] <= first_prod[0]
    return ok, (f"first test @commit#{first_test[0]} ('{first_test[1]}'), "
                f"first prod @commit#{first_prod[0]} ('{first_prod[1]}') → "
                + ("test-first" if ok else "code-before-test"))


def check_multiple_small_commits(commits) -> tuple[Optional[bool], str]:
    n = len(commits)
    big = [c["subject"] for c in commits if len(c["files"]) > 15]
    ok = n >= 3
    ev = f"{n} non-merge commits"
    if big:
        ev += f"; {len(big)} large commit(s) (>15 files)"
    return ok, ev


def check_separate_refactor_commits(commits) -> tuple[Optional[bool], str]:
    refactor = [c for c in commits if re.match(r"\s*refactor", c["subject"], re.I)]
    bundled = [c["subject"] for c in commits
               if re.search(r"\brefactor", c["subject"], re.I) and re.search(r"\b(add|feat|implement|fix)\b", c["subject"], re.I)
               and not re.match(r"\s*refactor", c["subject"], re.I)]
    if bundled:
        return False, "commit bundles behavior + refactor: " + "; ".join(bundled[:2])
    if refactor:
        return True, f"{len(refactor)} standalone refactor commit(s): " + "; ".join(c["subject"] for c in refactor[:2])
    return True, "no refactor commits (nothing to separate)"


def scan(repo: str, want_test: bool, regex: re.Pattern):
    hits = []
    for path in walk_code(repo):
        if is_test_file(path) != want_test:
            continue
        text = read(path)
        for m in regex.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{rel(repo, path)}:{line}")
    return hits


def check_no_owned_mocks(repo: str) -> tuple[Optional[bool], str]:
    hits = scan(repo, want_test=True, regex=MOCK_RE)
    if hits:
        return False, f"{len(hits)} mock/stub site(s) in tests: " + ", ".join(hits[:5])
    return True, "no mock/stub/spy of owned or in-process code found in tests"


def check_no_non_null_assertion(repo: str) -> tuple[Optional[bool], str]:
    hits = scan(repo, want_test=False, regex=NONNULL_RE)
    if hits:
        return False, f"{len(hits)} non-null-assertion site(s): " + ", ".join(hits[:5])
    return True, "no non-null-assertion / null-forgiving operator in production code"


def composed_test_titles(source: str) -> list[str]:
    """Test titles as a reader sees them: each case joined to its enclosing describe."""
    titles, context = [], None
    for line in source.splitlines():
        describe = DESCRIBE_RE.search(line)
        if describe:
            context = describe.group(1)
            continue
        case = CASE_RE.search(line)
        if case:
            titles.append(f"{context} {case.group(1)}" if context else case.group(1))
    if not titles:
        titles = TITLE_RE.findall(source)
    return titles


def check_gwt_test_names(repo: str) -> tuple[Optional[bool], str]:
    titles = []
    for path in walk_code(repo):
        if not is_test_file(path):
            continue
        titles += composed_test_titles(read(path))
    titles = [t for t in titles if len(t.split()) >= 2]
    if not titles:
        return None, "no test titles found to check"
    good = [t for t in titles if GWT_RE.search(t)]
    ok = len(good) >= max(1, int(0.6 * len(titles)))
    return ok, f"{len(good)}/{len(titles)} test titles follow Given/When/Then"


def check_detached_work_owned(repo: str) -> tuple[Optional[bool], str]:
    """Every detached call site has a visible failure owner.

    Heuristic by design: a hit counts as owned when a try/catch (or the language's
    equivalent) appears within 15 lines either side -- the same glance a reviewer
    makes. It catches the shape the discipline cares about: work started with
    nobody to hand a failure to.
    """
    hits, unowned = [], []
    for path in walk_code(repo):
        if is_test_file(path):
            continue
        lines = read(path).splitlines()
        for i, line in enumerate(lines):
            if not DETACHED_RE.search(line):
                continue
            where = f"{rel(repo, path)}:{i + 1}"
            hits.append(where)
            window = "\n".join(lines[max(0, i - 15):i + 16])
            if not GUARD_RE.search(window):
                unowned.append(where)
    if not hits:
        return True, "no detached call sites found in production code"
    if unowned:
        return False, f"{len(unowned)}/{len(hits)} detached call site(s) with no visible failure owner: " + ", ".join(unowned[:5])
    return True, f"{len(hits)} detached call site(s), each with a guard in scope: " + ", ".join(hits[:5])


CHECKS = {
    "test_before_code": lambda repo, cfg, commits, tc: check_test_before_code(repo, commits),
    "multiple_small_commits": lambda repo, cfg, commits, tc: check_multiple_small_commits(commits),
    "separate_refactor_commits": lambda repo, cfg, commits, tc: check_separate_refactor_commits(commits),
    "no_owned_mocks": lambda repo, cfg, commits, tc: check_no_owned_mocks(repo),
    "no_non_null_assertion": lambda repo, cfg, commits, tc: check_no_non_null_assertion(repo),
    "gwt_test_names": lambda repo, cfg, commits, tc: check_gwt_test_names(repo),
    "suite_passes": lambda repo, cfg, commits, tc: check_suite_passes(repo, cfg, tc),
    "detached_work_owned": lambda repo, cfg, commits, tc: check_detached_work_owned(repo),
}


def grade(repo: str, scenario: dict, test_cmd: Optional[str]) -> dict:
    commits = git_history(repo)
    cfg = scenario.get("config", {})
    expectations = []
    for a in scenario["assertions"]:
        check = a.get("check", "judgment")
        if check == "judgment" or check not in CHECKS:
            passed, evidence = None, a.get("note", "needs human/model review")
        else:
            passed, evidence = CHECKS[check](repo, cfg, commits, test_cmd)
        expectations.append({"text": a["text"], "passed": passed, "evidence": evidence})

    decided = [e for e in expectations if e["passed"] is not None]
    passed = sum(1 for e in decided if e["passed"])
    failed = sum(1 for e in decided if e["passed"] is False)
    needs_review = sum(1 for e in expectations if e["passed"] is None)
    return {
        "run_id": scenario.get("id", "behavioral"),
        "summary": {
            "passed": passed,
            "failed": failed,
            "needs_review": needs_review,
            "total": len(expectations),
            "pass_rate": round(passed / len(decided), 3) if decided else None,
        },
        "expectations": expectations,
    }


def main():
    ap = argparse.ArgumentParser(description="Deterministic craft-code behavioral grader")
    ap.add_argument("--repo", required=True, help="path to the produced git repository")
    ap.add_argument("--scenario", required=True, help="path to the scenario JSON")
    ap.add_argument("--test-cmd", default=None, help="command to run the unit suite (overrides scenario)")
    ap.add_argument("--out", default=None, help="write grading.json here (default: stdout)")
    args = ap.parse_args()

    with open(args.scenario) as fh:
        scenario = json.load(fh)
    result = grade(os.path.abspath(args.repo), scenario, args.test_cmd)
    text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
