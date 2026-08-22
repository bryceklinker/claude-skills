---
name: verification
description: "Use to prove work actually behaves as required before you claim it \u2014 running the real change and reading the output, not reasoning about it. Applies whenever you're about to call something done, fixed, working, passing, or ready to merge/PR, and whenever a request asks you to *demonstrate, prove, confirm, or show* that something works: run the full test suite, start the app, drive a flow end to end, re-run a bug's original failing steps, or gather evidence that each acceptance criterion holds. The evidence \u2014 commands run and output observed this session \u2014 is the point; never assert success from inspection alone. Not for defining criteria, writing tests, decomposing work, or explaining concepts. Invoked by dev-workflow as phase 7."
---

# Verification — evidence before any claim of done

## Why this exists

"It should work now" is not verification — it's a hypothesis. The gap between code that looks correct and code that *is* correct is exactly where shipped bugs live. This phase closes that gap by requiring that every claim of completion rests on observed evidence: commands actually run, output actually read, acceptance criteria actually exercised.

The discipline is simple and absolute: **assertions of success must be backed by output you have seen in this session.** If you didn't run it, you don't know.

## What to verify

Verify against the **acceptance criteria** from `intake`, not against a vague sense that things look fine. For each criterion, produce evidence that the behavior it describes actually happens. Use the project's configured commands — `commands.test`, `commands.acceptance`, `commands.run` from `.craft-code.yml` (see `craft-code-conventions`) — rather than guessing how this repo runs its suite or app.

1. **The full test suite passes, with pristine output.** Run it — all of it, not just the new tests. Read the output: green, no new warnings, no skipped tests quietly hiding failures. A suite you didn't just run is a suite you're guessing about.

2. **Each acceptance criterion is exercised.** For a criterion, the passing test that covers it *is* the evidence — point to it. Where a criterion involves behavior a unit test can't fully show (an end-to-end flow, a UI state, an integration), run the change for real and observe the result.

3. **For a bug:** the reproduction from `intake` — the steps that used to fail — now produces the correct behavior. Run the original failing scenario and confirm it's fixed, and confirm the regression test that captures it is green.

4. **The change runs in something close to the real environment**, not only in unit tests, when the criteria imply integration — start the app, hit the endpoint, drive the flow. If there's a project skill or command for running the app, use it.

5. **The acceptance suite passes**, where the feature has one (`acceptance-testing`). Run the outer, user-level tests against the production-like deployment and read their output — this is the strongest single piece of evidence that the feature works end to end. `acceptance-testing` authors and owns those tests up front; verification executes them here as proof of done.

## Capturing evidence

For each criterion or check, record what you ran and what you observed — the command and the salient output. This is what lets you (and the user, and a reviewer) trust the "done" claim instead of taking it on faith. Vague summaries ("tests pass, looks good") defeat the purpose; the specific observed output is the point.

## Honesty rules

- **If a test fails, say so** — report it with the actual output, don't round it up to "mostly passing."
- **If you skipped a check, say which** and why — don't imply coverage you didn't produce.
- **If a criterion can't be verified yet** (needs data, an environment, a credential you lack), name it as unverified rather than assuming it holds.
- **Only claim done for what you verified.** "The three unit-tested criteria pass; the end-to-end flow is unverified pending a staging login" is an honest, useful status. "Done" when you ran nothing is not.

## Environment-only defects: the evidence must come from that environment

Some failures exist only where you can't watch them — a CI runner, a container network, a deployed environment. A green local run is not evidence about them. Neither is a passing unit test that "covers the same logic," nor a careful reading of the workflow file.

<HARD-GATE>
For a defect that only manifests in CI or a deployed environment, the evidence is a **real run in that environment**, observed. Reasoning about why the fix should work there is a hypothesis, not verification — and shipping it as verified is how a fix gets four rounds instead of one.
</HARD-GATE>

Two things follow. First, if the loop is fix → push → wait, the cost per round is real, so spend the extra minutes *before* pushing: confirm the diff you are pushing is the diff you reasoned about, and confirm you read the code that actually ran (a stale checkout will happily explain a failure that no longer exists). Second, when a round fails, read the new evidence rather than reaching for the next idea — see `systematic-debugging`.

## Intermittent failures need repetition, not a single green

A flaky test that passes once has not been verified; you have observed one sample of a distribution. A single green after a race-condition fix is the weakest evidence in this whole file, because the failing case was always the minority outcome.

- **Run it repeatedly** — enough times that the previous failure rate would have shown up, and say how many. "Passed 20 consecutive runs, previously failed roughly 1 in 4" is evidence; "it passed" is not.
- **Prefer independent runs** over one loop in one process, when the flake involves environment, ordering, or startup timing.
- **Say what the fix removed.** If you can name the mechanism that made it non-deterministic and show it's gone, repetition confirms; if you can't, repetition is all you have and the confidence should be stated as lower.

## Abnormal duration is a signal, not "still pending"

A run taking far longer than its norm is telling you something — a hang, a deadlock, a wait on something that will never arrive. Treat it as an observation to act on: compare against a known-good duration for that job, and when it's well past, go look rather than continuing to wait. A job you cancelled after 15 minutes because it was stuck is a *result* — it is often the most informative one you'll get, and it belongs in the evidence.

The same applies to delegated work: a subagent or background job that reports "running" is claiming liveness, not proving it. Check for actual progress — new output, a moved artifact, a commit — before treating a long-running delegate as healthy.

## A check deferred twice is a defect

Naming an unverified item is honest the first time. The second time the *same* check is skipped for the *same* environmental reason — a missing token, an environment that won't come up, a suite that "doesn't run here" — the honest report has become a standing gap, and the gap is the defect.

At that point the missing verification is the work item: fix the environment, wire in the credential, make the suite runnable. Carrying it forward as a recurring caveat means the thing it would have caught is, in practice, untested — and it will stay that way until something breaks in production.

## When verification finds a defect

Back to `strict-tdd`: write a failing test reproducing the defect, then fix it, then re-verify. A defect found here is the pipeline working — it's cheaper here than after merge.

## Exit condition

Every acceptance criterion is backed by evidence you observed this session, the full suite is green with clean output, environment-only fixes are proven by a real run in that environment, intermittent failures are backed by repetition rather than a single green, and any unverified items are named explicitly — with anything now deferred a second time raised as a defect rather than a caveat. Hand off to `finish-work`.

