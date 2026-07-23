---
name: systematic-debugging
description: "Use to find the root cause of a defect by disciplined investigation rather than guessing — reproduce it, narrow the search space, form one falsifiable hypothesis at a time, and confirm the cause before changing anything. Trigger whenever something is broken, failing, flaky, throwing, or producing wrong output and you don't yet KNOW why: a failing test you can't explain, a bug report, a regression, a crash, a race condition, an 'it works locally but not in CI', or any 'why is this happening?'. This is the front half of the pipeline's defect loop — it finds the cause; strict-tdd then captures it as a failing test and fixes it. Not for building new features, and not once the cause is already known and it's time to write the fix."
---

# Systematic Debugging — find the cause before you change anything

## Why this exists

Most time lost to bugs is lost to *guessing* — changing a line that looks suspicious, re-running, changing another, until something shifts and the real cause is never understood. That "fix" often just moves the symptom or masks it until it resurfaces in production. Systematic debugging replaces the guessing with a method: reproduce, narrow, hypothesize, confirm. It is slower for the first thirty seconds and far faster by the end, because every step *removes* possibilities instead of shuffling them.

The discipline's core belief: **a bug is an information problem, not a typing problem.** You don't need to change code to make progress — you need to learn where reality diverges from your model. Once you know the cause exactly, the fix is usually small and obvious.

## The iron rule: reproduce first

<HARD-GATE>
Do not form theories about a bug you cannot reproduce. A bug you can't reproduce is a bug you can't confirm you fixed. Establish a reliable reproduction — ideally an automated failing test, at minimum a deterministic manual sequence with observed output — before investigating cause.
</HARD-GATE>

If the bug entered through the pipeline, `intake` already produced this reproduction. If it arrived some other way (a report, a crash), reproducing it *is* your first job. Reduce it to the **smallest input and shortest path** that still shows the failure — a minimal reproduction eliminates most of the search space for free.

## The loop: one falsifiable hypothesis at a time

1. **Observe, don't infer.** Read the *actual* error message and full stack trace. Read the actual output versus expected. Do not skim it and pattern-match to a cause you've seen before — this bug is not that bug until the evidence says so.
2. **Narrow the search space.** Cut the problem in half, repeatedly, until the fault is localized:
   - **Bisect the history** — if it used to work, `git bisect` to the exact commit that introduced it. This alone often names the cause.
   - **Bisect the code path** — add an observation point halfway between "state is correct" and "state is wrong"; the fault is on one side. Move the point; repeat.
   - **Bisect the input** — remove half the data/config; does it still fail? Keep halving.
3. **Form one hypothesis — and make it falsifiable.** State it as a prediction: *"If the cause is X, then observing Y will show Z."* A hypothesis you can't disprove is a belief, not a lead.
4. **Test that one hypothesis.** Change one thing, or better, *observe* one thing (a log, a breakpoint, an assertion) without changing behavior. Run it. Did the prediction hold?
5. **Keep or discard, and revert the probe.** Confirmed → you've localized further; narrow again. Disproved → discard it and revert any change you made to test it. **Never leave failed-experiment code in place** — accumulated debugging cruft becomes its own source of bugs.

Repeat until you can state the cause as a specific, confirmed fact: *"the timestamp is compared as a string, so `'100' < '99'`,"* not *"something with the sorting."*

## Then — and only then — fix it through the pipeline

Finding the cause is where this skill ends. The fix re-enters the discipline:

1. **Write a failing test that captures the bug** at the right level — a unit test via `strict-tdd` for a logic fault, or an acceptance test via `acceptance-testing` if it only reproduces end to end. Watch it fail for the reason you diagnosed.
2. **Fix it** — the minimum change that makes that test pass.
3. **Verify** the original reproduction now behaves correctly, and the regression test guards it forever.

You never patch a defect without a test that would have caught it. That is what keeps the pipeline a ratchet: every bug found makes the suite permanently stronger. Techniques for bisection, instrumentation, and the nastier classes of bug live in `references/techniques.md`.

## Rationalizations to reject

| Thought | Reality |
|---------|---------|
| "I'm pretty sure it's the null check — just fix that" | A guess is a hypothesis you skipped testing. Confirm it, or you'll fix the wrong thing and still ship the bug. |
| "Let me change a few things and see what helps" | Change one thing at a time. Multiple simultaneous changes make the result uninterpretable. |
| "It's too flaky to reproduce reliably" | Flakiness is a clue (timing, ordering, shared state), not a wall. Narrow *what* varies between pass and fail. |
| "I don't have time to bisect" | Bisection is logarithmic; guessing is not. Bisecting is the fast path, not the slow one. |
| "I'll clean up the debug logging later" | Revert probes as you go. Later never comes and the cruft causes the next bug. |
| "The stack trace is noise" | The stack trace is the map. Read it fully before theorizing. |

## Exit condition

You can state the root cause as a specific, evidence-backed fact, and you have a reliable reproduction. Hand off to `strict-tdd` (or `acceptance-testing`) to capture it as a failing test and fix it.
