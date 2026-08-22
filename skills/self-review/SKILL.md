---
name: self-review
description: "Use after implementing increments and before verification or merge — to review the full diff against the acceptance criteria, code-style, the smell catalog, and its runtime failure modes (unawaited work, swallowed errors, stopgaps that will bring you back) with fresh eyes. Trigger whenever an implementation is complete and you're tempted to call it done — a feature, a bugfix, and just as much a small in-session adjustment or a change made in response to feedback, which skip review most often and need it just as much. Best run as a subagent that did NOT write the code, so the review is unbiased. Invoked by dev-workflow as phase 6."
---

# Self-Review — fresh eyes on the diff before it ships

## Why this exists

The person who wrote the code is the worst-placed to review it: they see what they *meant*, not what's *there*. Self-review is a deliberate mode switch out of authoring and into critique, ideally performed by a fresh agent (see `subagent-execution`) who reads the diff cold. Its job is to catch — before verification and merge — the three things that most often slip through: a criterion left unmet, a style violation, and a design smell.

**If you dispatch this to a subagent, use a fresh, read-only reviewer — never a `fork`.** "Fresh eyes" is the entire mechanism, and a fork inherits the author's context, so it reviews with exactly the bias this phase exists to escape. A fork also carries write access with no barrier against fixing what it finds and committing it — which both defeats the report-don't-patch rule below and quietly corrupts the diff under review. The read-only `craft-code-reviewer` starts cold and cannot edit; that is the point. `subagent-execution` covers how to dispatch it and how to verify the read-only constraint actually held.

This is not a rubber stamp. A review that finds nothing on a non-trivial diff usually means the review wasn't done, not that the code was flawless.

## What to review against

Review the **entire diff for the work item** against four explicit standards, in order:

### 1. Acceptance criteria (does it do the right thing?)

Walk each acceptance criterion from `intake` and find the code and the test that satisfy it. For each:
- Is there a criterion with no corresponding behavior? → the work is incomplete.
- Is there behavior with no criterion? → either scope crept, or a criterion went unwritten; resolve which.
- Is there a criterion with no test that would fail if the behavior broke? → the TDD discipline slipped; flag it.

### 2. Code style (is it shaped right?)

Check the diff against `code-style` and its references, especially the `smells.md` catalog. Concretely scan for:
- Methods over ~10 lines; large classes; a `Service`/`Manager`/`Utility` that should be split into operations (input data object + its own handler).
- Mutable state that could be immutable (the highest-priority check).
- Comments explaining *what* instead of *why*.
- Thrown exceptions where a result was expected; nulls where a null object belongs.
- Duplicated `switch`/`if-else`; multi-line branches that should be single-line returns; loop bodies over 1–2 lines.
- Names: variables nouns, functions verbs, booleans with `is/has/should/can` prefixes, test names in Given/When/Then.
- Law of Demeter train-wrecks; data classes.

### 3. Tests (are they honest?)

- Do any tests double something that could have run for real — owned code or a real in-process library? → violates the doubles rule.
- Is the test code itself clean, or does it carry the smells in `test-utilities.md` (mystery guest, irrelevant detail, assertion roulette)?
- Was each behavior driven by a test, not retrofitted?

### 4. Durability and failure modes (will it hold, and what happens when it breaks?)

The first three standards ask whether the diff is correct and well-shaped. This one asks whether it will still be the right code in six months, and what it does on the bad path.

**A mechanical scan — every hit is either justified in place or a must-fix.** Go looking for these by name in the diff; they don't announce themselves in review the way a long method does:

- **Work started but not awaited** — a discarded task (`_ =`), a floating promise, a bare `go`/`create_task`, `async void` or any async handler with no return path, a background loop, a timer callback, an event subscription. For each: *if this throws, who finds out?* The three legal answers are awaited by a caller, self-guarding with a *why*-comment, or observed at shutdown. Anything else is a defect even though nothing is failing today. See `code-style/references/failure-modes.md`.
- **Loops whose guard sits outside the try** — one bad iteration silently ending a background worker.
- **Empty catches, swallowed errors, and lowered log levels** — a failure that now happens invisibly.
- **Non-null assertions and suppressions** added to make a compiler quiet.
- **Subscriptions with no matching unsubscribe.**

**Durability.** Is this fixed at the right level, or is it a patch that will bring us back here?

- Is the change a guard, retry, delay, or disable wrapped around a mechanism nobody explained? That's a symptom fix wearing a cause fix's clothes.
- Does the diff touch code that was *already* patched recently for the same symptom? A third round in the same few lines says the level was wrong — flag it even if this round works.
- Does a stopgap carry a *why*-comment naming what would let it be removed? An unnamed one becomes the design.
- Does the change buy its green by **weakening a guarantee** — making a confirmation non-blocking, dropping a check, accepting before the server agreed? That's a product decision, not a bugfix detail; it must be surfaced, not slipped in.

**Blast radius.** For anything that blocks, disables, locks, serializes, or guards: *could this block the operation it is meant to protect?* Name what the change makes impossible, not only what it prevents.

**Diagnosability.** Would a failure here be visible? If the diff removes signal — teardown that discards logs, a retry reporting only the last attempt, an assertion that reports `false` instead of the value it saw — that's a regression in the same sense a broken test is (`acceptance-testing/references/diagnosability.md`).

## How to report findings

Produce a findings list, each entry keyed to `file:line`, stating the problem and the specific standard it violates. Separate must-fix (a violated rule, an unmet criterion) from suggestions (a judgment call). Be concrete — "extract lines 40–58 into `applyDiscount`; the method is doing validation and calculation" beats "this method is long." For a smell, name the resolving technique from `refactoring` (its smell → technique map) so the fix is unambiguous — "Extract Function", "Hide Delegate", "Replace Conditional with Polymorphism" — not just "clean this up."

If reviewing as a subagent, return the findings to the orchestrator; don't fix them yourself, so the fix goes back through `strict-tdd`.

## What happens to findings

Every must-fix goes back through `strict-tdd`, not patched in place: write a failing test that captures the corrected behavior (or the missing coverage), then fix. A style-only finding with existing coverage can be fixed in a refactor step, staying green. Either way, the fix re-enters the disciplined loop — self-review feeds the ratchet, it doesn't bypass it.

## Exit condition

Every must-fix finding is resolved through the proper loop and the diff cleanly satisfies criteria, style, honest tests, and the durability/failure-mode scan. Hand off to `verification`.
