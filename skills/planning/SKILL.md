---
name: planning
description: "Use after intake and before any code — to turn agreed acceptance criteria into an ordered list of small, independently testable increments. Trigger whenever you have acceptance criteria but no implementation plan yet. Critically, this is where you mark which increments are independent so they can be dispatched to parallel subagents. Invoked by dev-workflow as phase 3."
---

# Planning

A plan makes the build phase routine: each increment's tests are written together, seen failing, and driven green in one cycle. It also says which increments can run in parallel.

## A good increment

- A thin vertical slice: one coherent piece of observable behavior, end to end, mapped to one or a few criteria.
- Small enough that its tests can be written up front and each seen failing cleanly — typically a handful of tests and a few files.
- Testable without increments that come later.

Prefer the fewest increments that keep each one that size; a plan of forty one-line increments is ceremony. Get something trivial working end to end first, then add behavior. Smells: horizontal layers ("build the data layer"), an increment whose tests need three others to exist, vague verbs ("handle", "support") instead of a named behavior.

## Write it down

A short plan saved where the work lives (`paths.plans` in `.craft-code.yml`, e.g. `docs/craft-code/plans/YYYY-MM-DD-<topic>.md`):

```
# Plan: promo codes at checkout

1. [independent] Reject unknown promo code → failure result naming the reason
     criteria: "invalid promo code returns a failure result"   files: promo/validate.ts
2. [independent] Apply percentage discount to subtotal
     criteria: "10% code reduces a $100 order to $90"          files: promo/apply.ts
3. [depends: 1,2] Wire promo entry into checkout
     criteria: "entering a valid code updates the shown total" files: checkout/*
```

## Marking independence

Two increments are `[independent]` only if they touch disjoint files; parallel implementers editing the same file corrupt each other's work. When unsure, mark it dependent — a missed parallelization costs a little time, a wrong one costs a broken merge. Order dependent increments so each one's tests can be written against what already exists.

## Exit condition

An ordered, written plan of increments, each tied to criteria and marked independent or dependent. Hand off to `worktree-setup`.
