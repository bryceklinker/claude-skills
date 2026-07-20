---
name: verification
description: "Use to prove work actually behaves as required before you claim it \u2014 running the real change and reading the output, not reasoning about it. Applies whenever you're about to call something done, fixed, working, passing, or ready to merge/PR, and whenever a request asks you to *demonstrate, prove, confirm, or show* that something works: run the full test suite, start the app, drive a flow end to end, re-run a bug's original failing steps, or gather evidence that each acceptance criterion holds. The evidence \u2014 commands run and output observed this session \u2014 is the point; never assert success from inspection alone. Not for defining criteria, writing tests, decomposing work, or explaining concepts. Invoked by dev-workflow as phase 7."
---

# Verification — evidence before any claim of done

## Why this exists

"It should work now" is not verification — it's a hypothesis. The gap between code that looks correct and code that *is* correct is exactly where shipped bugs live. This phase closes that gap by requiring that every claim of completion rests on observed evidence: commands actually run, output actually read, acceptance criteria actually exercised.

The discipline is simple and absolute: **assertions of success must be backed by output you have seen in this session.** If you didn't run it, you don't know.

## What to verify

Verify against the **acceptance criteria** from `intake`, not against a vague sense that things look fine. For each criterion, produce evidence that the behavior it describes actually happens.

1. **The full test suite passes, with pristine output.** Run it — all of it, not just the new tests. Read the output: green, no new warnings, no skipped tests quietly hiding failures. A suite you didn't just run is a suite you're guessing about.

2. **Each acceptance criterion is exercised.** For a criterion, the passing test that covers it *is* the evidence — point to it. Where a criterion involves behavior a unit test can't fully show (an end-to-end flow, a UI state, an integration), run the change for real and observe the result.

3. **For a bug:** the reproduction from `intake` — the steps that used to fail — now produces the correct behavior. Run the original failing scenario and confirm it's fixed, and confirm the regression test that captures it is green.

4. **The change runs in something close to the real environment**, not only in unit tests, when the criteria imply integration — start the app, hit the endpoint, drive the flow. If there's a project skill or command for running the app, use it.

## Capturing evidence

For each criterion or check, record what you ran and what you observed — the command and the salient output. This is what lets you (and the user, and a reviewer) trust the "done" claim instead of taking it on faith. Vague summaries ("tests pass, looks good") defeat the purpose; the specific observed output is the point.

## Honesty rules

- **If a test fails, say so** — report it with the actual output, don't round it up to "mostly passing."
- **If you skipped a check, say which** and why — don't imply coverage you didn't produce.
- **If a criterion can't be verified yet** (needs data, an environment, a credential you lack), name it as unverified rather than assuming it holds.
- **Only claim done for what you verified.** "The three unit-tested criteria pass; the end-to-end flow is unverified pending a staging login" is an honest, useful status. "Done" when you ran nothing is not.

## When verification finds a defect

Back to `strict-tdd`: write a failing test reproducing the defect, then fix it, then re-verify. A defect found here is the pipeline working — it's cheaper here than after merge.

## Exit condition

Every acceptance criterion is backed by evidence you observed this session, the full suite is green with clean output, and any unverified items are named explicitly. Hand off to `finish-work`.
