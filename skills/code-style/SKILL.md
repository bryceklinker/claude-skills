---
name: code-style
description: "Use whenever writing or refactoring any production code, and as a gate before every commit — to enforce a strict, opinionated house style: the least code that meets the criteria, immutability by default, no comments except to explain WHY awkward code exists, results over exceptions, null objects over nulls, boolean-signaling names, single-line control flow, small functions, and clean/hexagonal architecture. Trigger it during the refactor step of strict-tdd and during adversarial-review. Applies across every language and framework — the discipline is the same."
---

# Code Style

Language-agnostic rules for how code is shaped. Apply them while writing, sharpen them in each refactor step, and check them before every commit. The reasons are in `PRINCIPLES.md` at the plugin root.

## The core

**The least code that meets the criteria.** Fewer files, types, layers, parameters, and options, with the same guarantees. No interface with one implementation, no wrapper that only forwards, no option nobody asked for, no defensive check for a state that can't occur, no helper used once. When another rule here would add structure the code doesn't need yet, this one wins.

**Immutability by default.** Construct values fully formed and return new ones rather than mutating. Mutate only where a measured need forces it, and isolate it.

**Every failure has an owner.** Expected failure is a returned result carrying a named reason; exceptions are for the unrecoverable. Work started without awaiting it — a discarded task, an `async void` handler, a background loop, a subscriber, a timer — is awaited by a caller that handles failure, self-guards with a *why*-comment naming the owner, or is observed at shutdown. Catalog: `references/failure-modes.md`.

**Avoid nulls.** Prefer a null object, an empty collection, or an explicit optional resolved at the boundary. Never silence an absence with a non-null assertion (`x!`, force-unwrap); narrow it, resolve it, or return a failure.

**Comments explain only *why*.** A constraint or deliberate awkwardness the code can't express. A stopgap's comment names what would let it be removed. Otherwise rename and extract until the code says it.

**Names carry meaning.** Nouns for values, verbs for functions, booleans that announce themselves (`isActive`, `hasBalance`), file names that match contents, test names in Given/When/Then. `references/naming.md`.

**Small units.** A function does one thing at one level of abstraction; past ~10 lines, look again. Branches are guard clauses and single-line returns; loop bodies are a line or two. Keep a behavior's inputs as plain data, separate from the code that handles them; never grow a `Service`/`Manager`/`Utility`. A plain function taking an input value is the default shape (`references/patterns.md`).

## References

| When you're… | Read |
|--------------|------|
| Naming anything, including tests | `references/naming.md` |
| Placing boundaries, ports, result types, null objects | `references/architecture.md` |
| Starting work you don't await, handling events, writing a loop | `references/failure-modes.md` |
| Considering a pattern | `references/patterns.md` |
| Refactoring or reviewing | `references/smells.md` |

## As a pre-commit gate

Scan the diff against the core and the smell list, and run `commands.lint` and `commands.format_check` from `.craft-code.yml`. When a rule genuinely fights the problem, depart deliberately and leave a *why*-comment.
