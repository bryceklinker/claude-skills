# Testing and Verifying Pipelines — the TDD/verification split, made concrete

A pipeline definition is two different kinds of thing wearing one file extension: logic (decisions, computations, parsing, policy) that happens to live in a script the pipeline calls, and glue (which stage runs after which, gated by what) that just wires those scripts together. Those two kinds of thing are proven correct by two different methods, and conflating them is how pipelines end up either untested (because "you can't unit test YAML") or over-mocked (because someone tried to unit test the wiring and had to fake half the CI system to do it). This document makes the split from the skill's `SKILL.md` concrete: what actually goes through `strict-tdd`, what actually goes through `verification`, and how to keep the second category as small as possible.

## Table of contents
- What counts as logic: unit-test it under strict-tdd
- What counts as glue: verify it, don't unit-test it
- Running a verification pass against a throwaway artifact
- Smoke-invoke each script through the entrypoint the glue calls
- Shrinking the untestable surface

## What counts as logic: unit-test it under strict-tdd

**Anything extracted into a script per `pipeline-as-code-hygiene.md` — step scripts, artifact-metadata generators, policy checks, anything that branches, computes, or decides — is production code, and it goes through `strict-tdd` exactly like application code: a failing test first, then the minimal code to pass it.**

This follows directly from extraction: the entire reason non-trivial step bodies get pulled out of the pipeline definition and into files on disk is so that they *can* be given independent test coverage. A script that parses a build tool's output to decide pass/fail, a generator that computes a version string, a policy check that rejects a deploy past a certain hour — each of these has real branching logic with real edge cases (malformed input, boundary values, empty results), and each of those edge cases is something a unit test can pin down far faster and more precisely than running the whole pipeline and reading whether it happened to behave right. Treat these exactly like any other unit under test: write the test that captures the edge case, watch it fail, then implement.

## What counts as glue: verify it, don't unit-test it

**The declarative wiring itself — which stage runs after which, what triggers a stage, what a step is configured to call — is not unit-testable in any meaningful sense, and trying to force it into that mold produces tests that mock the CI system rather than exercise it.** This half is proven by `verification`: run the real pipeline and observe what it actually does.

The reason a unit test is the wrong tool here: the wiring has no interesting internal logic to isolate — its entire behavior *is* its integration with the CI platform, the artifact registry, the deploy target. A test that mocks all of those to make the wiring "testable" doesn't verify the wiring at all; it verifies that the wiring calls the mocks the way the test author expected, which is a tautology that would pass even if the real pipeline were subtly broken. What actually needs answering — "does this stage trigger when I think it does," "does the promotion step really point the next environment at the right digest," "does a failure in stage two actually halt stage three" — can only be answered by watching the real thing run.

## Running a verification pass against a throwaway artifact

**Verify the glue by running the actual pipeline definition against a throwaway or test artifact — a scratch branch, a disposable tag, a non-production target — and observing the real outcome: which stages ran, in what order, whether the gate that was supposed to block actually blocked, whether the artifact that came out the other end is the one that went in.** This is evidence, not inspection — reading the YAML and reasoning that it "looks right" is exactly the failure mode verification exists to rule out, the same way reading application code without running its tests would be.

Concretely, that means: trigger the pipeline for real, on infrastructure close enough to production's that the outcome is trustworthy, against an artifact and environment that can be safely discarded or reset afterward. Capture what actually happened — the run's logs, which stages executed, what got promoted where — as the record that verification occurred, not a description of what should have happened. If a gate is supposed to stop a promotion on a failing check, prove it by making the check fail and watching the promotion actually get blocked; a gate that's never been observed rejecting anything is a gate whose enforcement is still just an assumption.

## Smoke-invoke each script through the entrypoint the glue calls

**A script's unit tests import its functions directly; the pipeline invokes it through an entrypoint — `python -m ci.promote`, `./ci/deploy.sh`, a console command. Those are two different call paths, and the unit tests exercise only the first. A wrong module name, a broken argument parser, a renamed file, a missing `__main__` — none of it shows up in a green unit suite, and all of it fails on the first real run.** So the cheapest, most reliable slice of glue verification is to invoke each extracted script exactly the way the pipeline does — `python -m ci.promote --help`, `./ci/deploy.sh --dry-run`, `mytool generate --check` — and confirm the entrypoint resolves and its CLI wiring holds.

This is the one piece of verification you can almost always run even when the full pipeline can't — no CI runner, no registry, no cluster required, just the entrypoint and its argument handling. Do it for every script the glue calls. The point is not to re-test the logic — the unit tests own that — but to prove the *seam* between the wiring and the already-tested code is actually connected. A pipeline whose scripts are all green but whose definition calls `python -m ci.promote` when the module is `ci.promotion` is a pipeline that fails on its first deploy with `ModuleNotFoundError`; a single `python -m ci.promote --help` in the verification pass is what catches it. Whenever a real runner isn't available to verify the full glue, this entrypoint smoke-invocation is the minimum verification that still must happen — it covers exactly the class of break that unit-testing the logic can never see.

## Shrinking the untestable surface

**The size of the glue that only verification can cover is not fixed — it's a direct consequence of how aggressively logic gets extracted per `pipeline-as-code-hygiene.md`. The more a step's actual decision-making lives in a tested script, the less of the pipeline definition is doing anything beyond "call this script, then that one."** Minimizing the untestable surface isn't a separate goal from hygiene — it's the same goal, viewed from the testing side.

A pipeline where every step is three lines of inline shell has almost nothing that strict-tdd can reach — nearly the entire thing has to be proven by running it end to end, every time, for every change, no matter how small. A pipeline where every non-trivial step is a call to an extracted, tested script inverts that ratio: most of the actual behavior is covered fast, locally, and precisely by unit tests, and verification is left with a genuinely small job — confirming the wiring between already-trusted pieces is correct — instead of standing in for all the testing the pipeline never got.
