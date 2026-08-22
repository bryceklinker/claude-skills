#!/bin/bash
# Produce the repos the behavioral evals grade.
#
# This is the expensive, non-deterministic half: it drives the craft-code
# pipeline over each scenario's prompt in a throwaway git repo, with the plugin
# loaded from THIS checkout (--plugin-dir), so a run reflects the skills as they
# are right now rather than whatever is installed globally.
#
# Usage:
#   ./produce.sh <runs-dir> [scenario-id ...]           # default: every scenario
#   FORCE=1 ./produce.sh <runs-dir> [scenario-id ...]   # redo scenarios already done
#
# Resumable by default: a scenario that already has a completed run is skipped, so
# hitting a usage limit halfway through a batch costs only the unfinished ones --
# re-run the same command when the limit resets and it picks up where it stopped.
# Naming a scenario explicitly still skips it if it's done; use FORCE=1 to redo.
#
# Each run leaves <runs-dir>/<id>/repo (graded by run.sh) and
# <runs-dir>/<id>/transcript.jsonl (what the judgment/transcript assertions are
# read from). Seed repos, when a scenario needs one, live in inputs/<id>: either
# a plain tree, or a history/NN_name/ series applied as separate commits (each
# carrying a .commit-message) when the scenario's point is the git history.
#
# Runs unattended, so it passes the permission-bypass flag; keep <runs-dir>
# outside anything you care about.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/../.." && pwd)"
PY="${PY:-/opt/homebrew/bin/python3.14}"
RUNS_ARG="${1:?usage: ./produce.sh <runs-dir> [scenario-id ...]}"
shift
mkdir -p "$RUNS_ARG"
RUNS="$(cd "$RUNS_ARG" && pwd)"

ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
  ids=()
  for sc in "$HERE"/scenarios/*.json; do
    ids+=("$(basename "$sc" .json)")
  done
fi

seed_repo() {
  local id="$1" repo="$2" seed="$HERE/inputs/$1"
  git -C "$repo" init -q
  git -C "$repo" config user.email "evals@craft-code.local"
  git -C "$repo" config user.name "Behavioral Evals"
  git -C "$repo" config commit.gpgsign false

  if [ -d "$seed/history" ]; then
    for layer in "$seed"/history/*/; do
      rsync -a --exclude ".commit-message" "$layer" "$repo/"
      git -C "$repo" add -A
      git -C "$repo" commit -q -F "$layer/.commit-message"
    done
  elif [ -d "$seed" ]; then
    rsync -a "$seed/" "$repo/"
    git -C "$repo" add -A
    git -C "$repo" commit -q -m "chore: initial project state"
  else
    git -C "$repo" commit -q --allow-empty -m "chore: empty project"
  fi
  git -C "$repo" branch -M main
}

for id in "${ids[@]}"; do
  sc="$HERE/scenarios/$id.json"
  [ -f "$sc" ] || { echo "no scenario $id"; continue; }

  out="$RUNS/$id"
  repo="$out/repo"

  # Resume: a run that finished AND produced something stays put. Re-running the
  # batch after a usage limit then only spends quota on what never completed.
  # "Finished" is not enough on its own — a session can end cleanly having written
  # nothing, and that is a run to redo, not a result to keep.
  if [ "${FORCE:-0}" != "1" ] && [ -f "$out/timing.json" ] && [ -n "$($PY - "$out/timing.json" "$sc" <<'EOPY'
import json, sys
try:
    timing = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    print(""); raise SystemExit
if str(timing.get("status", "")) != "ok":
    print(""); raise SystemExit
scenario = json.load(open(sys.argv[2]))
# A transcript-graded scenario may legitimately end with no commits: for a gate,
# declining to write code is the result. Anything else needs commits to be real.
if scenario.get("config", {}).get("grading") == "transcript" or timing.get("commits_added", 0) > 0:
    print("keep")
EOPY
)" ]; then
    echo "=== $id: already produced — skipping (FORCE=1 to redo) ==="
    continue
  fi

  rm -rf "$out"
  mkdir -p "$repo"
  seed_repo "$id" "$repo"
  # Count every ref, not HEAD: the pipeline commits on a work-item branch in a
  # sibling worktree, so a finished run can leave main exactly where it started.
  before="$(git -C "$repo" rev-list --count --all)"

  prompt="$($PY -c "import json;print(json.load(open('$sc'))['prompt'])")"
  echo "=== $id: producing (this takes minutes) ==="
  start=$(date +%s)

  # cd into the throwaway repo: the session's working directory IS the project
  # under test. Without this the run happens wherever produce.sh was invoked
  # from -- which silently grades the wrong repo, or refuses for lack of one.
  # CLAUDECODE is unset so this can nest inside an interactive session; that
  # guard exists for terminal conflicts, and a subprocess run is not one.
  (
    cd "$repo" || exit 1
    env -u CLAUDECODE claude -p "$prompt" \
      --plugin-dir "$PLUGIN_ROOT" \
      --dangerously-skip-permissions \
      --output-format stream-json --verbose \
      > "$out/transcript.jsonl" 2> "$out/stderr.log"
  )
  rc=$?
  secs=$(( $(date +%s) - start ))
  after="$(git -C "$repo" rev-list --count --all)"

  # A run that produced no commits is not a result -- it is a refusal, a crash,
  # or a usage limit. Say so here rather than letting run.sh report it as a
  # discipline failure minutes later.
  status="$($PY - "$out/transcript.jsonl" <<'EOPY'
import json, sys
last = None
try:
    for line in open(sys.argv[1]):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            last = event
except OSError:
    pass
if last is None:
    print("no result event")
elif last.get("is_error"):
    print("ERROR: " + str(last.get("result", ""))[:120].replace("\n", " "))
else:
    print("ok")
EOPY
)"
  echo "{\"scenario\":\"$id\",\"seconds\":$secs,\"exit\":$rc,\"commits_added\":$(( after - before )),\"status\":\"$status\"}" > "$out/timing.json"
  echo "=== $id: done in ${secs}s (exit $rc, +$(( after - before )) commits) — $status ==="
  if [ "$after" -eq "$before" ]; then
    echo "    WARNING: no commits were made in $repo — this run produced nothing to grade"
  fi
done
