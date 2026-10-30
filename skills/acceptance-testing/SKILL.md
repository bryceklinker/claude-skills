---
name: acceptance-testing
description: "Use to drive a feature with an outer, user-level acceptance test against a production-like deployment — real UI and API together, a real database in a container or a deployed app, and real external services or external deployed fakes (never code-level doubles). The outer loop of double-loop TDD: write it up front from the agreed criteria, watch it fail, let the inner strict-tdd increments drive it green; its passing proves the feature works end to end. Trigger when a user-facing feature or user-flow change begins implementation, when someone asks for an end-to-end / acceptance / user-journey / black-box test of a real deployment, or when an end-to-end or CI run fails opaquely and the shared harness needs to capture logs, browser traces, videos, screenshots, or request/response detail. Distinct from strict-tdd (in-process unit level) and verification (final evidence). Not for internal refactors already covered by the acceptance suite, nor production observability."
---

# Acceptance Testing — the outer loop

Unit tests prove the pieces; an acceptance test proves the deployed whole does what the user came for. Written from the criteria before the feature exists, seen failing, and left red while `strict-tdd` builds the increments, its green is the proof the feature works end to end.

## What one is

- **A user journey.** The Given/When/Then criteria made executable, asserting only on what the user can observe — never internal calls or state.
- **Through the real interfaces.** For a user-facing feature, a browser driver against the deployed frontend talking to the deployed backend. For a headless change, the outermost interface the consumer uses: the public API, the CLI, the message it receives.
- **Against a production-like deployment.** The built artifact, real configuration, real migrations, the same database engine as production in a container or deployed environment.
- **A separate, slower suite** (`commands.acceptance`), run explicitly rather than on every save.

Write one test per meaningful flow, not per criterion permutation — the edge cases belong in the fast unit suite.

## Substitute outside the process, never inside

Use real services. Where one genuinely can't run in the test environment (a paid API, a partner system with no test tenancy), replace it with an **external deployed fake** — its own process or container, speaking the same protocol, reached by the same code path (WireMock, Prism, LocalStack, MailHog, a fake gateway container). Never wire an in-process mock or stub into the application: the point is that what you test is byte-for-byte what ships. `strict-tdd` substitutes inside the process; this loop substitutes outside it.

The environment declares an explicit, unique identity — a compose `name:`, a namespace, a workspace — and every teardown targets it by name, never an implicit default derived from the working directory. Details: `references/environment.md`.

## The procedure

1. Turn the criteria into user-journey tests.
2. Stand up the environment from `acceptance_env` in `.craft-code.yml`, with real migrations, and confirm the app is reachable and diagnostics are being captured.
3. Run the tests and confirm they fail because the feature is missing, not because the harness is broken.
4. Hand off to `strict-tdd`; the acceptance test stays red as increments land.
5. Re-run as the feature comes together; when it's believed done, it must pass against the real deployment.
6. Keep it in the suite as the flow's regression guard.

For a bug that only reproduces end to end, the reproduction becomes an acceptance-level failing test. For an internal refactor, the existing suite is the proof; if no acceptance test covers the flow, fill that gap first.

## Make failures legible before you need them

These tests fail where you can least reach — a removed container, an unwatched browser, a CI runner. Capture by default, in the shared fixture rather than per test: every service's logs collected before teardown, the browser trace, video, and screenshot, the failing request and response, and the commit and versions under test. A change that makes failures less legible is a regression. Details and CI wiring: `references/diagnosability.md`.

## Exit condition

Each of the feature's flows has an acceptance test that was seen failing, runs against a production-like deployment with no code-level doubles, and now passes; a failing run would leave the artifacts that explain it. Hand off to `adversarial-review`.
