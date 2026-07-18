---
name: strict-tdd
description: "Use when implementing ANY increment of production code — features, bugfixes, refactors, behavior changes — before writing implementation. This is a strict, classicist form of TDD: no code before a failing test, one test at a time, watch it go red then green, commit at green AND after refactor, and use real implementations wherever they run deterministically in-process (no mocking/stubbing your own code OR real in-process libraries; doubles only at genuine external/non-deterministic seams). Trigger it for every increment in the plan. If you're about to write implementation and haven't watched a test fail, stop and use this."
---

# Strict TDD — the classicist discipline

## The core loop

Write one failing test. Watch it fail for the right reason. Write the minimum code to pass. Watch it pass. **Commit the green — then** refactor, production *and* test code, and commit that separately. Then the next test. The order matters: green is committed before any refactoring, so it's always a point you can fall back to.

**If you didn't watch the test fail, you don't know that it tests anything.** A test written after the code passes immediately, which proves nothing — not that the behavior is right, not that the test would ever catch a regression.

## The iron law

<HARD-GATE>
NO PRODUCTION CODE IS WRITTEN OR EDITED WITHOUT A FAILING TEST DEMANDING IT.

Wrote code before the test? Delete it — actually delete it, don't keep it as "reference" and don't adapt it while writing the test. Re-derive it from the test. Code you kept and wrapped a test around is code tested after the fact, which is not TDD and doesn't earn the trust TDD earns.
</HARD-GATE>

This feels wasteful the first time and stops feeling wasteful once you've watched a "reference" implementation smuggle in a bug that the after-the-fact test happily approved.

## Red → Green → Refactor, one test at a time

Work **one test at a time**. Not a batch of tests, not the whole increment's worth of assertions up front — one behavior, driven to green, before the next. Batching tests hides which one is driving which line of code and makes red-green meaningless.

### RED — write one failing test

One test, one behavior, a name that reads as a specification. Use the **Given / When / Then** convention (Given optional; When and Then required) — see `code-style` for naming. Drive real code through its real interface; do not reach for a double (see the doubles rule below).

Then **run it and watch it fail.** Confirm:
- It fails — it doesn't error on a typo or a missing import.
- It fails for the *expected reason*: the behavior is missing, not something incidental.

A test that passes the first time is testing something that already exists — fix the test. A test that errors — fix the error and re-run until it fails cleanly.

### GREEN — minimum code to pass

Write the simplest thing that makes this one test pass. Not the general solution, not the configurable version, not the next three behaviors you can see coming — YAGNI. The next test will force the next piece of generality honestly.

Then **run it and watch it pass** — this test, and the whole suite. Output should be pristine: no new warnings, no errors. Other tests broke? Fix them now, before moving on.

### COMMIT THE GREEN — before you touch the design

The instant the test passes and the suite is green, **commit it.** This happens *before* any refactoring. That green commit is the entire safety mechanism of the cycle: a behavior-complete, known-good point you can fall back to if the next step goes wrong. Refactor on top of an uncommitted green and you've thrown that safety away — and you'll end up with one commit that tangles new behavior with cleanup, which can't be reviewed or reverted cleanly.

<HARD-GATE>
Reach green → commit → THEN refactor. Never refactor before the green is committed, and never bundle "add behavior" and "refactor" into one commit. If you catch yourself cleaning up code that isn't committed green yet, stop and commit first.
</HARD-GATE>

### REFACTOR — clean up, staying green

With the green committed, improve the design without changing behavior: remove duplication, sharpen names, extract methods, apply the patterns in `code-style`. **Refactor the test code too** — test code is real code and decays the same way. Duplicated setup, unclear arrange steps, and copy-pasted assertions are smells in a test just as in production. Extract them into the shared test utilities (see `references/test-utilities.md`).

Keep the suite green throughout the refactor. If it goes red, the last change was behavior, not refactoring — revert and reconsider.

### COMMIT THE REFACTOR

If you refactored, commit that as its own "refactor X" commit. Now you have two small, honest commits — "add X behavior" then "refactor X" — each independently reviewable and revertible. (A cycle that genuinely needed no refactoring just has the one green commit; that's fine. The rule is only that a refactor never rides along inside the behavior commit.)

Then start the next test.

## The doubles rule — use the real thing wherever you can run it

Strict TDD departs sharply from the mockist habit. The default is real collaborators, and the bar for introducing a test double is high:

<HARD-GATE>
Use the REAL implementation of a dependency whenever it runs deterministically and in-process. That includes your own code AND real third-party libraries — `@mui/*`, `lodash`, MediatR, FluentValidation, date/money libraries, and the like are real, in-process, deterministic code: wire them up for real, never double them.

Introduce a test double ONLY at a genuine external or non-deterministic seam: the network, the filesystem, the system clock, randomness, message brokers, third-party services over the wire, or a database you don't control. And even there, prefer a real lightweight substitute (in-memory database, temp directory, injected fixed clock) over a mock of the interaction.
</HARD-GATE>

The reasoning: a double asserts *how* your code talks to a collaborator, not *what* your code achieves. Double something that could have run for real and you get a test that passes while the real integration is broken, and that shatters on every refactor because it's pinned to structure instead of behavior. The exception is the boundary — you double the network or the clock not because it's third-party, but because it's slow, flaky, or non-deterministic and can't run honestly inside a unit test. The test of whether to double is never "do I own it"; it's **"can the real thing run deterministically here?"** If yes, use it.

If a unit is painful to test without doubling something you could otherwise run, that pain is a design signal, not a reason to reach for a double. The design is too coupled — invert the dependency, pass collaborators in, or split the responsibility. Listen to the test. Full boundary definition and worked examples: `references/testing-doubles.md`.

## Build up test utilities

Tests should get *easier* to write as the suite grows, because each test contributes reusable setup. Instead of hand-assembling objects in every test, build a vocabulary of test utilities — Test Data Builders, Object Mothers, custom assertions, and fixtures — that make each new test short and intention-revealing. This is a first-class part of the work, not an afterthought. Patterns and when to use each: `references/test-utilities.md`.

## Refactoring changes nothing about the above

Refactoring is a behavior-preserving change, so it's covered by existing tests: keep them green as you go, and if the refactor reveals missing coverage, add the failing test first. "Refactoring" that needs new behavior isn't refactoring — it's a new increment; give it its own RED.

## Red flags — stop and restart the cycle

- Production code exists with no test that failed first → delete it, start from RED.
- A test passed the moment you wrote it → it's testing existing behavior or nothing; fix it.
- You can't say why the test failed → you didn't watch it fail; re-run and read the failure.
- You doubled something that could have run for real (your code, or a real in-process library) → remove the double, use the real thing or invert the dependency.
- Several assertions for several behaviors landed in one test → split them; one behavior per test.
- One commit mixes new behavior and refactoring → separate them next cycle; commit at green and after refactor.

## Rationalizations to reject

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code still breaks, and the test costs seconds. |
| "I'll write the tests after" | Tests-after pass immediately and prove nothing. You never saw them catch anything. |
| "I'll mock this library to keep the test isolated" | If it runs in-process and deterministically, use it for real. Doubling it tests your mock, not your code. |
| "I need to mock this, it's my own service" | Ownership isn't the question — determinism is. If it can run here, run it. If it can't, the coupling is the bug. |
| "Deleting this working code is wasteful" | Sunk cost. Untrusted code is the liability; the test-first rewrite is the asset. |
| "Batching the tests is faster" | Batching hides which test drives which code and kills red-green. One at a time. |
| "I'll commit once at the end" | Then behavior and refactor are tangled and nothing is cleanly reviewable or revertible. |
| "The test is hard to write" | The design is hard to use. The test is telling you something — listen. |

## Exit condition

Every increment's behavior is covered by a test that was watched failing and then passing; production and test code are refactored clean; commits landed at green and after refactor; the whole suite is green with pristine output. Hand off to `self-review`.
