# Refactoring techniques — catalog and mechanics

A curated, craft-aligned set of named refactorings (after Fowler's catalog and
refactoring.guru's six categories). Each entry: **what** it does, the **smell** it
answers, the **mechanics** as small behavior-preserving steps, and a **craft note**
tying it to the house style. Run the fast scoped test suite after every mechanical
step (see `strict-tdd`) — that is what keeps each step behavior-preserving. Apply
one technique at a time and commit it on its own.

## Table of contents
1. Composing Methods — Extract/Inline Function, Extract/Inline Variable, Replace Temp with Query, Split Variable, Replace Function with Command, Substitute Algorithm
2. Moving Features Between Objects — Move Function, Move Field, Extract Class, Inline Class, Hide Delegate, Remove Middle Man
3. Organizing Data — Replace Magic Literal, Encapsulate Variable, Replace Primitive with Object, Replace Type Code with Subclasses/Strategy
4. Simplifying Conditionals — Decompose Conditional, Consolidate Conditional, Guard Clauses, Replace Conditional with Polymorphism, Introduce Null Object
5. Simplifying Method Calls — Rename, Introduce Parameter Object, Preserve Whole Object, Replace Parameter with Query, Separate Query from Modifier
6. Dealing with Generalization — Pull Up, Push Down, Extract Superclass/Interface, Replace Subclass with Delegate, Collapse Hierarchy

---

## 1. Composing Methods

### Extract Function
**What:** pull a fragment of code into its own named function. **Answers:** long method, long loop body, comment-explaining-*what*, duplication. **Mechanics:**
1. Name the new function for its intent (what, not how).
2. Copy the fragment out; pass in the locals it reads as parameters.
3. Return the local it produces (one output — if several, the fragment wants to be an object; see Replace Function with Command).
4. Replace the original fragment with a call; run tests.
**Craft note:** the workhorse. Aim for functions that do one thing at one level of abstraction; the caller then reads as a short list of named steps.

### Inline Function
**What:** replace a call with the function's body and delete the function. **Answers:** indirection that no longer earns its keep — a function whose body is as clear as its name, or a bad extraction you're reversing. **Mechanics:**
1. Confirm it isn't polymorphic (don't inline something overridden).
2. Replace each call with the body; run tests after each.
3. Delete the function.
**Craft note:** use it to undo speculative indirection before re-extracting along better lines.

### Extract Variable
**What:** name a subexpression with a well-named local. **Answers:** a dense expression, a comment explaining a clause. **Mechanics:**
1. Introduce an immutable local (`const`/`readonly`) set to the subexpression.
2. Replace the subexpression with the variable; run tests.
**Craft note:** prefer explaining an expression by naming it over commenting it.

### Inline Variable
**What:** replace a variable with its initializing expression. **Answers:** a name that adds nothing (`const x = order` then only `x` used). **Mechanics:** replace each use with the expression; delete the declaration; run tests.

### Replace Temp with Query
**What:** replace a computed temp with a small function (query) that computes it. **Answers:** a temp reused across a long method; a step toward Extract Function. **Mechanics:**
1. Ensure the temp is assigned once and its source doesn't change before use.
2. Extract the right-hand side into a query function.
3. Replace reads of the temp with calls; run tests.
**Craft note:** turns local state into a pure, independently testable function — a small win against mutable state.

### Split Variable
**What:** give each distinct responsibility of a reused/reassigned variable its own single-assignment variable. **Answers:** mutable state, a temp reassigned for two different purposes. **Mechanics:**
1. Rename the first use to its own immutable variable.
2. Introduce a second immutable variable for the second responsibility.
3. Run tests after each split.
**Craft note:** a reassigned temp almost always means two values sharing one name; separate them and both become immutable.

### Replace Function with Command (Method Object)
**What:** turn a big function with many locals into an object whose fields are those locals. **Answers:** a long method too entangled in local state to Extract Function directly. **Mechanics:**
1. Create a class; move the function in as its single operation.
2. Promote the shared locals to fields set in the constructor.
3. Now Extract Function freely into private methods that read those fields; run tests throughout.
**Craft note:** the input-object-plus-handler shape (see `code-style/patterns.md`) — the honest home for behavior that a plain function couldn't hold.

### Substitute Algorithm
**What:** replace a whole algorithm body with a clearer one. **Answers:** a convoluted implementation where a simpler equivalent exists. **Mechanics:**
1. Ensure the behavior is fully covered by tests first.
2. Swap the body for the clearer algorithm; run tests.
**Craft note:** only behavior-preserving if the tests truly pin the behavior — verify coverage before you swap.

---

## 2. Moving Features Between Objects

### Move Function
**What:** move a function to the object it most belongs with. **Answers:** feature envy, Law of Demeter train-wreck, data class. **Mechanics:**
1. Check what the function uses; if it touches another object's data more than its own, that object is its home.
2. Copy it there, adjust references to become local, leave a delegating call (or update callers).
3. Run tests; remove the old function once callers move.
**Craft note:** "tell, don't ask" — behavior belongs with the data it works on.

### Move Field
**What:** relocate a field to the class that uses it most. **Answers:** a field consistently read/written through another object. **Mechanics:** add it to the target, redirect accessors, run tests, remove the original.

### Extract Class
**What:** split one class into two along a seam of responsibility. **Answers:** large class, `Service`/`Manager`/`Utility` grab-bag, data clumps. **Mechanics:**
1. Identify a subset of fields+methods with one reason to change.
2. Create the new class; move that subset (Move Field / Move Function), one member at a time, tests between.
3. Link from the old class or update callers.
**Craft note:** decompose into focused operations, not a slightly smaller grab-bag.

### Inline Class
**What:** fold a class that no longer pulls its weight into its only user. **Answers:** lazy class, a class left anemic after other moves. **Mechanics:** move its members into the host; redirect; delete the class; tests throughout.

### Hide Delegate
**What:** give a class a method so callers stop navigating through it to a delegate. **Answers:** Law of Demeter train-wreck (`a.getB().getC()`). **Mechanics:**
1. Add a method on the server that does the delegation (`order.shippingCountryCode()`).
2. Point callers at it; run tests.
3. Remove the now-unused getter if nothing else needs it.
**Craft note:** the direct fix for message chains — callers talk only to immediate collaborators.

### Remove Middle Man
**What:** the inverse — when a class does nothing but delegate, let callers talk to the delegate. **Answers:** middle man (every method just forwards). **Mechanics:** replace forwarding methods with direct access; run tests. Balance against Hide Delegate — some delegation is worth keeping.

---

## 3. Organizing Data

### Replace Magic Literal with Named Constant
**What:** give an unexplained literal a name. **Answers:** magic number/string. **Mechanics:** declare a named constant; replace each occurrence *that means the same thing*; run tests. **Craft note:** don't merge two literals that happen to share a value but not a meaning.

### Encapsulate Variable / Field
**What:** route access to a piece of data through functions. **Answers:** exposed mutable data, a field about to grow behavior. **Mechanics:** wrap reads/writes in accessors; redirect callers; run tests. **Craft note:** a stepping stone — once encapsulated, it's easy to move behavior onto the data or make it immutable.

### Replace Primitive with Object
**What:** promote a primitive that carries meaning/rules into a small value type. **Answers:** primitive obsession (a `string` email, an `int` money). **Mechanics:**
1. Create a value type wrapping the primitive with its validation/behavior.
2. Replace usages incrementally; run tests.
**Craft note:** immutable value objects with behavior are the goal — this is how primitives grow up.

### Replace Type Code with Subclasses / Strategy
**What:** replace a `kind`/`type` field driving branches with polymorphic types. **Answers:** duplicated switch/if-else over a type code. **Mechanics:**
1. Introduce a type (subclass or strategy) per code value.
2. Move each branch's body onto the matching type.
3. Replace construction with a factory mapping code → type (see `code-style/patterns.md`); run tests.
**Craft note:** pairs with Replace Conditional with Polymorphism below.

---

## 4. Simplifying Conditional Expressions

### Decompose Conditional
**What:** extract the condition, then-branch, and else-branch into named functions. **Answers:** sprawling/nested conditional whose intent is buried. **Mechanics:** Extract Function on the test (`isEligibleForDiscount(...)`) and on each branch body; run tests. **Craft note:** the condition and branches become one-line, intention-revealing calls.

### Consolidate Conditional Expression
**What:** combine several checks that all lead to the same result. **Answers:** a stack of `if`s returning the same thing. **Mechanics:** OR/AND the conditions into one; Extract Function to name the combined check; run tests.

### Replace Nested Conditional with Guard Clauses
**What:** flatten a pyramid of `if/else` into early returns for the exceptional cases. **Answers:** deep nesting, sprawling control flow. **Mechanics:**
1. For each special/exit case, return early at the top.
2. Let the main path fall through, un-nested; run tests after each.
**Craft note:** each branch becomes a single-line return — the house-style shape.

### Replace Conditional with Polymorphism
**What:** move each branch of a type-switch onto a subtype/strategy that overrides a method. **Answers:** duplicated switch/type-code branching. **Mechanics:**
1. Ensure the types exist (Replace Type Code with Subclasses/Strategy).
2. Move one branch's body into an override; delete that case; run tests.
3. Repeat until the switch is gone (or lives only inside the factory).
**Craft note:** prefer polymorphism over repeated type-branching; a single switch inside a factory is fine.

### Introduce Null Object
**What:** replace null-and-check with an object representing "nothing" that answers the same messages. **Answers:** nulls, non-null assertions. **Mechanics:**
1. Create a null-object variant with do-nothing/default behavior.
2. Return it instead of null at the source; delete the null checks; run tests.
**Craft note:** a `code-style` fix (see `architecture.md`) — null checks become rare because nulls become rare.

---

## 5. Simplifying Method Calls

### Rename Function / Variable
**What:** change a name to reveal intent. **Answers:** unclear name, a comment compensating for one. **Mechanics:** rename at the declaration and all uses (prefer the tool's rename); run tests. **Craft note:** the cheapest, highest-leverage refactoring — nouns for variables, verbs for functions, `is/has/can` for booleans.

### Introduce Parameter Object
**What:** replace a clump of parameters that travel together with a single object. **Answers:** long parameter list, data clumps. **Mechanics:**
1. Create an immutable type for the group.
2. Add it as a parameter; migrate call sites; remove the old parameters; run tests.
**Craft note:** the group usually names a real concept (`DateRange`, `Money`) that then attracts behavior.

### Preserve Whole Object
**What:** pass the whole object instead of several values pulled off it. **Answers:** long parameter list built by unpacking one object. **Mechanics:** pass the object; let the callee extract what it needs; run tests. **Craft note:** shortens call sites and often reveals the method belongs on that object (Move Function).

### Replace Parameter with Query
**What:** drop a parameter the callee can derive itself. **Answers:** long parameter list, a parameter always computed from another. **Mechanics:** remove the parameter; compute it inside via a query; run tests. (Don't do this if it introduces an unwanted dependency.)

### Separate Query from Modifier
**What:** split a function that both returns a value and causes a side effect. **Answers:** a "getter" that mutates — a correctness hazard. **Mechanics:** create a pure query and a separate modifier; update callers; run tests. **Craft note:** supports the read/write separation the suite favors — a query never mutates.

---

## 6. Dealing with Generalization

### Pull Up Method / Field
**What:** move a member shared by siblings up into the superclass. **Answers:** duplicate code across subclasses. **Mechanics:** confirm the members are identical (Extract Function to align first if needed); move one up; delete the copies; run tests.

### Push Down Method / Field
**What:** move a member only one subclass uses down into it. **Answers:** a superclass member relevant to a single subtype (refused bequest). **Mechanics:** move it down; run tests.

### Extract Superclass / Interface
**What:** introduce a common parent/interface for the shared surface of related classes. **Answers:** duplicate code and parallel structure across classes with a common role. **Mechanics:** create the type; Pull Up the shared members (or declare the shared interface); point callers at the abstraction; run tests. **Craft note:** program to the role, not the concrete class.

### Replace Subclass with Delegate
**What:** replace inheritance used only for a small variation with a delegated strategy. **Answers:** refused bequest, inheritance strained to model a variant. **Mechanics:**
1. Create a delegate holding the varying behavior.
2. Move the subclass's overrides onto the delegate; forward from the host.
3. Remove the subclass; run tests.
**Craft note:** favor composition over inheritance when the "is-a" is really "has-a behavior."

### Collapse Hierarchy
**What:** merge a superclass and subclass that no longer differ enough to justify separation. **Answers:** a hierarchy left thin by other refactorings. **Mechanics:** move members into one class; redirect; delete the other; run tests.
