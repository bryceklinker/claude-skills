#!/bin/sh
# Tests for hooks/session-start.sh. Run from anywhere: tools/hook-tests/session-start-test.sh
set -u

HOOK="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)/hooks/session-start.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

passed=0
failed=0

check() { # check <description> <condition-exit-code>
  if [ "$2" -eq 0 ]; then passed=$((passed + 1)); else failed=$((failed + 1)); printf 'FAIL: %s\n' "$1"; fi
}

# A repo that opted in gets the routing line, as valid hook JSON.
mkdir -p "$TMP/opted-in/src" && git -C "$TMP/opted-in" init -q && touch "$TMP/opted-in/.craft-code.yml"
out="$(cd "$TMP/opted-in/src" && CLAUDE_PROJECT_DIR= "$HOOK")"
printf '%s' "$out" | grep -q 'craft-code:dev-workflow'; check "opted-in repo names dev-workflow" $?
printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["hookSpecificOutput"]["hookEventName"]=="SessionStart"' 2>/dev/null
check "opted-in output is SessionStart hook JSON" $?

# CLAUDE_PROJECT_DIR wins over the working directory.
out="$(cd "$TMP" && CLAUDE_PROJECT_DIR="$TMP/opted-in" "$HOOK")"
printf '%s' "$out" | grep -q 'dev-workflow'; check "CLAUDE_PROJECT_DIR is honored" $?

# A repo without .craft-code.yml gets nothing, and the hook still succeeds.
mkdir -p "$TMP/plain" && git -C "$TMP/plain" init -q
out="$(CLAUDE_PROJECT_DIR="$TMP/plain" "$HOOK")"; rc=$?
[ -z "$out" ]; check "repo without .craft-code.yml gets no output" $?
check "repo without .craft-code.yml exits 0" $rc

# Outside any git repo, the directory itself is checked.
mkdir -p "$TMP/nogit"
out="$(CLAUDE_PROJECT_DIR="$TMP/nogit" "$HOOK")"
[ -z "$out" ]; check "non-repo directory without the file gets no output" $?

printf '%d passed, %d failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
