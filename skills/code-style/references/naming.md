# Naming

Names are the primary documentation. Because comments are banned except to explain *why* awkward code exists, names carry the full weight of explaining *what* and *how*. Spend effort here.

## Table of contents
- Variables — nouns
- Functions — verbs
- Booleans — announce themselves
- Files — match contents
- Test names — Given / When / Then
- General rules

## Variables — nouns

A variable names a thing, so it's a noun or noun phrase: `order`, `remainingBalance`, `activeUsers`. Avoid meaningless names (`data`, `temp`, `obj`, `x`) and type-suffix noise (`orderObject`, `strName`). A collection is plural (`orders`), a single item singular (`order`). Prefer specific over generic: `unpaidInvoices` beats `list`.

## Functions — verbs

A function does something, so it starts with a verb: `calculateTotal`, `sendInvoice`, `parseAddress`, `loadOrders`. The name states the effect or the returned thing. A function named for a noun (`total()`) reads as a value; if it computes, name the computation (`calculateTotal()`) — or, if it's genuinely a cheap accessor, that's fine, but don't hide expensive work behind a noun.

Command functions (side effect) read as imperatives: `save`, `publish`, `retry`. Query functions (return a value, no side effect) read as questions or noun-returning verbs: `findOrder`, `getBalance`. A **query must never mutate**; a **command may return the data the caller needs** (a created id, a result). The naming still signals intent — an imperative name warns the reader that state changes, a noun/question name promises it doesn't.

For CQRS message/handler pairs (see `patterns.md`), name the handler after its message with a `Handler` suffix: `CreateOrderCommand` → `CreateOrderCommandHandler`; `GetOrderQuery` → `GetOrderQueryHandler`. The message is a noun phrase naming the operation's inputs; the handler's method is the verb (`Handle`/`handle`).

## Booleans — announce themselves

A boolean, or any function returning a boolean, must make its boolean nature obvious in the name via a predicate prefix:

- `is*` — `isActive`, `isEmpty`, `isExpired`
- `are*` — `areAllPaid`
- `has*` — `hasBalance`, `hasPermission`
- `should*` — `shouldRetry`, `shouldExpire`
- `does*` / `do*` — `doesQualify`
- `can*` — `canEdit`, `canShip`

`if (order.isPaid)` reads as English; `if (order.paid())` is ambiguous — is it a flag, a date, an action? The prefix removes the doubt. Avoid negatives in the name (`isNotReady`); prefer `isReady` and negate at the call site, so you never parse `!isNotReady`.

## Files — match contents

A file's name matches what's in it. A file defining `OrderValidator` is `OrderValidator.<ext>` (or the project's cased convention, e.g. `order-validator.ts`). One primary export per file is the default; when a file's name no longer describes its contents, that's a signal the file has grown a second responsibility — split it. Folder names describe the feature (see `architecture.md`), not the layer.

## Test names — Given / When / Then

Test names are specifications. Use **Given / When / Then** with this structure:

- **Given** — the preconditions. **Zero to many.** Omit entirely when there's no meaningful setup; chain several when multiple conditions define the case.
- **When** — the trigger or action. **Exactly one.** A test exercises a single action; if you find yourself writing two Whens, you have two tests.
- **Then** — the observable outcomes. **One to many.** A single action often has several checkable consequences; assert each relevant one.

```
When placing an order over $100, then free shipping is applied
Given a VIP customer and an empty cart, when checkout is opened, then it is blocked and a prompt to add items is shown
Given a promo code that has expired, when it is applied, then the order total is unchanged and a failure naming "expired" is returned
```

- One **When** per test keeps each test pinned to a single behavior — the thing `strict-tdd` drives one at a time.
- Multiple **Thens** are fine when they're facets of the same outcome; if they're really unrelated behaviors, that's a hint to split.
- Name the *behavior*, never the method (`whenChargeCalled_itWorks` says nothing). A reader should understand the requirement from the name without reading the body.
- Adapt the surface syntax to the framework (a `describe/it` block, an underscore-joined method name, an attribute string) but keep the Given/When/Then structure intact.

## General rules

- **Consistency beats cleverness.** One term per concept across the codebase — don't call it `customer` here and `client` there for the same thing.
- **Length scales with scope.** A loop index living for two lines can be short; a field on a widely-used type earns a full, descriptive name.
- **No encodings.** No Hungarian notation, no `I`-prefixed interfaces unless the language community strongly expects it, no `_`-prefixed privates unless idiomatic to the language.
- **Reveal intent, not implementation.** `eligibleCustomers` beats `filteredList` — the reader wants to know what they are, not how they were produced.
