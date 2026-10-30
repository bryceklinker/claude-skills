# Testing Doubles — where the boundary really is

## The one question

> **Can the real implementation run deterministically, in-process, inside this test?**

- **Yes** → use it. This covers your own code and real third-party libraries (`lodash`, `date-fns`, `@mui/*`, MediatR, FluentValidation, mapping and money libraries), pure computation, and in-memory data structures.
- **No** → you're at a genuine boundary: the network, filesystem, system clock, randomness that matters to the assertion, a database or service you don't control, anything out-of-process.

Ownership is irrelevant. A library you didn't write runs deterministically, so it's real; a network call to a service you own does not, so it's a boundary.

## At the boundary, prefer the most realistic deterministic option

1. A real lightweight implementation — temp directory, local test server, in-memory database.
2. A hand-written fake behind your own port — `InMemoryOrderRepository`, reused across tests.
3. An injected deterministic value — fixed clock, seeded RNG.
4. A mock of the interaction — last resort; keep it at the outermost seam and assert on outcomes, not call sequences.

Every double is a bet that you understand the collaborator perfectly. At the boundary that bet buys determinism; anywhere else it's a test that passes while the real integration breaks, and that shatters on every refactor.

## When it's hard to test without a double

That's a design message, not a reason to mock:

- Domain code reaching out to I/O itself → depend on a port; inject the adapter.
- A method constructing its own collaborators (`new HttpClient()` inside) → pass them in.
- One unit doing I/O and logic together → split them; test the logic for real.

## Examples

- **Discount using a money library** — real library. A mock would assert "we called `Money.multiply`."
- **`PriceService` calling a currency-rate API** — the HTTP call is the boundary: a `RateProvider` port with an in-memory implementation in tests; everything else real.
- **Records stamped with `now()`** — inject a clock; fixed clock in tests.
- **Postgres repository** — real Postgres in a container, or an in-memory implementation of the port. Never a pile of query-builder mocks.
