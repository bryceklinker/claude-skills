# Patterns

The patterns worth reaching for in this codebase, and the signal that calls for each. Most patterns are tools you apply when their signal appears — but **separating a behavior's inputs from its handling is different: it's the default structure for application logic, adopted up front, not a remedy applied later.** The rest are applied when their signal shows up; a pattern used without its signal is just ceremony.

## Table of contents
- Separate inputs from behavior — the default structure for application logic
- Factory — creating simple data structures / dispatching on type
- Builder — creating complex data structures
- Strategy — swapping an algorithm at runtime
- Repository — abstracting where data lives
- Unit of Work — one atomic save

## Separate inputs from behavior — the default structure for application logic

**This is how application logic is organized by default: separate *what* from *how*.** Do not create `Service`, `Manager`, `Utility`, `Helper`, or similarly-named grab-bag classes. They start small and always grow — every new bit of behavior gets one more method until the class is an unbounded pile with a dozen reasons to change. Head that off structurally by splitting every operation into two parts:

- **The inputs — the *what*.** An **immutable data object that captures exactly the data the behavior needs to run** — nothing more. No dependencies, no behavior.
- **The handling — the *how*.** A **separate, dedicated unit** (a class or function), one per behavior, that holds the collaborators and does the work. It takes the input data and returns a `Result` or the data the caller needs.

This separation — inputs are data, handling is a distinct unit — **is the rule**. Don't collapse the two into one class that both carries the inputs and does the work, and don't let a single class accumulate many unrelated operations. The input object is a plain, serializable record of "what was asked"; the handler is where collaborators are injected and the operation executes.

### One common shape: message + handler (Command/Query)

A widely used way to express this separation is a **message + handler** pair — often called CQRS. The message is the input data; the handler runs it. This is a good default *shape*, but it's one instantiation of the rule above, not the only acceptable one.

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

Under this naming, a *Command* names a state change (`CreateOrderCommand` → `CreateOrderCommandHandler`) and a *Query* names a read (`GetOrderQuery` → `GetOrderQueryHandler`, `handle(query): Promise<OrderSummary>`). The handler may be a plain function rather than a class where there's no ceremony to justify one. **Other shapes honor the same separation equally well** — a use-case/interactor taking a request object, a pure function taking a parameter object and returning a result. Pick the shape that fits; what's non-negotiable is that the inputs are a data object and the handling is a separate unit. The Command/Query names are a convenience, not a requirement.

### Why separate what from how
- **One behavior, one input type, one handler, one reason to change.** Each handler does exactly one thing, so nothing becomes the sprawling class you'd later have to break up. You prevent the growth instead of untangling it.
- **The input is a clean boundary object.** Because it's just data, it maps directly to an HTTP/GraphQL/gRPC request body, is trivial to construct in tests, and can be logged, queued, or dispatched (e.g. via a mediator) without dragging dependencies along.
- **Intent stays legible.** The handler's name and its single input announce what the operation is; you never hunt through a `Manager` to find which of twenty methods you meant.

**Splitting reads from writes (the CQRS discipline) is a worthwhile *additional* separation when it fits** — a read-only operation and a mutating one have different scaling, caching, and validation needs. Where you adopt it, keep the rule firm: **a query must never mutate.** A write handler, on the other hand, may return the data the caller genuinely needs — the id of a created entity, the resulting state, a `Result` carrying success or a named failure. Forcing every write to return nothing (and making callers issue a follow-up read for the id they just created) adds round-trips for no benefit. The rule is *return what the caller needs, nothing gratuitous* — not *return nothing*. Keep the return value purposeful and small; don't let a write handler double as a general read endpoint.

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

It keeps transaction boundaries explicit and out of the domain logic, and ensures a partial failure doesn't leave half-written state. A write handler is the natural home for a Unit of Work — a handler that mutates multiple aggregates wraps them in one.
