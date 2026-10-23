---
name: strict-tdd
description: "Use when implementing any increment of production code — features, bugfixes, behavior changes, and adjustments requested as feedback or a casual 'just change/tweak/fix X' — before writing or editing implementation. Classicist TDD paced for an agent: write the increment's tests first, run them and confirm each fails for the right reason, write the minimum code to pass, commit, refactor with the refactoring skill, commit, then the next increment. Uses real implementations wherever they run deterministically in-process (no mocking your own code or real in-process libraries); doubles only at external or non-deterministic seams. If you're about to edit production code and haven't watched a test fail, use this. Not for ops scripts and pipeline/infra glue, which craft-ops proves by running them."
---

# Strict TDD

Tests first, watched failing, then the least code that passes. The unit of work is an **increment** from the plan, not a single assertion: you write all of the increment's tests up front, because you can hold its whole behavior at once and a run-edit-run loop per assertion adds time without adding information. What keeps it honest is that every test is seen failing for the right reason before any implementation exists.

## The cycle, per increment

1. **Write the increment's tests.** One test per behavior the increment adds, named Given/When/Then (`code-style/references/naming.md`), driving real code through its public interface. Add only the bare signature (an empty function, a type) needed for them to compile, so failures are assertions rather than errors.
2. **Run them and read every failure.** Each must fail because the behavior is missing. An import error, typo, or compile failure is not a red — fix it and re-run. A test that already passes isn't specifying anything new — fix it or delete it.
3. **Write the minimum code to pass them all.** Not the general solution, not the next increment's behavior, not configurability nobody asked for. Run the scoped tests, then the full unit suite (`commands.test` from `.craft-code.yml`; see `craft-code-conventions`). Output clean — no new warnings.
4. **Commit** tests and code together (`feat:` / `fix:`). This green commit is your fallback point; never refactor on top of an uncommitted green.
5. **Refactor** production and test code using the `refactoring` skill — a named technique per smell, suite green after each step. Deleting is refactoring too: anything the tests don't need goes.
6. **Commit the refactor** on its own (`refactor:`). If nothing needed refactoring, there is no second commit.
7. Start the next increment.

If an increment needs more than a handful of tests, or the code to pass them sprawls across many files, it's too big to see failing cleanly — split it (`planning`).

While iterating, run the narrowest command that covers the code you're touching; widen to the full unit suite before each commit. The acceptance suite is never part of this loop.

## Rules

- **No production code without a failing test demanding it.** If you wrote code first, delete it and re-derive it from the tests — code you wrap a test around afterwards was never seen to be needed.
- **Adjustments are behavior changes.** "Make it retry instead of throw" gets a red test first. The red also proves the change was needed: if you can't make a test fail without it, the code may already do what was asked.
- **Keep the tests minimal.** One test per behavior; don't pin the same behavior twice at the same level, and don't test what the type system or framework already guarantees. Extract a builder or helper when the same setup appears a third time, not before (`references/test-utilities.md`).
- **Use the real thing wherever it runs deterministically in-process** — your own code and real libraries alike. Doubles only at the network, filesystem, clock, randomness, or another process, and even there prefer a real lightweight substitute (temp dir, fixed clock, in-memory port implementation) over a mock. A unit that's hard to test without doubling something runnable has a design problem: pass collaborators in or split the I/O from the logic. Details: `references/testing-doubles.md`.
- **For a defect, decide the fix level before you type.** If the same lines were patched before for the same symptom, or the fix is a guard, retry, or delay around a mechanism you can't explain, you're fixing too low. Where levels genuinely trade off, lay them out and recommend one (`intake/references/fix-options.md`).
- **Every detached call site has a failure owner.** Before leaving the refactor step, check each place the increment starts work without awaiting it (a discarded task, floating promise, `async void`, background loop, timer, subscription) and answer *if this throws, who finds out?* If nobody, that's missing behavior: give it its own red (`code-style/references/failure-modes.md`).

## Stop and restart the cycle when

- production code exists that no failing test demanded;
- you can't say why a test failed, or you never ran it before implementing;
- a double stands in for something that could run for real;
- a commit mixes new behavior with refactoring.

## Exit condition

Every behavior in the increment is covered by a test that was seen failing for the right reason, then passing; the code is the least that passes; refactors landed separately; detached work has a named owner; the full unit suite is green with clean output. Hand off to `adversarial-review`.
