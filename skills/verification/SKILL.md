---
name: verification
description: "Use to prove work actually behaves as required before you claim it — running the real change and reading the output, not reasoning about it. Applies whenever you're about to call something done, fixed, working, passing, or ready to merge/PR, and whenever a request asks you to *demonstrate, prove, confirm, or show* that something works: run the full test suite, start the app, drive a flow end to end, re-run a bug's original failing steps, or gather evidence that each acceptance criterion holds. The evidence — commands run and output observed this session — is the point; never assert success from inspection alone. Not for defining criteria, writing tests, decomposing work, or explaining concepts. Invoked by dev-workflow as phase 8."
---

# Verification

"It should work now" is a hypothesis. A claim of done rests on output you observed this session. If you didn't run it, you don't know.

## What to run

Use `commands.test`, `commands.acceptance`, and `commands.run` from `.craft-code.yml`.

1. **The full unit suite**, with clean output — no failures, no new warnings, no skips hiding problems.
2. **The acceptance suite**, where the feature has one — the strongest single evidence the whole works.
3. **Each acceptance criterion.** The passing test that covers it is evidence; where a test can't fully show the behavior (an end-to-end flow, a UI state, an integration), run the change for real and observe it.
4. **For a bug**, the original reproduction now behaves correctly.

Record each check as the command and the salient output. "Tests pass, looks good" isn't evidence.

## Report honestly

Say what failed, with its output. Say which checks you skipped and why. Name what can't be verified yet (missing credential, environment, data) rather than assuming it holds. Claim done only for what you verified.

## Harder cases

- **CI-only or deployed-only defects:** the evidence is a real run in that environment. A green local run or a careful reading of the workflow file is a hypothesis. Before pushing, confirm the diff you push is the one you reasoned about.
- **Intermittent failures:** one green is one sample. Run it enough times that the old failure rate would have shown, preferably as independent runs, and report the count ("20 consecutive passes; it previously failed about 1 in 4").
- **Abnormal duration:** a run far longer than its norm is a hang signal. Go look; a run cancelled because it was stuck is a result. The same goes for a delegate that reports "running" with no new output.
- **A check deferred twice** for the same environmental reason is no longer a caveat; the missing verification is the defect. Fix the environment or credential as its own work.

Any defect found goes back to `strict-tdd`: a failing test, then the fix, then verify again.

## Exit condition

Every criterion is backed by evidence observed this session, suites are green with clean output, and anything unverified is named. Hand off to `finish-work`.
