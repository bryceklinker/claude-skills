---
name: intake
description: "Establish and lock down requirements before writing code. Use when a feature, change, or bug is described but you don't yet have concrete, agreed-upon acceptance criteria — including requests to define, clarify, or write out acceptance criteria (e.g. given/when/then), figure out what a vague ticket really means, or pin down scope and edge cases before coding starts. For bugs, use this to build a reliable reproduction — reproduce the failure, establish a solid repro, or capture a failing test — before any fix is attempted. Applies whenever someone says \"before I start coding,\" \"let's nail down what this needs to do,\" \"reproduce this first,\" or \"establish a repro.\" Do not use once criteria are already agreed and it's time to plan, break work into tasks, or verify a finished fix."
---

# Intake

The most expensive defect is working code that solves the wrong problem. Intake produces a short list of agreed acceptance criteria that the plan, the tests, and the review are all measured against.

## For a feature or change

Ask one question at a time, and only about what the request and the code don't already answer: the intent and who it's for, what's in and out of scope, behavior at the edges (empty input, failure, concurrency), constraints, and — when it isn't obvious — whether this is the permanent shape or a deliberate stopgap. Stop as soon as you can write the criteria.

Write each criterion as something a test could assert, about observable behavior, in Given/When/Then shape (any number of Givens, one When, one or more Thens):

```
- Given a user with no saved addresses, when they open checkout, then the address form is empty.
- Given a total over $100, when the order is placed, then free shipping is applied.
- Given an invalid promo code, when it's applied, then a failure result names the reason.
```

Write only the criteria the change needs; each one becomes tests and code. Present them and get explicit agreement before planning.

## For a bug

Reproduce it before planning a fix — ideally as a failing automated test, at minimum a reliable manual sequence with observed output. That test becomes the first red in `strict-tdd`. Write the criterion as the corrected behavior. A suspected cause is a hypothesis for `systematic-debugging`, not a substitute for the reproduction.

## Look past the literal ask

Take the request at face value for scope, not for diagnosis. A bug report describes the symptom that reached someone; while reading the surrounding code, notice what else is wrong there and say so — "the warning is cosmetic; the same function also drops the file when the target exists — do you want both?" Name it and get a decision; don't silently expand scope, and don't silently ignore it.

## When the fix level is a real choice

Most work has one obvious shape. When it can be made at genuinely different levels — symptom, cause, structure — lay out the options with their costs and recommend the most durable one that fits the constraints. `references/fix-options.md` has the levels and the write-up format.

## Exit condition

Written, agreed acceptance criteria; for a bug, a reproduction. Where the level was a real choice, the chosen option and its reason are recorded. Hand off to `planning`.
