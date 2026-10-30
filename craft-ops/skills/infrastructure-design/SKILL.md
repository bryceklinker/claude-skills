---
name: infrastructure-design
description: "Use when deciding the SHAPE of infrastructure or reviewing existing infrastructure-as-code against conventions — what resources a change introduces, how they're grouped into modules, where state lives, how changes are reviewed before apply, and how environments stay in parity. Produces a short infrastructure design note — resource inventory and disposable-vs-durable tiering, tool/tech selection, module composition, network segmentation, state management, change safety, environment parity, identity/least-privilege, drift, and evidence-of-done — each decision with its why. It DESIGNS the infrastructure; it never writes the actual IaC configuration (that is infrastructure-authoring). Not for CI/CD pipeline shape, deployment/release strategy, or observability — those are other craft-ops domains."
---

# Infrastructure Design

Decide the shape once, deliberately, so a database isn't force-replaced, state doesn't end up on a laptop, and lock-in isn't chosen by accident. The output is a short design note, not IaC — that goes to `infrastructure-authoring`. Read `.craft-ops.yml` first if it exists (`craft-ops-conventions`).

Design the least infrastructure that meets the need: no resource, environment, or module "in case." If what exists already fits, the note confirms it and records the one change.

## Areas to account for

For a whole environment, decide all ten. For a targeted change, go deep on the areas it touches and discharge the rest together in one line — nothing silently skipped, nothing padded.

- **Resource inventory and tiering** — every resource introduced or touched, classified disposable (compute, functions, containers, load balancers, most networking) or durable (databases, object stores, queues, topics, buses), with the deletion guard for each durable one. (`references/resource-tiers.md`)
- **Tool and tech selection** — prefer portable tooling (Terraform, OpenTofu, Pulumi) and portable tech; record any lock-in with its *why*.
- **Module boundaries** — modules, their inputs and outputs, shared versus per-environment; a module only where a shape repeats. (`references/state-and-modules.md`)
- **Network topology and segmentation** — the core network is a foundation unit provisioned first and handed down by reference; durable resources sit in their own segment reachable by default only from the compute network, with every exception named. (`references/resource-tiers.md`)
- **State management** — remote, locked, versioned, isolated per environment, treated as sensitive.
- **Change safety** — the plan is the gate, and its first check is whether it destroys or replaces a durable resource; if so, the migration path. (`references/review-before-apply.md`)
- **Environment parity** — staging and prod from the same modules, differing only in inputs.
- **Identity, least privilege, and secrets** — scoped apply-time credentials; no secrets in configuration or state.
- **Drift stance** — how drift is detected and reconciled back to code.
- **Evidence of done** — a clean apply and a post-apply check that the infrastructure is in its desired state (a second plan showing no changes), not "apply exited 0."

## Write it down

Save the note under `paths.infrastructure` (e.g. `docs/craft-ops/infrastructure/YYYY-MM-DD-<name>.md`), each decision with its *why*. Length tracks the change. Then hand off to `infrastructure-authoring`.
