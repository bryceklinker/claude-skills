---
name: code-style
description: "Use whenever writing or refactoring any production code, and as a gate before every commit — to enforce a strict, opinionated house style: immutability by default, no comments except to explain WHY awkward code exists, results over exceptions, null objects over nulls, boolean-signaling names, single-line control flow, small functions, and clean/hexagonal architecture. Trigger it during the refactor step of strict-tdd and during self-review. Applies across every language and framework — the discipline is the same."
---

# Code Style — the house discipline

These rules are framework- and language-agnostic; they're about how code should be shaped, not which tools produce it. Apply them continuously while writing, sharpen them in every refactor step, and treat them as a gate before any commit. The details live in focused reference files — this page is the always-loaded core plus a map to the rest.

## The non-negotiable core

**Immutability by default.** This is the highest-priority rule. Construct values fully formed and don't mutate them; return new values instead of changing existing ones. Immutable data is what makes concurrency safe, makes reasoning local, and makes whole classes of aliasing bugs impossible. Reach for mutation only where a measured need forces it, and isolate it when you do.

**No comments — except to explain *why* awkward code exists.** Code says *what* and *how*; a comment that restates that is noise that rots. The only comment worth writing explains a *why* the code cannot: a non-obvious workaround, an ordering constraint, a deliberate deviation forced by something external. If you're tempted to comment *what* the code does, rename things and extract methods until the code says it itself.

**Results over exceptions.** Model expected failure as a returned result that carries success or a named reason for failure. Exceptions are for the truly exceptional — genuinely unrecoverable conditions — not for control flow the caller is expected to handle. A result type makes the failure path visible in the signature; an exception hides it and invites the caller to forget it. See `references/architecture.md` for the result-type shape.

**Avoid nulls; use null objects.** A null is an absence that every caller must remember to check, and forgets. Where a value can be "nothing," prefer a null object — a real instance with safe, do-nothing behavior — or an explicit optional at the boundary, so nulls stay rare and never propagate into the domain. **Never suppress an absence with a non-null assertion / null-forgiving operator** (`x!` in TypeScript, `x!` in C#, `!!` casts, force-unwraps) — they silence the compiler without removing the null, so the crash just moves to runtime. Handle the absence: narrow it, resolve it to a null object, or return a failure.

**Names carry meaning.** Variables are nouns. Functions are verbs. Booleans and boolean-returning functions announce themselves: `isActive`, `hasBalance`, `shouldRetry`, `canEdit`. A file's name matches its contents. Full rules and examples: `references/naming.md`.

**Small units.** Methods over ~10 lines are a smell; extract until each does one thing. `if`/`else` and `switch` are single-line return statements, not sprawling blocks. Loop bodies are 1–2 lines — extract the per-item method. Full smell catalog and the refactorings that resolve each: `references/smells.md`.

## Reference map — read the one you need

| When you're... | Read |
|----------------|------|
| Naming anything, or writing a test name | `references/naming.md` |
| Structuring modules, layers, dependencies, result types, null objects | `references/architecture.md` |
| Choosing or recognizing a design pattern | `references/patterns.md` |
| Reviewing or refactoring; something smells off | `references/smells.md` |

## The shape of well-styled code

To make the core concrete before you dive into references, a sketch of what "good" looks like here:

- Data comes in immutable, is transformed by small pure functions, and leaves as a new immutable value.
- Control flow reads top-to-bottom as guard clauses returning early, not nested `if`/`else` pyramids.
- Failure is a value you can see in the type, handled by the caller, not an exception thrown past three layers.
- A reader understands each function from its name and its ten lines, without a comment and without scrolling.
- Where the code branches on a type or a case, a factory or strategy has replaced the repeated `switch`.

## Using this skill

- **While writing (inside `strict-tdd`'s refactor step):** apply the core rules and pull up the relevant reference when a specific decision arises.
- **As a pre-commit gate:** scan the diff against the core rules and the smell list, and run the project's `commands.lint` and `commands.format_check` from `.craft.yml` (see `project-conventions`) — the linter enforces mechanically what this page enforces by judgment. A commit that adds a comment-that-explains-what, a mutable-by-default structure, a thrown exception for an expected failure, or a method over ~10 lines isn't ready.
- **During `self-review`:** the reviewer checks the whole diff against `references/smells.md` explicitly.

The point of the strictness is not conformity for its own sake — it's that each rule removes a recurring source of bugs or friction, and applying them by reflex frees attention for the actual problem. When a rule genuinely fights the problem in front of you, that tension is worth a conscious note (a *why* comment is literally the escape hatch), not a silent abandonment of the style. The reasons behind these rules are stated canonically in the craft principles (`PRINCIPLES.md` at the plugin root).
