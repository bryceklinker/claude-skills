#!/bin/bash
# Behavioral regression suite for the craft discipline.
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
# craft pipeline over each scenario's prompt in a headless session, e.g.:
#   claude -p "$(jq -r .prompt scenarios/feature-promo-code.json)" \
#     --dangerously-skip-permissions   # in a throwaway git repo, then copy it to <runs-dir>/feature-promo-code/repo
# then point this script at <runs-dir>.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-/opt/homebrew/bin/python3.14}"
RUNS="${1:?usage: ./run.sh <runs-dir>}"

pass=0; fail=0; review=0; missing=0
printf "%-26s %-8s %s\n" "SCENARIO" "RESULT" "detail"
printf -- "----------------------------------------------------------------\n"
for sc in "$HERE"/scenarios/*.json; do
  id="$($PY -c "import json,sys;print(json.load(open('$sc'))['id'])")"
  repo="$RUNS/$id/repo"
  if [ ! -d "$repo/.git" ]; then
    printf "%-26s %-8s %s\n" "$id" "MISSING" "no repo at $repo"
    missing=$((missing+1)); continue
  fi
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
