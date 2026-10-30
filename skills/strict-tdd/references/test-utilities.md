# Test Utilities

Test code is real code and decays the same way. The goal is a test body that shows only what makes this case different: arrange the interesting thing, act, assert the outcome. Extract a utility when repetition actually appears — the same setup or assertion a third time — not in anticipation of it. A helper used once is indirection a reader has to chase.

## The patterns, and the signal for each

| Pattern | Reach for it when | Shape |
|---------|-------------------|-------|
| **Test Data Builder** | Many tests construct the same complex object, varying a field or two | `anOrder().withSubtotal(dollars(100)).build()` — defaults make a valid object; tests set only what matters |
| **Object Mother** | A few named archetypes recur across many tests | `aVipCustomer()` — back it with the builder rather than adding a mother per variation |
| **Custom assertion** | The same multi-line assertion recurs, or failures need domain language | `assertThatOrder(result).wasRejectedWith("Email required")` |
| **Fixture / harness** | Several tests assemble the same real object graph with only the boundary substituted | `world.checkout(order)`; build fresh state per test, never shared mutable state |
| **Boundary fake** | A port to the network/DB/clock is used across the suite | `InMemoryOrderRepository`, `FakeClock` — behind the production interface, faithful to the real adapter |

A plain object literal or a two-line local setup beats all of these when it's only needed once.

## Smells in test code

- **Mystery guest** — the test depends on data defined far away; bring what matters into the test.
- **Irrelevant detail** — fields that don't affect the case; push them into defaults.
- **Assertion roulette** — many bare assertions; on failure you can't tell which. Split, or use a custom assertion.
- **Logic in tests** — conditionals and loops hide bugs in the test itself; prefer straight-line or parameterized cases.
- **Redundant tests** — two tests that fail for exactly the same bug; keep the clearer one.
