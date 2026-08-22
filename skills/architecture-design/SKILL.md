---
name: architecture-design
description: "Use after intake and before planning — to design the structure of a change that adds new moving parts: where the domain boundary sits, which ports and adapters it needs, where operations and their handlers live, how data flows across HTTP/GraphQL/gRPC and persistence, and what the shared types are. Trigger whenever a feature introduces a new module, a new integration, a new persistence or transport concern, background or scheduled work, or a non-trivial refactor of existing structure — anything where 'how is this shaped?' isn't already obvious.
 Produces a short design note that planning then decomposes into increments. Skip it for changes that add no new structure — a tweak inside an existing, well-shaped module. Not for pinning down requirements (intake), sequencing increments (planning), or writing the code."
---

# Architecture Design — decide the shape before you slice it

## Why this exists

Planning slices a change into increments, but it can only slice well if the *shape* of the solution is already decided. If the boundaries, ports, and handler placement are still open questions, planning either guesses (and the increments fight the structure later) or smears the design decision across every increment. This phase makes the structural decisions once, deliberately, so planning has something solid to decompose and strict-TDD has a target to build toward.

It is a **thinking** phase, not a building one. The output is a short design note, not code. No production code is written here — that waits for strict-TDD, behind the pipeline's gate.

## What to decide

Work from the agreed acceptance criteria (from `intake`) and settle only what the change actually needs. Over-designing is as costly as under-designing.

- **The domain boundary.** What is the core logic that must stay independent of transport and persistence? Draw the hexagon: what's inside, what's an edge detail.
- **Ports the change needs.** What does the domain need from the outside — `OrderRepository`, `PaymentGateway`, `Clock`? Name each in domain terms. These become the seams where test doubles are allowed (see `strict-tdd`).
- **Adapters at the edge.** Which concrete implementations sit behind each port (Postgres, Stripe, system clock), and which are new vs. existing.
- **Operations — inputs separated from handling.** Which operations this introduces, each as an immutable input data object plus its own dedicated handler — never a growing `Service`/`Manager`/`Utility`. A message + handler pair (CQRS) is the usual shape and a fine default (`CreateOrderCommand` → `CreateOrderCommandHandler`), but any shape that keeps the inputs as data and the handling separate is fine. If you split reads from writes, a query never mutates while a write handler may return data.
- **Data flow across boundaries.** How a request moves from a driving adapter (HTTP/GraphQL/gRPC/CLI) into a handler, out through ports, and back. Note where the shared domain types live and how the wire shapes mirror them.
- **Where it lives.** Which feature folder owns this; whether anything genuinely belongs in `shared` (only if more than one feature needs it).
- **What runs detached, and who owns its failure.** If the design introduces work with no caller waiting on it — a background loop, a poller, a scheduled job, an event subscriber, a queue consumer, a timer — name for each: who catches and logs its failure, what happens when it stops (does anything notice?), and how it shuts down. Detached work with no named owner is a design defect, not an implementation detail (see `code-style/references/failure-modes.md`).
- **What this reveals when it breaks.** For each new moving part, answer two questions in a line each: *what signal says it broke*, and *what evidence says why*. A component whose only failure mode is "it quietly stops working" is unfinished — give it a log, a health signal, or a surfaced error before it ships. Where craft-ops is available, its `observability-design` skill owns the runtime half of this (SLOs, symptom-based alerting, health signals) and is worth deferring to for anything user-facing or operationally significant; where it isn't, answer the two questions here rather than skipping them.

The full rule set behind these decisions lives in `code-style/references/architecture.md` and `patterns.md` — this skill is the *act of applying them* to one work item.

## Write it down

Produce a short design note — a paragraph and a sketch, not a treatise. Save it where the work lives (e.g. `docs/craft-code/design/YYYY-MM-DD-<topic>.md`) so `planning`, `strict-tdd`, and any subagent can read it. Include:

- The hexagon sketch: domain in the center, ports named, adapters at the edge.
- The operations — their input data objects and handlers.
- The new types and where they live.
- For any detached work: its failure owner, what notices when it stops, and how it shuts down.
- Any decision with a tradeoff
, stated with its *why* — so a later reader (or a reviewer) understands the choice rather than guessing at it.

## Guardrails

- **Design only what the criteria demand.** No speculative ports "in case," no abstraction with a single implementation and no second one in sight. YAGNI applies to structure too.
- **Don't write production code.** If you catch yourself implementing, stop — that's the strict-TDD phase, and it belongs behind the worktree gate.
- **Prefer the existing shape.** If the change fits cleanly into structure that already exists, the right design note is short: "fits the existing checkout feature, adds one operation and its handler." Not every change needs new architecture.

## Exit condition

A written design note: the domain boundary, the ports/adapters, the operations (input data objects + handlers), the shared types, where it all lives, the failure owner and shutdown story for anything detached, and what each new part reveals when it breaks — enough for `planning` to decompose into thin increments. Hand off to `planning`.

