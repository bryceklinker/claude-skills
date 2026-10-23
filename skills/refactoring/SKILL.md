---
name: refactoring
description: "Use when asked to refactor, clean up, restructure, tidy, simplify, de-duplicate, extract, inline, delete dead code, or otherwise improve the internal structure of existing code WITHOUT changing what it does — and when finding code smells and deciding how to resolve them. Trigger on 'refactor this', 'clean up this class', 'this method is too long', 'reduce the duplication here', 'this is over-engineered', 'simplify this conditional', 'find the smells and fix them'. Behavior-preserving only: if the change alters observable behavior (a new feature, a bugfix, different output), that is dev-workflow/strict-tdd, not this. Provides the named techniques, their safe mechanics, and the map from each smell to the technique that resolves it. It supplies the moves, never a licence to skip the pipeline: a restructure spanning several files, or one needing a characterization net built first, still runs inside dev-workflow — this skill is what you reach for within it."
---

# Refactoring

A refactoring changes structure without changing observable behavior. The goal is code that's easier to understand and cheaper to change, and usually that means *less* code: the most valuable refactorings often delete — dead code, a layer that only forwards, an interface with one implementation, a helper used once.

This skill supplies the moves. `strict-tdd` owns the green/commit ratchet it runs inside; `code-style` and its `references/smells.md` define the destination and the triggers. One technique on the smell in front of you is this skill alone; a restructure across several files, or one that needs a characterization net first, is a work item for `dev-workflow`.

## The discipline

1. **Start green.** If the code has no test covering its behavior, write characterization tests first (seen passing on current behavior, named Given/When/Then, real collaborators) and commit them.
2. **One named technique at a time**, using its mechanics from `references/techniques.md` rather than a freehand rewrite.
3. **Run the scoped tests after each small step.** If one goes red, the step changed behavior — revert it.
4. **Commit each technique that lands green**, on its own (`refactor: …`), never inside a behavior commit. Don't end a session with refactoring uncommitted.
5. **Refactor test code too**, with the same techniques.

If the change turns out to need new behavior, it isn't a refactoring: that part goes through `strict-tdd` with its own failing test.

## Smell → technique

| Smell | Resolve with |
|-------|--------------|
| Speculative generality: one-implementation interface, unused option or parameter, forwarding layer | Inline Single-Use Abstraction; Remove Parameter; Remove Middle Man; Collapse Hierarchy |
| Dead code | Remove Dead Code |
| Long method | Extract Function (Replace Function with Command if tangled in local state) |
| Large class (`Service`/`Manager`/`Utility`) | Extract Class along responsibilities; split into operations |
| Duplicate code (same reason to change) | Extract Function; Pull Up Method for siblings |
| Long parameter list / data clumps | Introduce Parameter Object; Preserve Whole Object |
| Sprawling or nested conditional | Replace Nested Conditional with Guard Clauses; Decompose Conditional |
| Duplicated switch on a type | Replace Conditional with Polymorphism; Replace Type Code with Strategy |
| Law of Demeter train-wreck | Hide Delegate; Move Function to the data's owner |
| Data class / feature envy | Move Function onto the data |
| Comment explaining *what* | Extract Function with an intention-revealing name; Rename |
| Magic literal | Replace Magic Literal with a named constant |
| Long loop body | Extract Function for the per-item work; Replace Loop with Pipeline |
| Mutable state / reassigned temp | Split Variable; Replace Temp with Query; build an immutable value |
| Nulls / non-null assertions | Introduce Null Object; narrow with a guard; return a Result |

Prefer the removing techniques when they resolve the smell: Inline before Extract, delete before generalize. Extract only when the extracted piece has a name that says more than its body.

## Exit condition

The smell is gone, every step kept the suite green, each technique landed as its own refactor commit, and `git status` is clean.
