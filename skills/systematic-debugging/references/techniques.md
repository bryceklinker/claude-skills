# Debugging Techniques — narrowing, observing, and the hard classes of bug

The SKILL.md gives the loop: reproduce → narrow → hypothesize → confirm. This reference is the toolbox for each step and for the bugs that resist it.

## Table of contents
- Bisection in depth
- Instrumentation without changing behavior
- Reading a stack trace
- Minimizing a reproduction
- The hard classes (concurrency, heisenbugs, environment-only)
- Binary-searching a "works here, not there"

## Bisection in depth

Bisection is the workhorse because it's logarithmic — each step halves the space.

- **`git bisect` for regressions.** If it worked before, the cause is a commit. `git bisect start; git bisect bad; git bisect good <known-good>` then test each revision (script it with `git bisect run <cmd>` when the test is automatable). The output is the exact introducing commit — often the whole diagnosis.
- **Bisect the code path.** Place an observation point (log, assertion, breakpoint) at the midpoint between where state is known-correct and where it's known-wrong. Whichever half still holds the divergence is where the fault lives. Move to that half's midpoint; repeat. Five steps localizes a fault across ~32 stages.
- **Bisect configuration/data.** Halve the input, the feature flags, the config. Still fails? The cause is in the remaining half. This finds "one poisoned record" and "one bad setting" fast.
- **Bisect dependencies.** For "broke after an upgrade," bisect the lockfile — pin half the bumped versions back.

## Instrumentation without changing behavior

Prefer *observing* over *changing* — a probe that alters behavior can create or hide the bug.

- **Log the state at the boundary**, not everywhere. You're looking for the single transition from correct to wrong; instrument around your current bisection midpoint.
- **Assert your assumptions.** `assert x >= 0` at a point where you believe x is non-negative either passes (assumption holds, move on) or fires (you found a divergence). Assertions are falsifiable hypotheses in code form.
- **Log identities and types, not just values.** "`total` is `100`" hides that it's the *string* `"100"`. Log the type/shape when a value looks right but behaves wrong.
- **Capture the whole state at failure** — inputs, relevant globals, timestamps, thread/request id — so you can reason offline instead of re-running.
- **Remove every probe when done.** Probes are experiments, not features.

## Reading a stack trace

- Read it **top to bottom**: the top frame is where it threw, but the *cause* is often a few frames down where a bad value originated. The boundary between your code and framework/library code is where to look first.
- Note the **exact exception type and message** — `undefined is not a function` vs `null reference` vs `index out of range` each point at different mistakes.
- For async/promise chains, look for the **async boundary** — the useful frame may be in a continuation, and naive traces truncate at the await. Enable async stack traces if the runtime supports them.
- A trace that points *only* into library code usually means you passed bad input in — walk back to your last frame.

## Minimizing a reproduction

A minimal repro is the highest-value artifact in debugging — it shrinks the search space and often becomes the regression test.

- **Delete-and-retest.** Remove code, data, config, and steps that you can while the failure persists. What remains is load-bearing.
- **Inline and isolate.** Pull the failing path into a standalone test or script with hardcoded inputs, away from the rest of the system.
- **Freeze the non-deterministic.** Pin the clock, seed the RNG, fix the ordering — if the bug survives, those weren't the cause; if it vanishes, they were.

## The hard classes

- **Concurrency / race conditions.** The symptom is intermittency correlated with load, timing, or parallelism. Narrow *what races*: add deliberate delays to widen the window and make it reliable, log thread/task ids with timestamps, look for shared mutable state crossing a boundary. The fix usually removes the sharing (immutability, ownership) rather than adding a lock. Immutability-by-default prevents most of these before they start.
- **Heisenbugs** (vanish when observed). The probe changed timing or optimization. Use lower-disturbance observation — post-hoc logging to a buffer, hardware/data breakpoints, or capture-and-replay — rather than stepping in a debugger. If adding a log fixes it, you've localized to a timing/ordering fault.
- **Environment-only** ("works locally, fails in CI/prod"). Bisect the *environment difference*: versions, env vars, data volume, timezone/locale, filesystem case-sensitivity, resource limits, network policy. Make local look like the failing environment one variable at a time until it reproduces — then you've named the cause.

## Binary-searching a "works here, not there"

When the same code behaves differently across two environments, the bug is in the *difference*, and the method is the same bisection applied to the environment:

1. Enumerate every difference you can (OS, runtime version, config, data, dependencies, clock/locale, permissions).
2. Change the working environment halfway toward the broken one (or vice-versa).
3. Did the behavior flip? The cause is in the half you changed. Narrow.

This turns a frustrating "it's just different" into the same logarithmic hunt as everything else.
