# Architecture

The organizing idea: **the core domain logic is independent of how data enters or leaves the system.** HTTP, GraphQL, gRPC, the database, the message queue — these are details at the edge. The domain in the center knows nothing about them. This is Clean Architecture / Ports and Adapters / Hexagonal — the same idea under three names.

## Table of contents
- Dependency inversion — the central rule
- Ports and adapters
- The dependency direction
- Feature-oriented organization
- Shared code
- Result types (failure as a value)
- Null objects
- Consistent data structures across boundaries

## Dependency inversion — the central rule

Dependencies point *inward*, toward the domain, never outward. The domain defines interfaces (ports) for what it needs — "give me the order with this id", "charge this card" — and the outer layers implement them. The domain depends on the abstraction; the infrastructure depends on the domain. It is never the other way around.

Concretely: a domain service does not `import` an HTTP client or an ORM entity. It declares a port and receives an implementation injected from outside. This is what makes the domain testable with real collaborators and boundary fakes (see `strict-tdd/references/testing-doubles.md`) — the only thing you substitute in a test is an adapter.

## Ports and adapters

- **Port** — an interface owned by the domain, expressing a need in domain terms (`OrderRepository`, `PaymentGateway`, `Clock`).
- **Adapter** — an implementation of a port living at the edge (`PostgresOrderRepository`, `StripePaymentGateway`, `SystemClock`).
- **Driving side** (inputs): controllers, message handlers, CLI — they call *into* the domain.
- **Driven side** (outputs): repositories, gateways, clocks — the domain calls *out* through ports to reach them.

The domain is a hexagon in the middle; every external concern plugs in through a port at the edge.

## The dependency direction

```
   HTTP / GraphQL / gRPC / CLI  (driving adapters)
                 |  calls into
                 v
        Application / Use cases
                 |  depends on
                 v
            Domain (entities, value objects, ports)   <-- knows nothing outward
                 ^  implements ports
                 |
   DB / queue / external services  (driven adapters)
```

Everything points at the domain. The domain points at nothing external.

## Feature-oriented organization

Organize folders by **feature**, not by technical layer. Prefer:

```
src/
  checkout/          # a feature — everything checkout owns
    domain/
    application/
    adapters/
  promotions/
    domain/
    application/
    adapters/
  shared/
```

over the layer-first alternative (`controllers/`, `services/`, `repositories/`, `models/`) where one feature is smeared across every folder. Feature folders keep related code together, make a feature's boundaries visible, and let you delete or extract a feature cleanly. Inside a feature, the clean-architecture layers still apply.

## Shared code

Code shared by **more than one feature** goes in a `shared` directory/package. The bar is genuine reuse across features — don't pre-emptively hoist things into `shared` "in case." A single feature's helper stays inside that feature until a second feature actually needs it. Shared code should be stable and dependency-light, since many features lean on it.

## Result types (failure as a value)

Expected failure is a returned value, not an exception (see the core rule in SKILL.md). A result carries either success with a value, or failure with a named reason:

```
type Result<T> =
  | { ok: true;  value: T }
  | { ok: false; error: FailureReason }
```

- The signature advertises that the call can fail, so callers can't forget to handle it.
- The failure reason is domain data (an enum/union naming *why*), not a string to parse.
- Reserve thrown exceptions for the genuinely unrecoverable — programmer errors, corrupted invariants — not for outcomes the caller is expected to handle. Use your language's idiom where one exists (a result/either type, an option), but keep the principle.

## Null objects

Rather than returning null and forcing every caller to guard, return a **null object** — a real instance of the type whose behavior is the safe "nothing" case: a `NoDiscount` that subtracts zero, an `AnonymousUser` with no permissions, an empty collection. Callers treat it uniformly; the null check disappears because there's nothing null to check. Where an absence must cross a boundary, use an explicit optional at that boundary and resolve it (to a null object or a handled failure) before it reaches the domain.

Never paper over an absence with a **non-null assertion / null-forgiving operator** (`x!` in TypeScript, `!` in C#, force-unwraps, non-null casts). It suppresses the compiler's nullability check without eliminating the null, so a wrong assumption becomes a runtime crash instead of a caught type error. When the type system says a value may be absent, honor it: narrow it with a guard, resolve it to a null object, return a failure, or model the field as non-nullable at construction so the absence never exists. See the smell entry in `smells.md` for the fixes in detail.

## Consistent data structures across boundaries

Define common domain data structures and let the externally-facing interfaces (HTTP DTOs, GraphQL types, gRPC messages) mirror them closely. When the wire shapes track the domain shapes, mapping stays trivial and mechanical; when they drift apart arbitrarily, every boundary becomes a translation layer that hides bugs. Keep a single vocabulary of types from the domain outward, adapting only where a protocol genuinely demands it.
