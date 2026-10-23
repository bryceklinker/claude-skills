---
name: systematic-debugging
description: "Use to find the root cause of a defect by disciplined investigation rather than guessing — reproduce it, narrow the search space, form one falsifiable hypothesis at a time, and confirm the cause before changing anything. Trigger whenever something is broken, failing, flaky, throwing, or producing wrong output and you don't yet KNOW why: a failing test you can't explain, a bug report, a regression, a crash, a race condition, an 'it works locally but not in CI', or any 'why is this happening?'. This is the front half of the pipeline's defect loop — it finds the cause; strict-tdd then captures it as a failing test and fixes it. Not for building new features, and not once the cause is already known and it's time to write the fix."
---

# Systematic Debugging

A bug is an information problem, not a typing problem: you make progress by learning where reality diverges from your model, not by changing lines until something shifts. Once the cause is known exactly, the fix is usually small.

## Reproduce first

Don't theorize about a failure you can't reproduce. Get a reliable reproduction — ideally a failing automated test — and reduce it to the smallest input and shortest path that still fails. If `intake` already produced one, start from it.

## Then narrow, one hypothesis at a time

1. **Observe.** Read the whole error, stack trace, and actual-versus-expected output. This bug isn't the one you saw last month until the evidence says so.
2. **Bisect.** `git bisect` a regression to its commit; put an observation point halfway along the code path; halve the input or config. Repeat until the fault is localized.
3. **Hypothesize falsifiably.** "If the cause is X, then observing Y will show Z."
4. **Test one thing** — preferably by observing (a log, a breakpoint) rather than changing behavior.
5. **Keep or discard it, and revert the probe.** Never leave experiment code behind.

Read the dependency instead of theorizing about it: if the cause hinges on what a library or platform does, its source, tests, or issue tracker is minutes away. And confirm you're reading the code that ran — a stale checkout explains failures that no longer exist.

Stop when you can state the cause as a specific fact — "the timestamp is compared as a string, so `'100' < '99'`" — not an area. `references/techniques.md` covers bisection strategies, instrumentation, and concurrency, heisenbugs, and environment-only failures.

## Hand the cause to the pipeline

The fix is written test-first: a failing test at the right level (`strict-tdd` for logic, `acceptance-testing` if it only reproduces end to end), then the fix at the right level (`intake/references/fix-options.md`). Two signs the level is wrong: this is the second or third patch to the same lines, or the fix is a guard, delay, or retry around behavior you never explained.

If the investigation was slow because evidence wasn't captured — logs discarded on teardown, no trace kept — that gap is a finding, and the fix for it ships with the bug fix, in the shared harness rather than a temporary probe.

## Exit condition

A root cause stated as an evidence-backed fact, and a reliable reproduction. Hand off to `strict-tdd` or `acceptance-testing`.
