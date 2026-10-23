# Craft-Code Principles

The canonical *why* behind the suite. Skills restate only the slice they need and point here. Each rule removes a recurring source of bugs or waste; each comes with its reason so it can be applied with judgment rather than by rote.

## 1. Use less to achieve more

Complexity is the cost every later change pays, so the goal is the smallest system that meets the criteria reliably: the fewest moving parts, layers, abstractions, files, dependencies, options, and tests that together prove the behavior. Every addition earns its place against a criterion in front of you, not a future you imagine. Prefer deleting to adding, the existing shape to a new one, a function to a class, a plain value to a framework, one good test to three overlapping ones.

Minimal is not fragile. What the criteria demand — handling the failure path, a test for each behavior, the signal that shows it broke — is part of the minimum. What gets cut is the speculative: unused flexibility, interfaces with one implementation, wrapper layers, configuration nobody asked for, defensive code for states that can't occur, tests that pin the same behavior twice, scaffolding left behind.

When another rule here would add structure the change doesn't need, this one wins. Patterns, handlers, builders, and abstractions are tools for removing complexity; used without their signal they add it.

*Embodied by:* every skill; checked explicitly in `adversarial-review`.

## 2. Discipline over the speed that isn't

The costliest failures — building the wrong thing, untested code, regressions — come from skipping a step because it felt unnecessary this time. The pipeline removes that per-change decision. The one sanctioned lightening is `dev-workflow`'s in-session follow-up lane, which collapses the paperwork of intake and planning for work already agreed this session. It never collapses the failing test or the review.

*Embodied by:* `dev-workflow`.

## 3. Tests come first, and they are a ratchet

No production code is written or edited without failing tests demanding it. For each increment, write its tests first, run them, and confirm each fails for the right reason — the behavior is missing, not a typo or a broken import. Then write the minimum code to pass, commit, refactor, commit. A test you never saw fail proves nothing. Every defect found becomes a permanent test. A thing that's hard to test is telling you its design is hard to use.

*Embodied by:* `strict-tdd`, `acceptance-testing`, `systematic-debugging`.

## 4. Two loops, two levels of substitution

The question is never "do I own this?" but **"can the real thing run deterministically here?"**

- **Inner loop (unit).** Real collaborators — your code and real in-process libraries. Substitute in code only at genuinely external or non-deterministic seams (network, filesystem, clock, randomness), and prefer a real lightweight substitute over a mock.
- **Outer loop (acceptance).** The deployed application is exactly what ships; substitute only outside the process — a real database in a container, an external deployed fake at the network boundary.

A double asserts how your code talks to a collaborator, not what it achieves; used where the real thing could run, it passes while the integration breaks.

*Embodied by:* `strict-tdd`, `acceptance-testing`.

## 5. Failure is a value, and every failure has an owner

Expected failure is a returned result carrying success or a named reason; exceptions are for the genuinely unrecoverable. Avoid nulls, and never silence an absence with a non-null assertion. Work with no caller — a discarded task, a background loop, an event handler, a timer — still needs someone named to catch, log, and decide: an awaiting caller, a self-guarding body, or a lifecycle that observes it at shutdown.

*Embodied by:* `code-style` (+ `references/failure-modes.md`).

## 6. Immutability by default

Construct values fully formed and return new ones rather than mutating. It makes concurrency safe, keeps reasoning local, and removes whole classes of aliasing bugs. Mutate only where a measured need forces it, and isolate it.

*Embodied by:* `code-style`.

## 7. The domain is independent of how data enters or leaves

Transport and persistence are edge details. The domain defines what it needs; the edges implement it; dependencies point inward. Organize by feature, not by layer. Introduce a port where there is a real seam to cross — external I/O or a second implementation — not by reflex.

*Embodied by:* `architecture-design`, `code-style/references/architecture.md`.

## 8. Small, single-purpose units

A unit does one thing at one level of abstraction; long methods are a smell. Keep a behavior's inputs as plain data, separate from the code that acts on them, and never grow a `Service`/`Manager`/`Utility` grab-bag. The simplest form that honors this — usually a function taking an input value — is the default; reach for classes, handlers, factories, and strategies when the code in front of you calls for them.

*Embodied by:* `code-style` (+ `references/patterns.md`, `references/smells.md`).

## 9. Code explains itself; comments explain only *why*

Names carry meaning: nouns for values, verbs for functions, booleans that announce themselves. The only comment worth writing explains a constraint or deliberate awkwardness the code cannot.

*Embodied by:* `code-style/references/naming.md`.

## 10. Judgment is adversarial and independent; done rests on evidence

The author sees what they intended. A reviewer who didn't write the code, and who sets out to break it, sees what's there: the assumption nobody checked, the input nobody tried, the test that would pass with the bug still present, the part that could be deleted. A claim of done is backed by output observed this session — never by inspection alone.

*Embodied by:* `adversarial-review`, `verification`.

## 11. A failure you can't see is a defect

When a test or deployment fails, the evidence that explains why — logs, trace, screenshot, the failing request — must already be captured, by default, in the shared harness. The same question applies in production: what will show that it broke, and why? If an investigation was hard because evidence was missing, that gap is a finding to fix.

*Embodied by:* `acceptance-testing` (+ `references/diagnosability.md`), `systematic-debugging`; craft-ops' `observability-design`.

## 12. Find the cause before you change anything

A bug is an information problem. Reproduce it, narrow by bisection, and confirm one falsifiable hypothesis at a time. Only a confirmed cause re-enters the pipeline as a failing test.

*Embodied by:* `systematic-debugging`.

## 13. Fix the cause at its level, and recommend the durable option

The minimum change is the minimum diff *at the right level*, not the shallowest patch that turns a test green. Where symptom, cause, and structural fixes genuinely trade off, lay them out and recommend the most durable one that fits the real constraints. A stopgap ships with a *why*-comment naming what would let it be removed. A symptom that recurs in the same lines is evidence the level was wrong.

*Embodied by:* `intake` (+ `references/fix-options.md`), `systematic-debugging`, `adversarial-review`.

## 14. State the why; keep the escape hatch

When a rule genuinely fights the problem in front of you, depart from it deliberately and record why — a *why*-comment is the sanctioned escape hatch. Silent abandonment is not.

---

*Lineage:* Clean Code, Fowler's *Refactoring*, Meszaros' *xUnit Test Patterns*, ports-and-adapters, CQRS, classicist (Detroit-school) TDD — tempered by YAGNI and "the simplest thing that could possibly work."
