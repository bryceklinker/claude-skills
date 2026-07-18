# Testing Doubles — where the boundary really is

## Table of contents
- The one question
- What a "double" is
- What is NOT a boundary (use the real thing)
- What IS a boundary (double it, or use a real substitute)
- Preferring real substitutes over mocks
- When something is hard to test without a double
- Worked examples

## The one question

Before introducing any test double, ask exactly one thing:

> **Can the real implementation run deterministically, in-process, inside this test?**

- **Yes** → use the real thing. This is the default and it covers the vast majority of dependencies, including third-party libraries.
- **No** → you're at a genuine boundary. Prefer a real lightweight substitute; fall back to a mock only when even that isn't practical.

Notice what the question is *not*: it is not "do I own this code?" Ownership is irrelevant. A real, in-process library you didn't write (`lodash`, `@mui/*`, MediatR, FluentValidation) runs deterministically, so you use it for real. A network call to a service you *do* own does not run deterministically in a unit test, so it's a boundary.

## What a "double" is

Any stand-in for a real collaborator: mock, stub, fake, spy, dummy. The problem they share is that they encode an *assumption* about how the collaborator behaves. When the assumption drifts from reality, the double keeps the test green while production breaks. Every double is a small bet that you understand the collaborator perfectly and forever. At the boundary that bet is worth making to buy determinism; everywhere else it's a liability.

## What is NOT a boundary (use the real thing)

Wire these up for real in tests, always:

- **Your own domain code, services, entities, value objects.** Test a unit through its real collaborators. If that's hard, the design is coupled — fix the design.
- **Real, in-process third-party libraries.** `lodash`, `date-fns`, `@mui/*` components, MediatR, FluentValidation, AutoMapper, mapping/validation/formatting libraries. They are deterministic in-process code. Doubling them means testing your mock of the library instead of your integration with it.
- **Pure computation** of any origin — parsers, formatters, calculators, mappers.
- **In-memory data structures**, collections, immutable models.

## What IS a boundary (double it, or use a real substitute)

Genuinely external or non-deterministic seams:

- **The network** — HTTP calls, gRPC, message brokers, third-party APIs over the wire.
- **The filesystem** — real disk reads/writes.
- **The system clock and calendar** — `now()`, timers, timeouts.
- **Randomness** — RNGs, UUID generation, when the value matters to the assertion.
- **A database or external service you don't control** — especially one requiring network or heavy setup.
- **The process boundary generally** — anything out-of-process, slow, flaky, or dependent on the outside world.

## Preferring real substitutes over mocks

Even at the boundary, a mock is the last resort, not the first. Reach for the most realistic thing that's still deterministic:

1. **A real lightweight implementation** — in-memory database, `tmpfs`/temp directory, a local test server. Highest fidelity; catches real integration bugs.
2. **A hand-written fake you own** — e.g. an in-memory implementation of a repository *port*. Lives behind your own interface at the boundary, behaves like the real thing, and is reused across tests.
3. **An injected deterministic value** — a fixed clock, a seeded RNG.
4. **A mock/stub of the interaction** — only when the above aren't practical. Keep it at the outermost seam, and assert on resulting behavior, not on call sequences, wherever you can.

This is why the architecture matters (`code-style/references/architecture.md`): with ports and adapters, the boundary is a small, explicit interface. You substitute the *adapter*, and everything inside — your domain plus all the real libraries it uses — runs for real.

## When something is hard to test without a double

That difficulty is a design message. Usual causes and fixes:

- **A domain object reaches out to the network/DB itself** → invert it. Depend on a port; inject the adapter. Now the domain is pure and testable with the real thing, and only the adapter needs a substitute.
- **A method constructs its own collaborators** (`new HttpClient()` inside) → pass them in. Construction-in-place is what forces mocking.
- **One unit does I/O and logic together** → split them. Pure logic tested for real; thin I/O adapter tested at the boundary.

Reaching for a mock to escape this pain hides the coupling instead of removing it. Fix the design; the test gets easy and stays honest.

## Worked examples

**Discount calculation using a money library** — the library is in-process and deterministic. Use it for real. A mock here would assert "we called `Money.multiply`," which is both fragile and pointless.

**A validator built with FluentValidation** — real, in-process. Construct the real validator, feed it real inputs, assert the real result. Never stub the validation library.

**A `PriceService` that calls a currency-rate HTTP API** — the HTTP call is the boundary. Put it behind a `RateProvider` port. In tests, use an in-memory `RateProvider` returning known rates. The `PriceService` and all its real-library dependencies run for real; only the wire call is substituted.

**Code that stamps records with the current time** — `now()` is non-deterministic. Inject a `Clock`; use a fixed clock in tests. Everything else runs for real.

**A repository backed by Postgres** — prefer a real Postgres (container) or an in-memory implementation of the repository port. A pile of mocks asserting query-builder calls tests the mock, not the persistence.
