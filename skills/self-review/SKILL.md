---
name: self-review
description: "Use after implementing increments and before verification or merge — to review the full diff against the acceptance criteria, code-style, and the smell catalog with fresh eyes. Trigger whenever a feature or bugfix's implementation is complete and you're tempted to call it done. Best run as a subagent that did NOT write the code, so the review is unbiased. Invoked by dev-workflow as phase 6."
---

# Self-Review — fresh eyes on the diff before it ships

## Why this exists

The person who wrote the code is the worst-placed to review it: they see what they *meant*, not what's *there*. Self-review is a deliberate mode switch out of authoring and into critique, ideally performed by a fresh agent (see `subagent-execution`) who reads the diff cold. Its job is to catch — before verification and merge — the three things that most often slip through: a criterion left unmet, a style violation, and a design smell.

This is not a rubber stamp. A review that finds nothing on a non-trivial diff usually means the review wasn't done, not that the code was flawless.

## What to review against

Review the **entire diff for the work item** against three explicit standards, in order:

### 1. Acceptance criteria (does it do the right thing?)

Walk each acceptance criterion from `intake` and find the code and the test that satisfy it. For each:
- Is there a criterion with no corresponding behavior? → the work is incomplete.
- Is there behavior with no criterion? → either scope crept, or a criterion went unwritten; resolve which.
- Is there a criterion with no test that would fail if the behavior broke? → the TDD discipline slipped; flag it.

### 2. Code style (is it shaped right?)

Check the diff against `code-style` and its references, especially the `smells.md` catalog. Concretely scan for:
- Methods over ~10 lines; large classes; a `Service`/`Manager` that should be commands/queries.
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

## How to report findings

Produce a findings list, each entry keyed to `file:line`, stating the problem and the specific standard it violates. Separate must-fix (a violated rule, an unmet criterion) from suggestions (a judgment call). Be concrete — "extract lines 40–58 into `applyDiscount`; the method is doing validation and calculation" beats "this method is long."

If reviewing as a subagent, return the findings to the orchestrator; don't fix them yourself, so the fix goes back through `strict-tdd`.

## What happens to findings

Every must-fix goes back through `strict-tdd`, not patched in place: write a failing test that captures the corrected behavior (or the missing coverage), then fix. A style-only finding with existing coverage can be fixed in a refactor step, staying green. Either way, the fix re-enters the disciplined loop — self-review feeds the ratchet, it doesn't bypass it.

## Exit condition

Every must-fix finding is resolved through the proper loop and the diff cleanly satisfies criteria, style, and honest tests. Hand off to `verification`.
