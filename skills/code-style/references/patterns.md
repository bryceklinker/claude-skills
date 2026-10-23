# Patterns

Patterns remove complexity when their signal is present and add it when it isn't. Start with the simplest form and move to a pattern when the code in front of you shows its signal — not because a second case might arrive someday.

## Inputs as data, handling separate — the default structure

Don't create `Service`, `Manager`, `Utility`, or `Helper` grab-bags; they grow one unrelated method at a time. Instead, each operation has:

- **Its input** — a plain, immutable value holding exactly what the operation needs. It maps directly to a request body, is trivial to build in a test, and can be logged or queued.
- **Its handling** — a dedicated unit that does the work and returns a `Result` or the data the caller needs.

The simplest form is the default: **a function that takes the input value.** Use a class only when the handler holds collaborators (repositories, a clock) that are injected once. Don't add a mediator, a base handler type, or a command bus unless the codebase already has one or something actually dispatches dynamically.

```typescript
export type ApplyPromo = { orderId: OrderId; code: string };

export const applyPromo = (orders: OrderRepository, clock: Clock) =>
  async (input: ApplyPromo): Promise<Result<Order>> => { /* ... */ };
```

```csharp
public record ApplyPromo(OrderId OrderId, string Code);

public class ApplyPromoHandler(IOrderRepository orders, IClock clock)
{
    public Task<Result<Order>> Handle(ApplyPromo input) { /* ... */ }
}
```

A message + handler pair (CQRS naming: `CreateOrderCommand` → `CreateOrderCommandHandler`) is one shape of this, fine where the codebase uses it. If you split reads from writes, a query never mutates; a write may return what the caller needs (the new id, the resulting state) rather than forcing a follow-up read.

## The rest, by signal

| Pattern | Signal | Not before |
|---------|--------|------------|
| **Factory** | The same `switch` on a kind appears in a second place | One switch in one place is fine |
| **Strategy** | Behavior varies by a runtime condition and you'd branch on it repeatedly | Two variants chosen once can be an `if` |
| **Builder** | A constructor has many optional parts or step-by-step assembly | A handful of required fields is a constructor or literal |
| **Repository** | The domain needs data from a store it shouldn't know about (a real I/O seam) | In-memory data the domain owns needs no port |
| **Unit of Work** | One operation mutates several aggregates that must persist atomically | A single save is already atomic |

Each pattern's cost is a concept a reader must learn and a file they must open. Pay it when the pattern removes more than that — the duplicated switch, the repeated branching, the unreadable construction — and inline it again (`refactoring`'s Inline Single-Use Abstraction) if the signal goes away.
