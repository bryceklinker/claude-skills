#!/bin/sh
# Tests for .githooks/commit-msg. Run from anywhere: tools/hook-tests/commit-msg-test.sh
set -u

HOOK="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)/.githooks/commit-msg"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

passed=0
failed=0

# expect_accept <description> <subject>
expect_accept() {
  printf '%s\n' "$2" > "$TMP/msg"
  if "$HOOK" "$TMP/msg" >/dev/null 2>&1; then
    passed=$((passed + 1))
  else
    failed=$((failed + 1))
    printf 'FAIL (expected accept): %s -- %s\n' "$1" "$2"
  fi
}

# expect_reject <description> <subject>
expect_reject() {
  printf '%s\n' "$2" > "$TMP/msg"
  if "$HOOK" "$TMP/msg" >/dev/null 2>&1; then
    failed=$((failed + 1))
    printf 'FAIL (expected reject): %s -- %s\n' "$1" "$2"
  else
    passed=$((passed + 1))
  fi
}

# expect_accept_raw <description> <full message body>
# For messages whose shape matters beyond the subject line (leading blank lines,
# leading comment blocks) -- git strips both before storing the message.
expect_accept_raw() {
  printf '%s\n' "$2" > "$TMP/msg"
  if "$HOOK" "$TMP/msg" >/dev/null 2>&1; then
    passed=$((passed + 1))
  else
    failed=$((failed + 1))
    printf 'FAIL (expected accept): %s\n' "$1"
  fi
}

# Every allowed type, unscoped.
for t in feat fix docs refactor perf test chore build ci revert; do
  expect_accept "type $t" "$t: do a thing"
done

expect_accept "scoped"                "feat(craft-ops): add a skill"
expect_accept "scope with dashes"     "fix(craft-code): correct the thing"
expect_accept "breaking marker"       "feat!: drop the old flag"
expect_accept "scoped breaking"       "refactor(craft-code)!: rename the namespace"
expect_accept "merge commit"          "Merge pull request #3 from bryceklinker/feat/x"
expect_accept "merge branch"          "Merge branch 'main' into feat/x"
expect_accept "git revert subject"    'Revert "feat: add a thing"'
expect_accept "fixup"                 "fixup! feat: add a thing"
expect_accept "squash"                "squash! feat: add a thing"

expect_reject "no type"               "add a thing"
expect_reject "unknown type"          "feet: add a thing"
expect_reject "missing colon"         "feat add a thing"
expect_reject "missing space"         "feat:add a thing"
expect_reject "empty description"     "feat: "
expect_reject "empty scope"           "feat(): add a thing"
expect_reject "unclosed scope"        "feat(craft-code: add a thing"
expect_reject "leading whitespace"    "  feat: add a thing"

# git strips trailing whitespace, so these would be stored as a bare "feat:",
# which git cliff cannot parse and drops from the release notes.
expect_reject "spaces-only description" "feat:   "
expect_reject "tab-only description"    "$(printf 'feat: \t')"

# A comment-only or empty message file must not be accepted as a subject.
expect_reject "empty message"         ""

# The real git-editor flow: git strips a leading blank line and the comment
# block it appends, so a subject behind either must still be validated.
expect_accept_raw "leading blank line" "$(printf '\nfeat: do a thing')"
expect_accept_raw "leading comments"   "$(printf '# Please enter the commit message for your changes.\n# Lines starting with %s will be ignored.\nfeat: do a thing' "'#'")"

printf '\n%d passed, %d failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
