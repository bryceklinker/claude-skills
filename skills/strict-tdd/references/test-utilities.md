# Test Utilities — make each new test cheap to write

Test code is real code. It deserves the same design effort as production, and it pays that effort back: a suite with a good utility vocabulary makes every new test short, readable, and focused on the one behavior it's about. This file catalogs the patterns (drawn largely from Meszaros' *xUnit Test Patterns*) and when to reach for each.

## Table of contents
- The goal: intention-revealing tests
- Test Data Builder
- Object Mother
- Custom assertions / matchers
- Fixtures and setup helpers
- Fakes at the boundary
- Refactoring test code
- Smells in test code

## The goal: intention-revealing tests

A good test reads as: arrange the interesting thing, act, assert the outcome. The noise — constructing valid-but-irrelevant objects, wiring collaborators, repeating assertions — should be factored into utilities so the test body shows only what makes *this* case different. If a reader can't tell in five seconds what behavior a test pins down, the setup is drowning the intent.

## Test Data Builder

For constructing complex objects with sensible defaults and only the fields relevant to the test made explicit. This is the workhorse; prefer it for anything with more than a couple of fields.

```
val order = anOrder()
    .withSubtotal(dollars(100))
    .withPromoCode("SAVE10")
    .build()
```

- Defaults produce a valid object, so tests set only what matters.
- Fluent `withX` methods make the salient values jump out.
- Builders compose (`withCustomer(aCustomer().vip())`).
- Pairs naturally with the Builder pattern in production code (`code-style/references/patterns.md`).

## Object Mother

Named factory methods for canonical example objects: `aVipCustomer()`, `anExpiredCard()`, `anEmptyCart()`. Reach for these when a few well-known archetypes recur across many tests.

- Great for readability of common cases.
- Can rigidify if overused — when a test needs a slight variation, don't add a mother per permutation. Back the mothers with builders: `aVipCustomer()` returns `aCustomer().vip().build()`, and a test needing a tweak uses the builder directly.

## Custom assertions / matchers

When the same multi-line assertion recurs, or a failure message would be clearer in domain terms, extract a custom assertion:

```
assertThatOrder(result).wasRejectedWith("Email required")
```

- One call expresses the intended outcome; the matcher owns the detail.
- Failure messages speak the domain ("expected order rejected with 'Email required', but it was accepted") instead of raw field diffs.
- Keeps the assert step of each test to one intention-revealing line.

## Fixtures and setup helpers

Shared, deterministic starting state — a seeded in-memory repository, a wired-up system-under-test with real collaborators and boundary fakes injected. Prefer **fresh fixtures per test** (build the state each time) over shared mutable fixtures that leak state between tests and cause order-dependent flakiness.

A common shape is a small "test harness" or "world" helper that assembles the real object graph with only the boundary substituted, so each test says `world.checkout(order)` and asserts on `world`.

## Fakes at the boundary

Hand-written in-memory implementations of your boundary ports (an `InMemoryOrderRepository`, a `FakeClock`, a `FakeRateProvider`) are reusable test utilities in their own right. Build them once, behind the same interface production uses, and share them across the suite. See `testing-doubles.md` for why these beat mocks. Keep their behavior faithful to the real adapter — a fake that lies is worse than no test.

## Refactoring test code

Every REFACTOR step includes the tests. Watch for:
- The same object hand-constructed in many tests → extract a builder.
- The same arrange block repeated → extract a fixture/harness helper.
- The same assertion block repeated → extract a custom assertion.
- A test that needs extensive comments to explain its setup → the setup wants a named helper that makes the comment unnecessary.

Do this while green, and keep the suite green — refactoring tests is behavior-preserving on the production side.

## Smells in test code

- **Mystery guest** — the test depends on data defined far away (a shared file, a giant fixture) so you can't see why it passes. Bring the relevant data into the test via a builder.
- **Irrelevant detail** — setting fields that don't matter to the case. Push them into builder defaults.
- **Assertion roulette** — many bare assertions with no messages; on failure you can't tell which blew up. Use custom assertions or split the test.
- **Fragile setup** — every test breaks when one constructor changes. Centralize construction in builders/mothers.
- **Test logic** — conditionals and loops in tests. They hide bugs in the test itself; prefer straight-line, parameterized cases.
