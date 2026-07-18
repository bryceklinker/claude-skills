# Patterns

The patterns worth reaching for in this codebase, and the signal that calls for each. Most patterns are tools you apply when their signal appears — but **CQRS is different: it's the default structure for application logic, adopted up front, not a remedy applied later.** The rest are applied when their signal shows up; a pattern used without its signal is just ceremony.

## Table of contents
- CQRS — the default structure for application logic
- Factory — creating simple data structures / dispatching on type
- Builder — creating complex data structures
- Strategy — swapping an algorithm at runtime
- Repository — abstracting where data lives
- Unit of Work — one atomic save

## CQRS — the default structure for application logic

**This is how application logic is organized by default.** Do not create `Service` or `Manager` classes. They start small and always grow — every new bit of behavior gets one more method until the class is an unbounded grab-bag with a dozen reasons to change. Head that off structurally: express each operation as a **message** plus a dedicated **handler**.

### Message + handler — the shape

Separate the *inputs* of an operation from the *logic* that runs it:

- **The message** (Command or Query) is an **immutable data object that captures the inputs** — nothing more. No dependencies, no behavior. A Command names a state change (`CreateOrderCommand`); a Query names a read (`GetOrderQuery`).
- **The handler** is a **dedicated class or function, one per message**, that holds the dependencies and does the work: `CreateOrderCommandHandler` handles `CreateOrderCommand`. It takes the message and returns a `Result` (for commands) or the data (for queries).

This message/handler split is the key structural rule: the message is a plain, serializable record of "what was asked"; the handler is where collaborators are injected and the operation executes. Don't collapse them into one class that both carries inputs and does the work.

**C#:**
```csharp
public record CreateOrderCommand(CustomerId Customer, IReadOnlyList<OrderLine> Lines, string? PromoCode);

public class CreateOrderCommandHandler
{
    public CreateOrderCommandHandler(/* injected dependencies: repositories, clock, ... */) { }

    public async Task<Result<Guid>> Handle(CreateOrderCommand command)
    {
        // validation, domain logic, persistence — then return the new order id
    }
}
```

**TypeScript:**
```typescript
export type CreateOrderCommand = {
  customerId: string;
  lines: OrderLine[];
  promoCode?: string;
};

export class CreateOrderCommandHandler {
  constructor(/* injected dependencies */) {}

  async handle(command: CreateOrderCommand): Promise<Result<OrderId>> {
    // validation, domain logic, persistence — then return the new order id
  }
}
```

A query mirrors this: `GetOrderQuery` (the message) + `GetOrderQueryHandler` with `handle(query): Promise<OrderSummary>`. A handler may be a plain function instead of a class where there's no ceremony to justify one — the message/handler separation is what matters, not whether the handler is a class.

### Why this is the default rather than a fix-it
- **One operation, one message, one handler, one reason to change.** Each handler does exactly one thing, so nothing becomes the sprawling class you'd later have to break up. You prevent the growth instead of untangling it.
- **Read/write intent is explicit.** A Command message means "this mutates"; a Query message means "this only reads." The intent is visible at the call site and in the type.
- **The message is a clean boundary object.** Because it's just data, it maps directly to an HTTP/GraphQL/gRPC request body, is trivial to construct in tests, and can be logged, queued, or dispatched (e.g. via a mediator) without dragging dependencies along.
- **Reads and writes evolve independently** — different scaling, caching, and validation needs, cleanly separated.

**Commands may return data.** A query must never mutate — that separation is firm. But a command handler is allowed to return the data the caller genuinely needs: the id of a created entity, the resulting state, a `Result` carrying success or a named failure. Forcing every command to return nothing (and making callers issue a follow-up query for the id they just created) adds round-trips and complexity for no benefit. The rule is *return what the caller needs, nothing gratuitous* — not *return nothing*. Keep the return value purposeful and small; don't let a command handler double as a general read endpoint.

## Factory

**Use for:** creating simple data structures, and for replacing a repeated `switch`/`if-else` that branches on a type or kind. When you see the same `switch (kind)` in more than one place, that's the signal — centralize construction in a factory so the branching lives in exactly one spot.

```
createNotification(kind) -> Notification
// the ONE place that knows kind -> concrete type
```

A factory turns scattered type-branching into a single mapping, so adding a new kind touches one function instead of every switch. See the smell "duplicated switch/if-else" in `smells.md` — the factory is its usual cure.

## Builder

**Use for:** creating complex data structures — many fields, optional parts, validation during assembly, or step-by-step construction. Where a factory is a single call, a builder accumulates configuration fluently and produces the object at the end.

```
anOrder()
  .withCustomer(customer)
  .withLine(item, quantity)
  .withPromoCode("SAVE10")
  .build()
```

Builders keep construction readable, make optional fields explicit, and pair directly with the Test Data Builder pattern (`strict-tdd/references/test-utilities.md`). Reach for a builder when a constructor grows past a handful of parameters or sprouts many overloads.

## Strategy

**Use for:** selecting an algorithm at runtime. When behavior needs to vary by a runtime condition and you'd otherwise branch on it repeatedly, encapsulate each variant behind a common interface and inject the chosen one.

```
interface ShippingCost { calculate(order): Money }
// StandardShipping, FreeShipping, ExpressShipping
```

Strategy removes runtime `if`/`switch` chains over "which algorithm" and makes each variant independently testable. Often paired with a factory that picks the strategy from input.

## Repository

**Use for:** abstracting where data comes from — database, HTTP service, in-memory, cache. A repository is a driven-side port (see `architecture.md`): the domain asks for and stores aggregates in domain terms, ignorant of the backing store.

```
interface OrderRepository {
  findById(id): Order
  save(order): void
}
```

This is what lets tests use an in-memory implementation of the port instead of doubling a database, and lets the storage technology change without touching the domain.

## Unit of Work

**Use for:** making a set of changes commit as one atomic operation. When a use case mutates several aggregates and they must all persist together or not at all, a Unit of Work tracks the changes and commits (or rolls back) as a single transaction.

```
unitOfWork.begin()
// ... domain operations across repositories ...
unitOfWork.commit()   // all-or-nothing
```

It keeps transaction boundaries explicit and out of the domain logic, and ensures a partial failure doesn't leave half-written state. Command handlers are the natural home for a Unit of Work — a handler that mutates multiple aggregates wraps them in one.
