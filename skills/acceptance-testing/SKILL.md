---
name: acceptance-testing
description: "Use to drive a feature with an outer, user-level acceptance test that runs against a production-like deployment — real UI and API together, a real database in a container or a deployed app, and real external services (or external deployed fakes, never code-level doubles). This is the outer loop of double-loop TDD: write the acceptance test up front from the agreed criteria, watch it fail, then let the inner strict-tdd increments drive it green; its passing is what proves the feature works end to end. Trigger whenever a user-facing feature or a change to a user flow begins implementation, or when someone asks for an end-to-end / acceptance / user-journey test, a black-box test of a real deployment, or wants to prove a whole flow works through the real UI and API. Distinct from strict-tdd (in-process unit level) and from verification (final evidence-gathering). Not for pure internal refactors already covered by the existing acceptance suite."
---

# Acceptance Testing — the outer loop that proves the feature works

## Why this exists

Unit tests prove each piece behaves; they don't prove the assembled system does the thing a user came for. A feature can have a green unit suite and still fail the moment a real request crosses the real UI, the real API, and a real database — because the wiring, the deployment, the migrations, or an external integration was never exercised together. Acceptance testing closes that gap by driving the whole system, deployed as it will run in production, from the perspective of the user.

It is the **outer loop of double-loop TDD.** The acceptance test is written *up front* from the agreed acceptance criteria, watched failing, and left red while the inner `strict-tdd` cycle builds the increments. When the last increment lands and the acceptance test goes green, that green is the proof the feature works as a whole — not a hopeful inference from unit coverage.

## The double loop

```
OUTER (this skill):  write acceptance test from criteria → watch it FAIL (feature-level red)
                            │
                            ▼
  INNER (strict-tdd):  ┌─ red → green → commit → refactor → commit ─┐   per increment,
                       └───────────── repeat ──────────────────────┘   until the plan is done
                            │
                            ▼
OUTER:  acceptance test now PASSES against the real deployment → the feature is proven
```

The outer test does not replace the inner cycle and the inner cycle does not replace the outer test. Unit tests give fast, precise feedback on each piece; the acceptance test gives slow, holistic proof of the whole. You need both, and the outer test written first is what keeps the inner work aimed at a user-visible goal rather than at a pile of green units that don't add up.

## What an acceptance test is

- **Written from the user's perspective.** It reads as a user journey — the Given/When/Then acceptance criteria from `intake`, made executable. It asserts on outcomes the user can observe, never on internal calls or implementation structure.
- **End to end through the real interfaces.** For a user-facing feature it drives the **real UI and the real API together** (a browser/automation driver against the deployed frontend, which talks to the deployed backend). For a headless or service change, it drives the outermost interface the consumer actually uses — the public API, the CLI, the message it receives.
- **Against a production-like deployment.** The application runs the way it runs in production — the built artifacts, real configuration, real migrations applied — not an in-process harness. A **real database** backs it, running in a container or in an actually deployed environment. See `references/environment.md`.
- **Longer-running and separate.** These tests are slower than units by nature (they boot services, hit a database, drive a browser). Keep them in a **separate suite**, run explicitly — not on every save. They trade speed for the one thing units can't give: confidence the deployed whole works.

## Real services, and external fakes — never code-level doubles

This is where acceptance testing departs from `strict-tdd`'s doubles rule, and the distinction is sharp.

<HARD-GATE>
Acceptance tests run against **real services**. Where a real dependency genuinely cannot be used in the test environment (a paid third-party API, a partner system, something with no test tenancy), substitute an **external deployed fake** — a standalone fake of that service, running as its own process/container, that speaks the same protocol and is called exactly like the real one (a WireMock/Prism server, a LocalStack, a fake-gateway container, a sandbox instance).

Never substitute with a **code-level double** — an in-process mock, stub, or hand-written fake wired into the application under test. The whole point of an acceptance test is that the deployed application is byte-for-byte what ships; reaching inside it to swap a collaborator destroys that guarantee and lets integration bugs through.
</HARD-GATE>

Put plainly: `strict-tdd` asks *"can the real thing run deterministically in-process?"* and doubles the seam **in code** when it can't. Acceptance testing keeps the application untouched and moves the substitution **outside the process** — a real database in a container, and for the few dependencies you can't run for real, a deployed fake at the same network boundary the real service lives at. The application can't tell the difference, which is exactly the point. Full detail: `references/environment.md`.

## How to use it (the outer-loop procedure)

1. **Derive the acceptance test from the agreed criteria.** Take the Given/When/Then criteria from `intake` and write them as executable user-journey tests. One test per meaningful flow; assert only on user-observable outcomes.
2. **Stand up the production-like environment.** Compose the app, a real database, and any external fakes (see `references/environment.md`). Use the project's `acceptance_env` and `commands.acceptance` from `.craft.yml` (see `project-conventions`) — the `up`/`down` commands, the database engine, the external fakes — rather than inventing them. Apply real migrations. Confirm the app is reachable through its real interface.
3. **Watch the acceptance test FAIL.** Run it against the environment before the feature exists. It must fail for the right reason — the behavior is missing, not the harness is broken. A red you never saw is not a spec.
4. **Leave it red and hand off to the inner loop.** `strict-tdd` builds the increments from `planning`, each with its own unit red-green-refactor. The acceptance test stays red throughout — that's expected; it's the target.
5. **Drive it green.** As increments land, periodically re-run the acceptance test. When the feature is believed done, it must pass against the real deployment. That green is the feature-level proof.
6. **Keep it in the suite forever.** The acceptance test now guards this flow against regression. Later refactors that don't change the user flow are covered by it and need no new acceptance test.

## When to write one

- **User-facing feature or a change to a user flow** → write an acceptance test up front. This is the default for anything a user sees or does end to end.
- **A bug in a user flow** → the reproduction from `intake` becomes an acceptance-level failing test when the flow only reproduces end to end; drive it green the same way.
- **Pure internal refactor with no user-flow change** → no new acceptance test; the *existing* acceptance suite is what proves the refactor preserved behavior. If there's no acceptance test covering the flow you're refactoring, that gap is worth filling first.

## Relationship to the neighbors

- **`strict-tdd`** is the inner loop — in-process, unit level, real collaborators, doubles only at non-deterministic seams *in code*. Acceptance testing is the outer loop — out-of-process, system level, real deployment, fakes only *outside* the process. Different levels, both required.
- **`verification`** (phase 8) is the final evidence-gathering: it *runs* the acceptance suite (among the full test run and any manual flow) and records the observed output as proof of done. Acceptance testing *authors and owns* those tests up front; verification *executes and evidences* them at the end. They meet at the same green.
- **`intake`** supplies the criteria the acceptance test is built from — which is why intake writes them in Given/When/Then in the first place.

## Exit condition

A user-level acceptance test exists for each of the feature's flows, was watched failing before implementation, runs against a production-like deployment with a real database and external fakes (never code-level doubles), and now passes. The inner `strict-tdd` work is complete and both suites are green. Hand off to `self-review`.
