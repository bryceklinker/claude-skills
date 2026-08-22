# Behavioral Evals — a regression guard for the discipline

The trigger-optimizer proves each skill *fires* on the right requests. These
behavioral evals prove an agent following the skills actually *behaves* — that a
run built test-first, didn't mock owned code, didn't reach for a non-null
assertion, committed the refactor separately, and named its tests
Given/When/Then. They exist so that when you edit a skill, you can confirm you
didn't quietly loosen the discipline it encodes.

## What's here

```
scenarios/          one JSON per scenario: prompt + assertions
  feature-promo-code.json   a feature (test-first, results-over-exceptions, immutability, no owned mocks)
  bug-empty-email.json      a bug   (reproduce-first, regression test, minimal fix)
  refactor-orderservice.json a refactor (behavior preserved, decomposed, style improved)
  gate-refusal.json         the gate ("just quickly…" must NOT skip intake+plan)
  followup-lane.json        the follow-up lane (in-session follow-up takes the lighter lane, still test-first + reviewed)
  feedback-adjustment.json  feedback is a change request ("adjust X" goes RED-first, not straight to a production edit)
  repeat-defect.json        the third patch to the same lines (escalate the level; recommend the durable option)
  flaky-ci-test.json        a CI-only flake (no symptom patch, fix the missing diagnostics, repeat the run)
  discarded-async-work.json background work (every detached call site gets a named failure owner)
inputs/<id>/        starting state for scenarios that need one (a tree, or a history/ series of commits)
produce.sh          drive the pipeline over each scenario in a throwaway repo → <runs-dir>/<id>/
grade.py            deterministic grader → grading.json (same shape the benchmark aggregator reads)
run.sh              grade every scenario's produced repo, print a pass/fail table
```

## Deterministic vs. judgment

Each assertion carries a `check`. Most are **deterministic** — decided mechanically from the produced repo and its git history, so they're cheap and repeatable:

| check | what it verifies |
|-------|------------------|
| `suite_passes` | the configured test command exits 0 |
| `test_before_code` | a test file is committed at or before the production code it covers |
| `multiple_small_commits` | red-green-refactor rhythm, not one big-bang commit |
| `separate_refactor_commits` | no commit bundles "add behavior" with "refactor" |
| `no_owned_mocks` | no `jest.fn`/`vi.fn`/`Mock<>`/`Moq`/`unittest.mock`… in tests |
| `no_non_null_assertion` | no `x!` / null-forgiving operator in production code |
| `gwt_test_names` | ≥60% of test titles follow Given/When/Then |
| `detached_work_owned` | every detached call site (`async void`, `_ = call()`, `void call()`, bare `go`/`create_task`) has a try/catch in scope — heuristic, ±15 lines |

A few assertions are `judgment` (`passed: null`) — things a regex shouldn't decide: immutability nuance, results-vs-exceptions intent, and the **gate-refusal** behavior, which lives in the run *transcript*, not the repo. Those are flagged for a human or model reviewer rather than faked as mechanical. Being honest about that boundary is the point.

## Running it

Producing the repos is the expensive, non-deterministic step. `produce.sh` does it: for each scenario it builds a throwaway git repo from `inputs/<id>` (if the scenario needs a starting state), then drives the pipeline over the scenario's `prompt` in a headless session with the plugin loaded **from this checkout** — `--plugin-dir`, so a run reflects the skills as they are right now, not whatever is installed globally.

```bash
./produce.sh <runs-dir>                        # every scenario
./produce.sh <runs-dir> repeat-defect …        # named scenarios only
FORCE=1 ./produce.sh <runs-dir> repeat-defect  # redo one that already succeeded
```

**It resumes.** A scenario that already finished *and produced something* is skipped, so hitting a usage limit halfway through a batch costs only the unfinished scenarios — re-run the same command when the limit resets and it continues. "Finished" alone isn't enough: a session can end cleanly having written nothing, and that gets redone. Transcript-graded scenarios are exempt from the commits test, since declining to write code is the result being measured there.

It leaves `<runs-dir>/<id>/repo` for the grader and `<runs-dir>/<id>/transcript.jsonl` for the transcript-graded assertions. Runs unattended, so it passes `--dangerously-skip-permissions` — keep `<runs-dir>` outside anything you care about. Budget minutes and tens of thousands of tokens per scenario.

Seeds live in `inputs/<id>/`, in one of two shapes: a plain tree copied in as one initial commit, or a `history/NN_name/` series applied as separate commits (each with a `.commit-message`) when the scenario's point *is* the git history — `repeat-defect` needs its two prior rounding fixes to be real commits, or there's no recurrence for the run to notice.

`run.sh` reports **NOTRUN** rather than a result when a run errored (a usage limit mid-batch is the common one) or added no commits above its seed. That distinction matters: a seed repo sails through the deterministic checks, so grading a scenario that never ran reports a confident OK for nothing at all.

**Known gap:** `gate-refusal`, `followup-lane`, and `feedback-adjustment` have no seed. Their prompts describe a session already in flight against code that doesn't exist here (`ApsSender`, a health check, a checkout to tweak), so a run correctly refuses on the premise instead of exercising the gate. They need seeds matching their premises before their judgment items mean anything.

Two failure modes to watch for, both observed the first time this ran:
 a session that runs in the **wrong working directory** silently grades the wrong repo (the run happens where you invoked it, not in the throwaway — `produce.sh` now `cd`s and warns when a run adds no commits), and a run with the scenarios in view can **read its own grading assertions**, which voids it. Keep `<runs-dir>` outside this checkout so the scenario files aren't in the session's reach.

Then grade:

```bash
PY=/opt/homebrew/bin/python3.14 ./run.sh <runs-dir>
```

`run.sh` grades each scenario, writes `grading.json` beside each repo, and prints a table; it exits non-zero if any deterministic check failed or a repo is missing — so it drops straight into CI as a discipline gate.

Grade a single repo directly:

```bash
/opt/homebrew/bin/python3.14 grade.py \
  --repo <path-to-produced-repo> \
  --scenario scenarios/feature-promo-code.json \
  --test-cmd "node --test"
```

## Validated against the existing benchmark

The grader was checked against the `iteration-2` produced repos:
- The **with-skill** promo-code repo scores **7/7** deterministic checks (2 judgment items flagged).
- The **without-skill** baseline is correctly caught **failing** on `multiple_small_commits` (one big-bang commit) and `gwt_test_names` (0/13 titles) — proving the grader discriminates discipline from its absence, which is the whole job.

## Adding a scenario

1. Write `scenarios/<id>.json` with a `prompt` and `assertions` (each an object with `text` and a `check` from the table above, or `"check": "judgment"` with a `note`).
2. Optionally set `config.test_cmd` for the suite command.
3. Produce a repo for it and run `./run.sh`.

Keep scenarios small and focused on a discipline that could regress — the value is a fast, honest signal, not exhaustive coverage.
