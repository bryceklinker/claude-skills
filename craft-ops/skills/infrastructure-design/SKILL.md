---
name: infrastructure-design
description: "Use when deciding the SHAPE of infrastructure or reviewing existing infrastructure-as-code against conventions — what resources a change introduces, how they're grouped into modules, where state lives, how changes are reviewed before apply, and how environments stay in parity. Produces a short infrastructure design note — resource inventory and disposable-vs-durable tiering, tool/tech selection, module composition, state management, change safety, environment parity, identity/least-privilege, drift, and evidence-of-done — each decision with its why. It DESIGNS the infrastructure; it never writes the actual IaC configuration (that is a separate authoring skill). Not for CI/CD pipeline shape, deployment/release strategy, or observability — those are other craft-ops domains."
---

# Infrastructure Design — decide the shape before you provision it

## Why this exists

Infrastructure wired by guesswork force-replaces a database, leaks state onto a laptop, and locks you into one cloud before anyone decided that tradeoff was worth it. Deciding the shape once, deliberately, against the conventions, makes the authoring that follows mechanical rather than another set of judgment calls made under pressure at apply time.

It is a **thinking** phase, not a building one. The output is a short design note, not IaC configuration — that is handed off to the `infrastructure-authoring` skill, behind its own review.

## What it decides

Work from the change's actual resource needs, and settle only what they demand. Each decision below ties back to a principle in `craft-ops/PRINCIPLES.md`.

The ten areas are a **coverage checklist, not a required table of contents.** How much each gets depends on the ask:

- **Designing a whole environment** (greenfield, or a redesign): decide all ten — they're all in play.
- **A targeted change** (reviewing or reorganizing existing infrastructure — adding one resource, tightening a policy, moving state): go deep on the areas the change actually touches, and dispatch the rest in a **single one-line "not implicated" note** naming them together. The checklist exists so you don't *silently* skip an area that turns out to matter — a one-liner confirming an area is untouched discharges it completely. A paragraph defending why each unrelated area is unchanged is noise that buries the decision the person actually asked for.

- **Resource inventory & tier classification** — enumerate every resource the change introduces or touches; classify each disposable (compute, functions, containers, load balancers, most networking — rebuilt freely from code) or durable (databases, object/blob stores, queues, topics, event buses — holds state that can't be rebuilt from code); for every durable resource, name its deletion-protection / no-destroy guard. Classifying a resource into the wrong tier is how you lose data. (see `references/resource-tiers.md`)
- **Tool & tech selection** — apply the portability bias toward cloud-agnostic tooling (a cloud-agnostic tool such as Terraform, OpenTofu, or Pulumi, and cloud-agnostic provisioned tech where a portable equivalent exists) over cloud-specific tools; record any lock-in choice with its *why* — it's sometimes the right call, never the silent default.
- **Module boundaries & composition** — modules, their inputs/outputs, and which are shared versus per-environment. (see `references/state-and-modules.md`)
- **Network topology & segmentation** — the core virtual network (VPC/VNet, subnets, routing, base security groups) is its own foundational component, provisioned *before* the durable and disposable resources that attach to it and handed down to them by reference — they never co-create it. Durable resources sit in their own isolated network segment — a dedicated subnet, or a separate network — reachable *by default only from the compute/non-durable network*; the durable segment is default-deny to everything else, and every exception (a bastion, a migration or backup runner, a replication path) is named and justified up front, never added ad hoc. Deciding networking last, or leaving the durable tier reachable from outside the compute network, is how you get circular dependencies and a database exposed to something that was never supposed to reach it. (see `references/resource-tiers.md`)
- **State management** — remote, locked, versioned, isolated per environment, and treated as sensitive — never local, never committed to the repo. (see `references/state-and-modules.md`)
- **Change safety — review-before-apply & blast radius** — the plan/diff is the gate, and its first, non-negotiable check is whether it destroys or replaces any durable resource; if so, name the migration path — never applied on a green plan alone. (see `references/review-before-apply.md`)
- **Environment parity** — staging and prod built from the same modules, differing only in inputs/variables.
- **Identity, least privilege & secrets** — scoped, apply-time credentials; no secrets baked into configuration or state.
- **Drift stance** — how drift is detected and reconciled back to code; no manual console clicking as the source of truth.
- **Evidence of done** — the plan applied cleanly AND a real post-apply check that the infrastructure is in its desired state — not "apply exited 0."

## Write it down

Save a short design note where the work lives (e.g. `docs/craft-ops/infrastructure/YYYY-MM-DD-<name>.md`): the resource, tooling, module, state, and safety decisions, each with its *why*. If the repo has a `.craft-ops.yml`, read it first for the project's target environments and existing tooling conventions — it documents them until a dedicated conventions skill exists.

## Guardrails

- **YAGNI on resources and environments.** Don't add a resource or an environment "in case" — only what the change's actual needs demand today.
- **Never write the IaC configuration here.** If you catch yourself drafting the actual `.tf`, `.bicep`, Pulumi program, or any provisioning code, stop — that belongs to the authoring skill, behind its own review.
- **Prefer the existing shape.** If the infrastructure already fits the conventions, the right design note is short: confirm it, note the one thing that changed, and move on. Not every change needs a redesign.
- **Match the note's length to the change.** A targeted fix gets a targeted note — depth on the implicated areas, one line for the rest. If you find yourself writing a full section explaining why an area the ask never touched is "unchanged," collapse it into the one-line not-implicated note. Length signals importance; padding every area to equal weight hides which decision actually mattered.

## Exit condition

A written infrastructure design note that accounts for all ten checklist items — resource inventory & tier classification, tool & tech selection, module boundaries, network topology & segmentation, state management, change safety (review-before-apply), environment parity, identity/least-privilege/secrets, drift stance, and evidence of done — with the implicated ones decided in depth (each with its *why*) and any the change doesn't touch acknowledged in a single one-line not-implicated note. Nothing silently skipped; nothing padded. Hand off to the `infrastructure-authoring` skill to implement it.
