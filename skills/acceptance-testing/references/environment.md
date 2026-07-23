# The Acceptance Environment — production-like, real services, external fakes

An acceptance test is only as trustworthy as the environment it runs against. The goal is a deployment that is **indistinguishable from production to the application itself**: the same built artifacts, the same configuration mechanism, a real database, real migrations, and real network boundaries. The application under test is never modified for the test — everything you substitute lives *outside* it.

## Table of contents
- The application: run what ships
- The database: real, in a container or deployed
- External dependencies: real, or an external deployed fake
- What "external deployed fake" means (and what it is not)
- Data setup and isolation
- Driving the system through its real interface
- Where these tests run

## The application: run what ships

Boot the actual build — the compiled/bundled artifact, started the way production starts it, reading configuration the way production reads it (environment variables, config files, secrets). Do **not** spin up an in-process test host that bypasses the real entry point, and do **not** compile the app in a special "test mode" that swaps components. If production runs a container image, run that image. The acceptance test's value comes entirely from the app being byte-for-byte what deploys.

## The database: real, in a container or deployed

Use the **same database engine as production** (same Postgres/SQL Server/Mongo version), backed by real storage:

- **A container** is the common case — spin up the real engine (e.g. via Docker Compose or a Testcontainers-style harness), apply the real migrations, and point the app at it. This gives production-fidelity persistence with disposable, reproducible state.
- **A deployed instance** — for tests running against a real staging/ephemeral deployment, use its provisioned database.

Never substitute an in-memory or different database (SQLite standing in for Postgres, an ORM's in-memory provider). Those hide exactly the migration, dialect, transaction, and constraint bugs acceptance tests exist to catch.

## External dependencies: real, or an external deployed fake

Prefer the **real external service** wherever it can be used — a sandbox/test tenancy of the payment gateway, a test instance of the identity provider, the real message broker in a container. That's the highest fidelity.

Where a real dependency genuinely can't run in the environment — it costs money per call, has no test tenancy, is a partner system you can't provision, or is non-deterministic in a way that breaks the test — replace it with an **external deployed fake**, not a code change.

## What "external deployed fake" means (and what it is not)

An external deployed fake is a **standalone service** that stands in for the real one at the same network boundary:

- It runs as **its own process/container**, separate from the application under test.
- It speaks the **same protocol/contract** — same HTTP endpoints, same gRPC service, same message schema — so the application calls it with the *same code path* it uses for the real service. The app is not aware it's a fake.
- Examples: WireMock or Prism serving a stubbed HTTP API, LocalStack standing in for AWS, a hand-built "fake payment gateway" container, a mock SMTP server (MailHog), a fake OIDC provider.

Contrast with a **code-level double**, which is banned here: an in-process mock/stub/fake wired into the app's own object graph (an `ISomethingGateway` swapped for a test implementation in the DI container, a `jest.mock`, a hand fake injected into the app). That changes the running application, so the deployment you tested is not the deployment that ships. Code-level doubles are the right tool one level down, in `strict-tdd` — see `strict-tdd/references/testing-doubles.md` — and the wrong tool here.

The line: **`strict-tdd` substitutes inside the process; acceptance testing substitutes outside it.** In the acceptance environment the application is untouched; only its external neighbors are stand-ins, and they're stand-ins the app reaches over the wire exactly as it would the real thing.

## Data setup and isolation

- **Set up state through the real interface where you can** — create the account by calling the real signup API, not by inserting rows — so the setup exercises real code paths too. Fall back to seeding the real database directly only when driving the UI/API for setup is impractical.
- **Isolate tests** so they don't contaminate each other: a fresh database per run (disposable container), transactional rollback, or per-test namespacing of data. Flaky order-dependent acceptance tests erode the trust the suite exists to build.
- **Reset external fakes** between tests the same way you reset the database — clear their recorded interactions and reprogram their responses per scenario.

## Driving the system through its real interface

- **User-facing feature:** drive the **real UI** with a browser automation driver (Playwright, Cypress, Selenium) against the deployed frontend, which talks to the deployed backend and real database. Assert on what the user sees. This is the fullest fidelity — it covers the UI, the API, and the integration between them in one flow.
- **Headless/service change:** drive the outermost interface the consumer uses — call the public HTTP/gRPC API, run the CLI, or publish the message the system consumes — and assert on the observable result (response, emitted event, persisted state visible through the API).

Either way, assert on **user-observable outcomes**, never on internal state or call sequences. If a test needs to peek at internals to know whether it passed, it's testing implementation, not acceptance.

## Where these tests run

Because they boot services and a database, acceptance tests are slower and heavier than units. Keep them in a **separate suite** with its own command, run explicitly — in CI on a pipeline stage that provisions the environment, and on demand locally (a `docker compose up` plus a test command). They are not part of the fast inner-loop feedback; they're the gate that the deployed whole actually works.
