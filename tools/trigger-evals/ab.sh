#!/bin/bash
# A/B every skill's description: a baseline checkout vs this one.
#
# Usage: ./ab.sh <baseline-root> <out-dir> [skill ...]   (default: every set in sets/)
#
# Resumable: a skill/arm with a finished report in <out-dir> is skipped. Prints
# one line per skill: baseline passed -> current passed / total.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
BASE="$(cd "${1:?usage: ./ab.sh <baseline-root> <out-dir> [skill ...]}" && pwd)"
OUT="${2:?usage: ./ab.sh <baseline-root> <out-dir> [skill ...]}"
shift 2
PY="${PY:-/opt/homebrew/bin/python3.14}"
mkdir -p "$OUT"

skills=("$@")
if [ ${#skills[@]} -eq 0 ]; then
  for set in "$HERE"/sets/*.json; do skills+=("$(basename "$set" .json)"); done
fi

for skill in "${skills[@]}"; do
  for arm in baseline current; do
    report="$OUT/$skill.$arm.json"
    [ -s "$report" ] && continue
    root=$ROOT; [ $arm = baseline ] && root=$BASE
    if [ ! -f "$root/skills/$skill/SKILL.md" ]; then echo "$skill: no SKILL.md in $arm" >&2; continue; fi
    "$PY" "$HERE/run.py" --eval-set "$HERE/sets/$skill.json" --skill-path "$root/skills/$skill" \
      > "$report.tmp" 2> "$OUT/$skill.$arm.log" && mv "$report.tmp" "$report"
  done
  "$PY" - "$OUT/$skill.baseline.json" "$OUT/$skill.current.json" "$skill" <<'EOF'
import json, sys
try:
    b, c = (json.load(open(p))["summary"] for p in sys.argv[1:3])
    print(f"{sys.argv[3]:24} {b['passed']:>3} -> {c['passed']:>3} / {c['total']}")
except (OSError, ValueError, KeyError):
    print(f"{sys.argv[3]:24} incomplete")
EOF
done
