---
name: planning
description: "Use after intake and before any code — to turn agreed acceptance criteria into an ordered list of small, independently testable increments. Trigger whenever you have acceptance criteria but no implementation plan yet. Critically, this is where you mark which increments are independent so they can be dispatched to parallel subagents. Invoked by dev-workflow as phase 2."
---

# Planning — slice the work into testable increments

## Why this exists

A plan's job is to make the strict-TDD phase boring. If the work is decomposed into small, well-ordered increments — each a thin vertical slice of behavior that a single test can drive — then implementation becomes a rhythm: red, green, refactor, commit, next. If it isn't, TDD thrashes because each "test" is really five behaviors tangled together.

Planning also unlocks parallelism. The orchestrator can only dispatch increments to concurrent subagents if the plan tells it which increments are independent. That judgment is made here, once, deliberately — not guessed at dispatch time.

## What a good increment looks like

Each increment is a **thin vertical slice**: the smallest change that adds one observable behavior end to end, drivable by one focused test (or a small handful). Prefer walking-skeleton order — get something trivial working end to end first, then flesh out behaviors — over building horizontal layers that can't be tested until they all exist.

Good increments:
- Map to one or two acceptance criteria.
- Are independently testable — you can write a failing test for this slice without the others existing.
- Are small enough to finish in one red-green-refactor cycle (minutes, not hours).

Smells in a plan:
- "Build the data layer" / "build the service layer" — horizontal slices that can't be verified alone.
- An increment whose test needs three other increments to exist first — it's too big or mis-ordered.
- Vague verbs: "handle", "support", "integrate". Name the behavior.

## Write it down

Produce a short plan document with an ordered list of increments. For each: the behavior, which acceptance criteria it satisfies, and its independence marker. Save it where the work lives (e.g. `docs/craft/plans/YYYY-MM-DD-<topic>.md`) so a resumed or subagent session can pick it up.

```
# Plan: promo codes at checkout

1. [independent] Reject unknown promo code → failure result naming reason
     criteria: "invalid promo code returns a failure result"
     files: promo/validate.ts
2. [independent] Apply percentage discount to subtotal
     criteria: "10% code reduces a $100 order to $90"
     files: promo/apply.ts
3. [depends: 1,2] Wire promo entry into checkout flow
     criteria: "entering a valid code updates the shown total"
     files: checkout/*
```

## Marking independence — the parallelism contract

For each increment, mark it `[independent]` or `[depends: N, M]`. The rule the orchestrator relies on:

**Two increments are independent only if they touch disjoint files.** Independent increments can run concurrently in sibling worktrees. Anything sharing a file must be sequenced, or the parallel subagents will collide and produce merge conflicts that quietly undermine the discipline.

When unsure, mark it dependent. A missed parallelization opportunity costs a little time; a wrong one costs a corrupted merge and lost trust in the pipeline. Sequence dependent increments in an order where each one's test can be written against already-existing slices.

## Exit condition

An ordered, written plan of thin increments, each tied to acceptance criteria, each marked independent or dependent. Hand off to `worktree-setup`.
