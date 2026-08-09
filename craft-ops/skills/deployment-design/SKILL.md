---
name: deployment-design
description: "Use when deciding HOW a new version is released to real traffic, or reviewing an existing release/rollout setup — the rollout strategy (canary, blue-green, rolling, rings), decoupling deploy from release (feature flags / dark launch), health-gated promotion and automatic rollback, blast-radius control, and backward/forward compatibility across the transition. Produces a short deployment design note — strategy, deploy-vs-release decoupling, rollout steps, health gates, rollback plan, compatibility, state during rollout, ownership, and evidence-of-done — each decision with its why. It DESIGNS the release; it never performs or authors the rollout (that is a separate authoring skill). It takes over once an artifact has reached an environment and defers to cicd-pipeline-design for pipeline shape and promotion. Not for CI/CD pipeline design, infrastructure provisioning, or observability — those are other craft-ops domains."
---

# Deployment Design — decide how the release reaches users before you roll it out

## Why this exists

A release flipped 100% at once, with no way back, turns a bad version into an outage. Deciding the strategy, the health gates, and the rollback path once, deliberately, against the conventions, makes the rollout that follows mechanical rather than a set of judgment calls made under pressure while traffic is already shifting.

It is a **thinking** phase, not a doing one. The output is a short design note, not rollout code, feature-flag configuration, or a deploy script — that waits for the (future) `deployment-authoring` skill, behind its own review.

**Seam with the pipeline:** this skill takes over once `cicd-pipeline-design` has promoted a built artifact into an environment. It does not re-decide artifact strategy, stage ordering, or how an environment is promoted to — that is `cicd-pipeline-design`'s domain. This skill decides what happens to traffic once the artifact is there.

## What it decides

Work from the change's actual rollout needs, and settle only what they demand. Each decision below ties back to a principle in `craft-ops/PRINCIPLES.md` ("Deployment & release").

The nine areas are a **coverage checklist, not a required table of contents.** How much each gets depends on the ask:

- **Designing a whole rollout** (a new release path, or a redesign): decide all nine — they're all in play.
- **A targeted change** (reviewing or adjusting an existing rollout — tightening a gate, adding a ring, fixing a flag that never got cleaned up): go deep on the areas the change actually touches, and dispatch the rest in a **single one-line "not implicated" note** naming them together. The checklist exists so you don't *silently* skip an area that turns out to matter — a one-liner confirming an area is untouched discharges it completely. A paragraph defending why each unrelated area is unchanged is noise that buries the decision the person actually asked for.

- **Release strategy** — a progressive-delivery approach such as canary, blue-green, rolling, or ring-based, and why it fits this change's risk profile. (see `references/progressive-delivery.md`)
- **Deploy-vs-release decoupling** — what ships dark (deployed, not yet exposed) versus what's exposed immediately; the flag or toggle plan; who flips it and how. Deploy is not release — shipping the bits and exposing the behavior are separate actions. (see `references/deploy-vs-release.md`)
- **Rollout steps & blast radius** — the concrete progression (e.g. internal → 1% → 10% → 50% → 100%), the population covered at each step, and the pace between steps.
- **Health gates & abort criteria** — the objective signals (error rate, latency, saturation, a key business metric) that promote each step, and the thresholds that auto-halt or auto-roll-back a regression. A human eyeballing a dashboard is not a gate.
- **Rollback / roll-forward plan** — the reversible path decided up front, before the rollout starts: how fast it reverts, what it costs, and when roll-forward is the better call than rollback. Never ship what you can't cheaply undo. (see `references/rollback-and-compatibility.md`)
- **Compatibility across the transition** — old and new versions run at once during the rollout, so each must tolerate the other: expand-contract migrations, N-1 compatible schemas, APIs, and messages; what had to ship earlier to make this safe.
- **State & data during rollout** — sessions, in-flight work, sticky routing, and migrations that must survive traffic moving between old and new versions; ties to the infrastructure design's durable tier.
- **Ownership & the release decision** — who starts, advances, and aborts the rollout; whether the gate widening to prod-at-large is automated or requires a human decision. Deploying is routine; releasing is a deliberate, owned decision.
- **Evidence of done** — the release is fully live AND the health signals held through 100% AND the rollback path was proven available during the rollout — not "the deploy job finished."

## Write it down

Save a short design note where the work lives (e.g. `docs/craft-ops/deployments/YYYY-MM-DD-<name>.md`): the strategy, decoupling, rollout, gate, and rollback decisions, each with its *why*. If the repo has a `.craft-ops.yml`, read it first for the project's environments and existing release conventions — it documents them until a dedicated conventions skill exists.

## Guardrails

- **YAGNI on rollout mechanics.** Not every release needs canary rings plus feature flags plus automated health gates — match the mechanism to the actual risk of the change.
- **Never perform or author the rollout here.** If you catch yourself drafting flag configuration, a deploy script, or the actual rollout automation, stop — that belongs to the (future) authoring skill, behind its own review.
- **Prefer the existing shape.** If the release path already fits the conventions, the right design note is short: confirm it, note the one thing that changed, and move on. Not every change needs a redesign.
- **Match the note's length to the change.** A targeted fix gets a targeted note — depth on the implicated areas, one line for the rest. If you find yourself writing a full section explaining why an area the ask never touched is "unchanged," collapse it into the one-line not-implicated note. Length signals importance; padding every area to equal weight hides which decision actually mattered.
- **Defer to `cicd-pipeline-design` at the promotion seam.** This skill takes over once an artifact has reached an environment; it does not re-decide artifact strategy, stage ordering, or the pipeline's promotion flow — that's `cicd-pipeline-design`'s domain.

## Exit condition

A written deployment design note that accounts for all nine checklist items — release strategy, deploy-vs-release decoupling, rollout steps & blast radius, health gates & abort criteria, rollback/roll-forward plan, compatibility across the transition, state & data during rollout, ownership & the release decision, and evidence of done — with the implicated ones decided in depth (each with its *why*) and any the change doesn't touch acknowledged in a single one-line not-implicated note. Nothing silently skipped; nothing padded. Hand off to the (future) `deployment-authoring` skill to implement it.
