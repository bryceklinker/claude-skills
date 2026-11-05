#!/usr/bin/env python3
"""Measure whether a skill's description makes Claude load it.

For each query in an eval set, installs the skill's description as a project
command in a fresh, empty project and runs `claude -p` with the query. A run
counts as a trigger if the model invokes that command within --max-turns.

Usage:
  run.py --eval-set sets/<skill>.json --skill-path ../../skills/<skill> [--runs 3] [--workers 4]

Prints a JSON report to stdout: per-query trigger counts and pass/fail, plus a
summary. A query passes when its trigger rate is on the expected side of 0.5.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class Throttled(Exception):
    """The run ended on a usage limit or auth error, not on the model's choice."""


def read_frontmatter(skill_path: Path) -> tuple[str, str]:
    lines = (skill_path / "SKILL.md").read_text().split("\n")
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        value = value.strip()
        # Double-quoted YAML scalars here use JSON-compatible escapes (\").
        fields[key.strip()] = json.loads(value) if value.startswith('"') else value.strip("'")
    return fields["name"], fields["description"]


def run_once(query: str, name: str, description: str, max_turns: int, timeout: int) -> bool:
    # Each run gets its own empty project. Parallel runs sharing one
    # .claude/commands/ show the model several identical copies of the skill,
    # and picking another run's copy would be scored as a miss.
    command = f"{name}-under-test-{uuid.uuid4().hex[:8]}"
    project = Path(tempfile.mkdtemp(prefix="trigger-eval-"))
    try:
        commands = project / ".claude" / "commands"
        commands.mkdir(parents=True)
        indented = "\n  ".join(description.split("\n"))
        (commands / f"{command}.md").write_text(
            f"---\ndescription: |\n  {indented}\n---\n\n# {name}\n\nThis skill handles: {description}\n"
        )
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        proc = subprocess.Popen(
            ["claude", "-p", query, "--output-format", "stream-json", "--verbose",
             "--max-turns", str(max_turns)],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=project, env=env, text=True,
        )
        watchdog = threading.Timer(timeout, proc.kill)
        watchdog.start()
        try:
            for line in proc.stdout:
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("type") == "assistant":
                    for block in event["message"].get("content", []):
                        if block.get("type") == "tool_use" and command in json.dumps(block.get("input", {})):
                            return True
                elif event.get("type") == "result":
                    # Hitting --max-turns is the model's choice; anything else
                    # flagged as an error (usage limit, auth) is not a measurement.
                    if event.get("is_error") and event.get("subtype") != "error_max_turns":
                        raise Throttled(str(event.get("result", ""))[:100])
                    return False
            # A timeout kill is a miss, not a throttle.
            if proc.wait() != 0 and watchdog.is_alive():
                raise Throttled(f"exit {proc.returncode}")
            return False
        finally:
            watchdog.cancel()
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    finally:
        shutil.rmtree(project, ignore_errors=True)


def run_with_retry(query, name, description, max_turns, timeout, max_wait_hours) -> bool:
    waited, attempt = 0, 0
    while True:
        try:
            return run_once(query, name, description, max_turns, timeout)
        except Throttled as reason:
            if waited >= max_wait_hours * 3600:
                # Fail loudly rather than score an unmeasured query as a miss.
                raise RuntimeError(f"gave up after {waited}s throttled: {reason}") from None
            attempt += 1
            pause = min(60 * attempt, 900)
            print(f"  throttled ({reason}); retrying in {pause}s", file=sys.stderr)
            time.sleep(pause)
            waited += pause


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eval-set", required=True, type=Path)
    parser.add_argument("--skill-path", required=True, type=Path)
    parser.add_argument("--runs", type=int, default=3, help="runs per query")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=120, help="seconds per run")
    parser.add_argument("--max-wait-hours", type=float, default=72, help="total throttle wait per run")
    args = parser.parse_args()

    name, description = read_frontmatter(args.skill_path)
    queries = json.loads(args.eval_set.read_text())
    jobs = [(i, q) for i, q in enumerate(queries) for _ in range(args.runs)]
    with ThreadPoolExecutor(args.workers) as pool:
        fired = list(pool.map(
            lambda job: run_with_retry(job[1]["query"], name, description,
                                       args.max_turns, args.timeout, args.max_wait_hours),
            jobs))

    results = []
    for i, q in enumerate(queries):
        hits = [f for (j, _), f in zip(jobs, fired) if j == i]
        rate = sum(hits) / len(hits)
        results.append({
            "query": q["query"], "should_trigger": q["should_trigger"],
            "triggers": sum(hits), "runs": len(hits),
            "pass": (rate >= 0.5) == q["should_trigger"],
        })
    passed = sum(r["pass"] for r in results)
    json.dump({"skill": name, "description": description, "results": results,
               "summary": {"passed": passed, "total": len(results)}}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
