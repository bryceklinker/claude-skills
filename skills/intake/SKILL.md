---
name: intake
description: "Establish and lock down requirements before writing code. Use when a feature, change, or bug is described but you don't yet have concrete, agreed-upon acceptance criteria — including requests to define, clarify, or write out acceptance criteria (e.g. given/when/then), figure out what a vague ticket really means, or pin down scope and edge cases before coding starts. For bugs, use this to build a reliable reproduction — reproduce the failure, establish a solid repro, or capture a failing test — before any fix is attempted. Applies whenever someone says \"before I start coding,\" \"let's nail down what this needs to do,\" \"reproduce this first,\" or \"establish a repro.\" Do not use once criteria are already agreed and it's time to plan, break work into tasks, or verify a finished fix."
---

# Intake — decide what "done" means before building

## Why this exists

The most expensive defect is a feature that works perfectly and solves the wrong problem. Intake is the cheapest possible insurance against it: a few minutes of clarifying intent and writing down acceptance criteria, before a single line of code commits you to an interpretation.

The output of intake is small but load-bearing — a short list of acceptance criteria that everything downstream (the plan, the tests, the review) is measured against.

## For a feature or change

Ask questions **one at a time** until you can answer these. Don't interrogate; converse. Stop as soon as the picture is clear enough to write criteria — over-specifying is its own waste.

- **Intent** — what problem does this solve, for whom? What does success look like from the user's side?
- **Scope** — what's explicitly in, and just as importantly, what's out? Where's the boundary?
- **Behavior at the edges** — empty inputs, failures, concurrent use, the unhappy paths that tests will need.
- **Constraints** — existing patterns to follow, interfaces that can't change, performance or compatibility limits.
- **Durability** — how long does this need to hold? Is this the permanent shape of the thing, or a deliberate stopgap with something better behind it? Ask when the answer isn't obvious; the default assumption is permanent, because that's what a stopgap becomes when nobody names it one.

## Look past the literal ask

Take the request at face value for *scope*, not for *diagnosis*. Someone reporting a bug describes the symptom that reached them, which is often not the worst thing in that code path — a report about a noisy warning can sit ten lines from a data-loss bug nobody noticed. So while you're reproducing and reading the surrounding code, notice what else is wrong there and say so.

That doesn't license scope creep. Name what you found, state whether it's in or out of this change, and get agreement — "the warning is cosmetic; the same function also drops the file when the target exists — do you want both?" Silently fixing only what was asked, when you saw the bigger defect, is the failure this guards against.

Then write **acceptance criteria** as concrete, checkable statements — each one something a test could later assert. Prefer observable behavior over implementation:

```
- Given a user with no saved addresses, when they open checkout, then the address form is shown empty.
- Given a total over $100, when the order is placed, then free shipping is applied.
- An invalid promo code returns a failure result naming the reason; it never throws.
```

Present the criteria back and get explicit agreement before moving to `planning`. Disagreement surfaced here costs a sentence; surfaced after implementation it costs a rewrite.

## For a bug

A bug's intake has one non-negotiable extra step: **reproduce it first.**

<HARD-GATE>
Do not plan or attempt a fix until you have reproduced the failure — ideally as a failing automated test, at minimum as a reliable manual sequence with observed output. A bug you cannot reproduce is a bug you cannot prove you fixed.
</HARD-GATE>

1. **Reproduce.** Establish the exact steps and the actual (wrong) behavior versus the expected behavior.
2. **Capture it as a failing test if you can.** This test becomes the first RED of the `strict-tdd` phase — the fix is done when it goes green, and it guards against regression forever.
3. **Write the acceptance criterion** as the corrected behavior, in the same Given/When/Then shape.

Resist the pull to jump straight to a suspected cause. "I bet it's the null check" is a hypothesis for `systematic-debugging`, not a substitute for reproducing the actual failure.

## When there's a real choice, present options — and recommend one

Most work has one obvious shape and needs no menu. But when the change can be made at genuinely different levels — patch the symptom, fix the cause, or change the structure that allowed it — don't pick silently and don't hand over a neutral list. Lay out the options with their costs and **recommend the most durable one that fits the real constraints**, saying why.

The recommendation is the deliverable. A menu with no recommendation moves the judgment to whoever has less context about the code than you do, and the cheapest-looking option wins by default. If a stopgap is chosen anyway, that's a legitimate answer — record it as one, with the condition that would let it be removed.

`references/fix-options.md` has the four levels, the questions that decide between them, and how to write the options up.

## Exit condition

You're done with intake when there is a written, agreed set of acceptance criteria — and for bugs, a reproduction (preferably a failing test). Where the change had a real choice of level, the chosen option and its rationale are recorded alongside them. Hand off to `planning`.
