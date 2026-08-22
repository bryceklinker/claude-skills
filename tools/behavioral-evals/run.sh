#!/bin/bash
# Behavioral regression suite for the craft-code discipline.
#
# Grades produced repos against the discipline (test-first, no owned-code
# doubles, no non-null assertions, separate refactor commits, GWT names,
# green suite) and prints a pass/fail summary. The deterministic checks are
# the regression guard; judgment assertions are flagged for a reviewer.
#
# Usage:
#   ./run.sh <runs-dir>
#     where <runs-dir>/<scenario-id>/repo is a produced git repository for
#     each scenario you want graded. Writes grading.json next to each repo.
#
# Producing the runs (the expensive step) is separate and manual — drive the
# craft-code pipeline over each scenario's prompt in a headless session, e.g.:
#   claude -p "$(jq -r .prompt scenarios/feature-promo-code.json)" \
#     --dangerously-skip-permissions   # in a throwaway git repo, then copy it to <runs-dir>/feature-promo-code/repo
# then point this script at <runs-dir>.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-/opt/homebrew/bin/python3.14}"
RUNS="${1:?usage: ./run.sh <runs-dir>}"

# The pipeline does its work on a work-item branch inside a SIBLING worktree, and
# only merges back if the run reached finish-work. So the deliverable is often not
# <id>/repo -- grading that would report a disciplined run as a total failure.
# Pick whichever checkout under <id>/ carries the most commits.
resolve_target() {
  local dir="$1" best="" best_count=-1 candidate count
  for candidate in "$dir"/*/; do
    candidate="${candidate%/}"
    [ -e "$candidate/.git" ] || continue
    count="$(git -C "$candidate" rev-list --count HEAD 2>/dev/null || echo 0)"
    if [ "$count" -gt "$best_count" ]; then
      best_count="$count"; best="$candidate"
    fi
  done
  echo "$best"
}

pass=0; fail=0; review=0; missing=0
printf "%-26s %-8s %s\n" "SCENARIO" "RESULT" "detail"
printf -- "----------------------------------------------------------------\n"
for sc in "$HERE"/scenarios/*.json; do
  id="$($PY -c "import json,sys;print(json.load(open('$sc'))['id'])")"
  repo="$(resolve_target "$RUNS/$id")"
  if [ -z "$repo" ]; then
    printf "%-26s %-8s %s\n" "$id" "MISSING" "no checkout under $RUNS/$id"
    missing=$((missing+1)); continue
  fi
  # A run that errored (usage limit, crash) or built nothing must not be graded:
  # its repo is still the seed, and a seed sails through the deterministic checks,
  # reporting OK for a scenario that never ran. That false green is worse than a gap.
  target_commits="$(git -C "$repo" rev-list --count HEAD 2>/dev/null || echo 0)"
  notrun="$($PY - "$RUNS/$id/timing.json" "$sc" "$HERE/inputs/$id" "$target_commits" <<'EOPY'
import json, os, sys

timing_path, scenario_path, seed_dir, target_commits = sys.argv[1:5]
try:
    status = str(json.load(open(timing_path)).get("status", ""))
except (OSError, ValueError):
    status = ""
if status.startswith("ERROR") or status == "no result event":
    print(status[:60]); raise SystemExit

# How many commits the seed itself contributed -- anything at or below that means
# the run added nothing, so the repo under grade is the fixture, not a result.
history = os.path.join(seed_dir, "history")
if os.path.isdir(history):
    seed_commits = len([d for d in os.listdir(history) if os.path.isdir(os.path.join(history, d))])
else:
    seed_commits = 1

scenario = json.load(open(scenario_path))
# Transcript-graded scenarios are allowed to end with no commits -- for a gate
# scenario, declining to write code IS the result being measured.
if scenario.get("config", {}).get("grading") == "transcript":
    print(""); raise SystemExit
decidable = any(a.get("check", "judgment") != "judgment" for a in scenario["assertions"])
print("run added no commits to the seed" if decidable and int(target_commits) <= seed_commits else "")
EOPY
)"
  if [ -n "$notrun" ]; then
    printf "%-26s %-8s %s\n" "$id" "NOTRUN" "$notrun"
    missing=$((missing+1)); continue
  fi
  [ "$repo" = "$RUNS/$id/repo" ] || echo "    ($id graded from $(basename "$repo") — work landed on a branch, not main)"
  out="$RUNS/$id/grading.json"
  summary="$($PY "$HERE/grade.py" --repo "$repo" --scenario "$sc" --out "$out" \
            | $PY -c "import json,sys; d=json.load(sys.stdin)['summary']; print(f\"{d['passed']}/{d['passed']+d['failed']} decided, {d['needs_review']} review\", '' if d['failed']==0 else 'FAILED')")"
  if echo "$summary" | grep -q FAILED; then
    printf "%-26s %-8s %s\n" "$id" "FAIL" "$summary"; fail=$((fail+1))
  else
    printf "%-26s %-8s %s\n" "$id" "OK" "$summary"; pass=$((pass+1))
  fi
done
printf -- "----------------------------------------------------------------\n"
echo "scenarios: $pass ok, $fail failed, $missing missing (deterministic checks; judgment items flagged for review)"
[ "$fail" -eq 0 ] && [ "$missing" -eq 0 ]
