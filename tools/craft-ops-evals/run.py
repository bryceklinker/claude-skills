#!/usr/bin/env python3
"""Run a craft-ops eval set against one checkout and grade each response.

For every eval in the set, a `claude -p` session is told to follow the skill at
<root>/craft-ops/skills/<skill>/SKILL.md and answer the prompt. A separate call
then grades the response against the eval's assertions, blind to which checkout
produced it. Resumable: a response or grade already on disk is reused.

Usage:
  run.py --set deployment-design.json --root <checkout> --out <dir> [--runs 3] [--evals name ...]

Writes <dir>/<skill>.<eval>.<run>.out.md and .grade.json, and prints passed/total per run.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LIMIT_MARKERS = ("hit your session limit", "hit your weekly limit", "Failed to authenticate")


def claude(prompt: str, cwd: Path) -> str:
    """One headless call, waiting out usage limits rather than recording them as output."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    for attempt in range(1, 200):
        result = subprocess.run(["claude", "-p", prompt, "--dangerously-skip-permissions"],
                                capture_output=True, text=True, cwd=cwd, env=env, timeout=1800)
        text = result.stdout.strip()
        if result.returncode == 0 and text and not any(m in text for m in LIMIT_MARKERS):
            return text
        pause = min(60 * attempt, 900)
        print(f"  claude failed ({text[:80] or result.returncode}); retrying in {pause}s", file=sys.stderr)
        time.sleep(pause)
    raise RuntimeError("claude never succeeded")


def run_eval(skill: str, ev: dict, run: int, root: Path, out: Path) -> tuple[str, int, int]:
    stem = out / f"{skill}.{ev['eval_name']}.{run}"
    response, grade = stem.with_name(stem.name + ".out.md"), stem.with_name(stem.name + ".grade.json")
    if not response.exists():
        response.write_text(claude(
            f"Read and follow the skill at {root}/craft-ops/skills/{skill}/SKILL.md (its references/ and "
            f"{root}/craft-ops/PRINCIPLES.md as it directs). Don't read anything under tools/ or any "
            f"*-workspace directory. Then respond to this request:\n\n{ev['prompt']}", out))
    if not grade.exists():
        raw = claude(
            "You are a strict grader. For each assertion, decide whether the RESPONSE clearly satisfies it. "
            'Reply with ONLY a JSON array of {"assertion": str, "passed": bool, "evidence": str}.\n\n'
            f"ASSERTIONS:\n{json.dumps(ev['assertions'], indent=1)}\n\nRESPONSE:\n{response.read_text()}", out)
        verdicts = json.loads(raw[raw.find("["): raw.rfind("]") + 1])
        grade.write_text(json.dumps(verdicts, indent=1) + "\n")
    verdicts = json.loads(grade.read_text())
    return ev["eval_name"], sum(v["passed"] for v in verdicts), len(verdicts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path, help="checkout whose craft-ops/ to evaluate")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--evals", nargs="*", help="only these eval_names")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    eval_set = json.loads(args.set.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [(ev, run) for ev in eval_set["evals"] if not args.evals or ev["eval_name"] in args.evals
            for run in range(1, args.runs + 1)]
    with ThreadPoolExecutor(args.workers) as pool:
        for name, passed, total in pool.map(
                lambda job: run_eval(eval_set["skill_name"], job[0], job[1], args.root.resolve(), args.out), jobs):
            print(f"{eval_set['skill_name']:26} {name:36} {passed}/{total}")


if __name__ == "__main__":
    main()
