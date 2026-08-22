# Diagnosability — what a failing acceptance run must tell you

An acceptance failure happens in the least reachable place you have: a container that is about to be deleted, a browser nobody watched, a CI runner you can't attach to. Whatever the run didn't capture is gone. This file is the checklist for making sure the first failing run is enough — the standard being *a reviewer who wasn't there can say what broke from the artifacts alone.*

## The four layers

**1. Application logs, from every service.** Not just the service under test — the API, the worker, the database's error log, the external fakes. Most acceptance failures are one service refusing another, and you can only see that from both sides. Capture at a level that's actually useful under failure (debug for the app under test is usually right; acceptance runs are not the place to economize on log volume), and make sure they **outlive teardown** — write to a mounted volume or collect them before the environment comes down, never `docker logs` a container that's already removed.

**2. The browser record**, for UI journeys. Whatever the driver offers, turned on for the run rather than for a retry: a trace (Playwright's trace has the DOM snapshots, network, and console together and is the single highest-value artifact), a video of the session, and a screenshot at the moment of failure. Console errors and page errors are worth failing on in their own right — an unhandled rejection in the page is a real defect even when the assertion passed.

**3. The failing interaction.** The request and its response, the query, the message that wasn't consumed — with enough of the payload to be actionable and secrets redacted. When the assertion is "the item appears in the list," the answer is nearly always in whether the write actually returned 200.

**4. Run identity.** The commit under test, image tags or versions, and the seed/ordering if the suite randomizes. This is what turns "flaky" into "fails only on this version of that dependency."

## Where it lives, and why that matters

Centralize it. The base class, the fixture, the harness — one place that every test inherits.

Per-test opt-in fails in a specific way: coverage decays silently as tests are added, and the test that finally fails is statistically the one nobody instrumented. Centralizing also means diagnosability can't be "forgotten" in a hurry — nobody has to remember it.

The corollary is that it must be **on by default in CI, not behind a flag.** If the workflow is "it failed, re-run with tracing enabled," you have already paid the round-trip this exists to prevent — and for a flaky failure, the re-run may not reproduce at all, which is exactly when you needed the artifact most.

Cost is the usual objection. Trace-on-first-retry and video-on-failure keep the price of a green run near zero while keeping a failing run fully legible; that's a reasonable middle. What is not reasonable is a green-only pipeline that captures nothing.

## Wiring it into CI

- **Upload artifacts on failure — and `if: always()`**, or a cancelled/timed-out job (the interesting one) leaves nothing behind.
- **Name and scope the artifacts** per job and per attempt, so a re-run doesn't overwrite the evidence from the run you were investigating.
- **Fail loudly on infrastructure problems.** A missing token, an image that didn't build, a service that never became healthy should fail with the reason, not surface as forty assertion errors.
- **Keep the retention long enough to matter** — an artifact expiring before someone reads it is the same as not capturing it.

## Record it in the project's conventions

The concrete paths, flags, and commands belong in `.craft-code.yml` under `diagnostics` (see `craft-code-conventions/references/schema.md`), not in this skill and not rediscovered per feature — so the next person's harness captures the same things without re-deriving them.

## Treat lost diagnosability as a regression

If a change makes failures *less* legible, that is a defect, not a tidy-up:

- teardown that removes containers before logs are collected,
- a retry wrapper that reports only the last attempt,
- swallowing a service's stderr to quiet the CI output,
- lowering the log level to make a run faster,
- an assertion helper that reports `false` instead of the value it saw.

A wording check that catches this: if a change description says it *restores* diagnosability, something removed it earlier and nothing noticed — worth asking what else went with it.

## Related

The runtime half of this question — what the *deployed* system reveals when it breaks in production — is craft-ops' `observability-design` domain (SLOs, symptom-based alerting, health signals). This file covers only what a test run must reveal. Both answer the same principle: a failure you can't see is a defect.
