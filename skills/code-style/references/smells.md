# Smells

A smell is a surface symptom of a deeper design problem. None is automatically a bug, but each is a prompt to look closer and usually to refactor. This is the checklist `self-review` runs the diff against, and the list to keep in mind during every `strict-tdd` refactor step. Each entry names the smell, why it hurts, and the refactoring that resolves it.

## Table of contents
- Long method (> 10 lines)
- Large class
- Duplicate code
- Law of Demeter violations
- Data classes
- Duplicated switch / if-else
- Sprawling control flow
- Long loop bodies
- Mutable state
- Comments that explain *what*
- Nulls
- Non-null assertions (null-forgiving operator)

## Long method (> 10 lines)

**Smell:** a method longer than ~10 lines. **Why it hurts:** length almost always means the method is doing more than one thing, so it can't be named for a single purpose and can't be understood at a glance. **Fix:** Extract Method until each does one thing at one level of abstraction. The top-level method should read like a short list of named steps. Ten lines is a prompt to look, not a hard trip-wire — but a method well past it is doing too much.

## Large class

**Smell:** a class with many fields/methods and several unrelated reasons to change — classically a `Service`, `Manager`, or `Utility`. **Why it hurts:** it violates single responsibility, becomes a merge magnet, and grows without bound. **Fix:** this is exactly what separating inputs from handling prevents — split the responsibilities into focused operations, each an input data object plus its own handler (`patterns.md`). Don't refactor a `Manager` into a slightly smaller `Manager`; decompose it into operations.

## Duplicate code

**Smell:** the same logic in more than one place. **Why it hurts:** every copy must change together, and one always gets missed. **Fix:** extract the shared logic to one home — a function, a strategy, a factory. Distinguish true duplication (same reason to change) from incidental similarity (looks alike today, will diverge) — only unify the former, or you couple things that should move apart.

## Law of Demeter violations

**Smell:** train-wreck navigation — `order.getCustomer().getAddress().getCountry().getCode()`. Talking to a stranger reached through a chain of intermediaries. **Why it hurts:** the caller is coupled to the entire object graph's shape; any change along the chain breaks it. **Fix:** tell, don't ask — put the behavior on the object that owns the data (`order.shippingCountryCode()`), so callers talk only to their immediate collaborators. This keeps knowledge where the data is.

## Data classes

**Smell:** a class that is only fields plus getters/setters, with all the behavior that operates on it living elsewhere. **Why it hurts:** it's the anemic-domain trap — data and the logic over it drift apart, the logic gets duplicated across the places that reach into the data, and Law of Demeter violations multiply. **Fix:** move the behavior onto the data. Ask what operations belong with these fields and give the type real methods. (Immutable value objects with meaningful behavior are the goal; a pure data bag is the smell.) Genuine DTOs at the boundary are the deliberate exception — they carry data across a seam and legitimately have no behavior.

## Duplicated switch / if-else

**Smell:** the same `switch (kind)` or `if-else` ladder over a type/kind appearing in more than one place. **Why it hurts:** adding a new case means finding and editing every copy, and one is always forgotten. **Fix:** isolate the branching to a single location — a factory that maps kind → object (`patterns.md`), or a strategy selected once. Prefer polymorphism over repeated type-branching. A switch that exists in exactly one place (e.g. inside a factory) is fine; it's the *duplication* that's the smell.

## Sprawling control flow

**Smell:** `if`/`else` and `switch` written as multi-line blocks with logic inside each branch; nested conditionals forming a pyramid. **Why it hurts:** branch bodies hide behavior and deepen nesting until the method's flow is unreadable. **Fix:** each branch should be a **single-line return**. Use guard clauses that return early instead of nesting; push the work inside a branch into a named function so the branch is one line. A `switch` should map each case to a returned value/object, not run a paragraph per case.

## Long loop bodies

**Smell:** a loop whose body is more than 1–2 lines. **Why it hurts:** the loop conflates iteration with per-item logic, so neither is named or testable on its own. **Fix:** extract the per-item work into a named method that acts on a single element; the loop body becomes a one-line call (`for (item of items) process(item)`), or better, a map/filter/reduce expression naming the transformation. The per-item method is then independently testable.

## Mutable state

**Smell:** objects mutated after construction; variables reassigned as a matter of course; shared mutable data. **Why it hurts:** mutation defeats local reasoning and is the root of aliasing and concurrency bugs — the highest-priority thing this style guards against. **Fix:** construct values fully formed and immutable; produce new values instead of mutating; confine any genuinely necessary mutation to the smallest possible scope and isolate it.

## Comments that explain *what*

**Smell:** a comment restating what the code does. **Why it hurts:** it's duplicated information that silently goes stale, and it's usually compensating for unclear code. **Fix:** delete it and make the code say it — rename, extract a well-named method. Keep only comments that explain a *why* the code cannot: a non-obvious constraint or a deliberate, externally-forced awkwardness.

## Nulls

**Smell:** methods returning null; callers guarding with null checks; nulls flowing into the domain. **Why it hurts:** every null is a check someone will forget, and the failure surfaces far from the cause. **Fix:** return null objects or empty collections for the "nothing" case; use an explicit optional at the boundary and resolve it before the value enters the domain (`architecture.md`). The aim is that null checks become rare because nulls are rare.

## Non-null assertions (null-forgiving operator)

**Smell:** a non-null assertion used to silence the type checker about a possible absence — TypeScript's `x!` and `!` postfix, C#'s `!` null-forgiving operator, force-unwraps, or a cast that asserts non-null. **Why it hurts:** it doesn't remove the null, it removes the *warning about* the null. The type system was telling you a value can be absent, and the operator overrides that judgment with your unverified word; when you're wrong, the null-safety net you were handed is gone and the failure resurfaces at runtime — a `NullReferenceException` / `undefined is not an object` far from where the assumption was made. It's the null smell made invisible. **Fix:** treat the compiler's nullability warning as correct and handle the absence honestly:
- **Narrow it** — a guard clause or early return that proves non-null to the type checker, so no assertion is needed.
- **Resolve it to a null object** or a sensible default before use, so there is genuinely nothing null to assert.
- **Return a failure** (result type) when absence is an expected outcome the caller must handle.
- **Fix the type** — if a field is truly always present, model it as non-nullable at construction rather than asserting it at every use.

The one narrow exception is a *test* asserting a value must exist to make the failure obvious (`expect(x).toBeDefined()` then use), and even there prefer the assertion library's own non-null helper. In production code, an `!` is a bug the compiler already found and you told it to ignore.
