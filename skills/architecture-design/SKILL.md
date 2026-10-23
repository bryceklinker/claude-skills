---
name: architecture-design
description: "Use after intake and before planning — to design the structure of a change that adds new moving parts: where the domain boundary sits, which ports and adapters it needs, where operations live, how data flows across HTTP/GraphQL/gRPC and persistence, and what the shared types are. Trigger whenever a feature introduces a new module, a new integration, a new persistence or transport concern, background or scheduled work, or a non-trivial refactor of existing structure — anything where 'how is this shaped?' isn't already obvious. Produces a short design note that planning then decomposes into increments. Skip it for changes that add no new structure — a tweak inside an existing, well-shaped module. Not for pinning down requirements (intake), sequencing increments (planning), or writing the code."
---

# Architecture Design

Decide the shape once, before planning slices it, so the increments don't fight the structure later. This is a thinking phase: the output is a short note, not code.

The target is the least structure that meets the criteria. Start from the shape the codebase already has; "fits the existing checkout feature, adds one operation" is a strong design. Every port, layer, type, and module you add answers to a criterion or a real seam — external I/O or a genuine second implementation. Don't add a port for code that can simply be called, an interface with one implementation, or a layer that only forwards.

## Decide only what the change needs

- **The domain boundary** — the logic that stays independent of transport and persistence.
- **Ports and adapters** — for each external dependency (database, API, clock, queue), the port named in domain terms and the adapter behind it; note which already exist.
- **Operations** — each behavior's input as plain data, handled by a dedicated unit; a function is the default, a class when it holds collaborators (`code-style/references/patterns.md`).
- **Data flow and types** — how a request moves from the driving adapter through the operation and out, and where shared types live (a feature folder; `shared` only if more than one feature needs it).
- **Detached work** — for any background loop, poller, scheduled job, subscriber, or timer: who catches and logs its failure, what notices if it stops, how it shuts down.
- **What each new part reveals when it breaks** — the signal that says it broke and the evidence that says why. Defer to craft-ops' `observability-design` for operationally significant parts when it's installed.

## Write it down

A paragraph and a sketch, saved under `paths.design` (e.g. `docs/craft-code/design/YYYY-MM-DD-<topic>.md`): the boundary and ports, the operations, the types and where they live, detached-work ownership, and each tradeoff with its *why* — including what you considered and left out.

## Exit condition

A short design note covering the above, enough for `planning`. Hand off to `planning`.
