# Craft Principles

The one place the *why* behind the whole methodology is stated. Individual skills restate the slice of this they need to stand alone, but this is the canonical source — when a skill says "see the craft principles," it means here. Every rule in the suite is strict on purpose: each removes a recurring source of bugs or friction. None is dogma, because each is given with its reason, and each has an escape hatch for the case where it genuinely fights the problem in front of you.

## 1. Discipline over the speed that isn't

The failures that cost the most — building the wrong thing, untested code, style drift, regressions — almost always come from skipping a step because it "felt unnecessary this time." There is no fast lane, because the fast lane is where the bugs live. The pipeline removes the per-change decision to skip; the gate is cheap, the missed assumption is not.

*Embodied by:* `dev-workflow` and its gates.

## 2. Tests come first, and they are a ratchet

No production code is written or edited without a failing test demanding it — watched failing, then passing, so you know it tests something. Every defect found becomes a permanent test that would have caught it. The suite only ever tightens. This is a design tool as much as a safety net: a thing that's hard to test is telling you the design is hard to use.

*Embodied by:* `strict-tdd`, `acceptance-testing`, `systematic-debugging`.

## 3. Two loops, two levels of substitution

Quality comes from exercising the real thing, and the question is never "do I own this code?" but **"can the real thing run deterministically here?"**

- **Inner loop (unit).** Use real collaborators — your own code and real in-process libraries alike. Substitute *in code* only at genuine external or non-deterministic seams: the network, filesystem, clock, randomness. Even there, prefer a real lightweight substitute over a mock.
- **Outer loop (acceptance).** Keep the deployed application byte-for-byte what ships and substitute *outside* the process: a real database in a container, and for the few dependencies that can't be real, an external deployed fake at the same network boundary — never a code-level double reaching into the running app.

A double asserts *how* your code talks to a collaborator, not *what* it achieves; used where the real thing could have run, it passes while the real integration breaks.

*Embodied by:* `strict-tdd` (+ `references/testing-doubles.md`), `acceptance-testing` (+ `references/environment.md`).

## 4. Failure is a value, not an exception

Model expected failure as a returned result carrying success or a named reason. Exceptions are for the genuinely unrecoverable, not for control flow the caller is expected to handle — a result makes the failure path visible in the signature; an exception hides it and invites the caller to forget it. In the same spirit, avoid nulls: prefer null objects with safe behavior, and never suppress an absence with a non-null-assertion operator, which silences the compiler without removing the null.

*Embodied by:* `code-style` (+ `references/architecture.md`, `references/smells.md`).

## 5. Immutability by default

Construct values fully formed and return new ones rather than mutating in place. Immutable data is what makes concurrency safe, keeps reasoning local, and makes whole classes of aliasing bugs impossible. Reach for mutation only where a measured need forces it, and isolate it when you do. This is the highest-priority style rule, and it prevents most race conditions before they can exist.

*Embodied by:* `code-style`.

## 6. The domain is independent of how data enters or leaves

HTTP, GraphQL, gRPC, the database, the queue — details at the edge. The core domain knows nothing of them. Dependencies point inward: the domain defines ports for what it needs; the outer layers implement them. Organize by feature, not by technical layer, so a feature's boundaries are visible and it can be extracted or deleted cleanly. This is what makes the domain testable with real collaborators — the only thing you substitute is an adapter.

*Embodied by:* `architecture-design`, `code-style/references/architecture.md`.

## 7. Small, single-purpose units — and messages over managers

Methods over ~10 lines are a smell; extract until each does one thing at one level of abstraction. Structure behavior as CQRS — an immutable message plus a dedicated handler per operation — rather than a `Service`/`Manager` that only ever grows. Commands may return the data the caller needs; queries never mutate. Isolate branching behind factories and strategies; keep control flow reading top-to-bottom as guard clauses.

*Embodied by:* `code-style` (+ `references/patterns.md`, `references/smells.md`).

## 8. Code explains itself; comments explain only *why*

Names carry meaning: variables are nouns, functions are verbs, booleans announce themselves (`isActive`, `hasBalance`). A file's name matches its contents. The only comment worth writing explains a *why* the code cannot — a non-obvious constraint or a deliberate, externally-forced awkwardness. A comment restating *what* the code does is noise that rots; rename and extract until the code says it itself.

*Embodied by:* `code-style/references/naming.md`.

## 9. Judgment is independent, and "done" rests on evidence

The person who wrote the code is primed to see what they intended; fresh eyes see what's actually there. Review and verification run as independent passes (and, in parallel work, as agents that didn't write the code). A claim of done is backed by output observed this session — the full suite green, the acceptance suite green, each acceptance criterion exercised — never by inspection or reasoning alone. If you didn't run it, you don't know.

*Embodied by:* `self-review`, `verification`.

## 10. Find the cause before you change anything

A bug is an information problem, not a typing problem. Reproduce it, narrow the search space by bisection, and confirm one falsifiable hypothesis at a time before touching code. Guessing moves the symptom; method finds the root. Only once the cause is a specific, evidence-backed fact does the fix re-enter the pipeline as a failing test.

*Embodied by:* `systematic-debugging` (+ `references/techniques.md`).

## 11. State the why; keep the escape hatch

Every strict rule here is legible rather than dogmatic because it comes with its reason. When a rule genuinely fights the problem in front of you, that tension is worth a conscious, recorded note — a *why*-comment is literally the sanctioned escape hatch — not a silent abandonment of the discipline. The rules are strict so that applying them by reflex frees attention for the actual problem; they are not strict for their own sake.

---

*Lineage:* this methodology draws on Clean Code, Fowler's *Refactoring*, Meszaros' *xUnit Test Patterns*, ports-and-adapters / hexagonal architecture, CQRS, and classicist (Detroit-school) TDD.
