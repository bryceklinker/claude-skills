#!/bin/sh
# SessionStart: in a repo that has opted into craft-code (a .craft-code.yml at
# its root), tell the model to route code changes through dev-workflow.
#
# Without this, the gate only engages when the model happens to load
# dev-workflow from its description, and on terse requests ("fix it", "just
# quickly…") in a fresh session it mostly doesn't: behavioral evals saw it
# fire in 1 of 9 runs without this line and 8 of 8 with it. Repos without a
# .craft-code.yml get nothing.
set -u

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
root="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$dir")"
[ -f "$root/.craft-code.yml" ] || exit 0

cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"This repository uses craft-code (it has a .craft-code.yml). Before changing any code here, whether a feature, a fix, a small tweak, or an adjustment to work in progress, invoke the craft-code:dev-workflow skill and follow it. It decides how much process the change needs, including the lighter follow-up lane for in-session changes."}}
EOF
