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

A few assertions are `judgment` (`passed: null`) — things a regex shouldn't decide: immutability nuance, results-vs-exceptions intent, and the **gate-refusal** behavior, which lives in the run *transcript*, not the repo. Those are flagged for a human or model reviewer rather than faked as mechanical. Being honest about that boundary is the point.

## Running it

Producing the repos is the expensive, non-deterministic step and is kept manual: drive the craft pipeline over each scenario's `prompt` in a throwaway git repo (a headless `claude -p …` session, or by hand), then place the result at `<runs-dir>/<scenario-id>/repo`. Then grade:

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
