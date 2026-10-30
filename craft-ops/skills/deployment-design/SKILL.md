---
name: deployment-design
description: "Use when deciding HOW a new version is released to real traffic, or reviewing an existing release/rollout setup — the rollout strategy (canary, blue-green, rolling, rings), decoupling deploy from release (feature flags / dark launch), health-gated promotion and automatic rollback, blast-radius control, and backward/forward compatibility across the transition. Produces a short deployment design note — strategy, deploy-vs-release decoupling, rollout steps, dependency readiness, health gates, rollback plan, compatibility, state during rollout, ownership, and evidence-of-done — each decision with its why. It DESIGNS the release; it never performs or authors the rollout (that is deployment-authoring). It takes over once an artifact has reached an environment and defers to cicd-pipeline-design for pipeline shape and promotion. Not for CI/CD pipeline design, infrastructure provisioning, or observability — those are other craft-ops domains."
---

# Deployment Design

Decide how a release reaches users — and how it comes back — before traffic starts shifting. The output is a short design note, not rollout code, flag config, or a deploy script; those go to `deployment-authoring`. This skill starts once `cicd-pipeline-design` has put the artifact in an environment, and doesn't re-decide artifact strategy or promotion. Read `.craft-ops.yml` first if it exists (`craft-ops-conventions`).

Match the mechanism to the change's real risk. Minimal means the lightest mechanism that still limits exposure, gates on a signal, and can be undone — a deceptively simple change (a config value, a timeout, a flag) still gets a partial exposure step, a gate, and a rollback, just not canary rings plus flags plus automated analysis. If the existing release path fits, the note confirms it and records the one change.

## Areas to account for

For a new release path, decide all ten. For a targeted change, go deep on the areas it touches and discharge the rest together in one line — nothing silently skipped, nothing padded.

- **Release strategy** — canary, blue-green, rolling, or rings, and why it fits this risk. (`references/progressive-delivery.md`)
- **Deploy-vs-release decoupling** — what ships dark, the flag plan, who flips it. (`references/deploy-vs-release.md`)
- **Rollout steps and blast radius** — the concrete progression (internal → 1% → 10% → 50% → 100%), the population at each step, the pace.
- **Dependency and integration readiness** — *only when the change adds or swaps an external dependency*: capacity and rate-limit headroom at full production volume, and its failure mode (fail-open vs. fail-closed, timeouts, fallback). Otherwise, one line in the not-implicated note.
- **Health gates and abort criteria** — the objective signals and thresholds (error rate, latency, saturation, a business metric) that promote each step and auto-halt or auto-roll-back a regression, with an observation window per step. Every gate signal gets a number; a human watching a dashboard is not a gate.
- **Rollback and roll-forward plan** — both decided up front: how fast it reverts, what it costs, and the criteria for when rolling forward beats rolling back. (`references/rollback-and-compatibility.md`)
- **Compatibility across the transition** — old and new run at once: expand-contract migrations, N-1 schemas, APIs, and messages.
- **State and data during rollout** — sessions, in-flight work, sticky routing, migrations that must survive traffic moving.
- **Ownership and the release decision** — who starts, advances, and aborts; whether widening to everyone is automated or a human decision.
- **Evidence of done** — fully live, health held through 100%, and the rollback proven available throughout — not "the deploy job finished."

## Write it down

Save the note under `paths.deployments` (e.g. `docs/craft-ops/deployments/YYYY-MM-DD-<name>.md`), each decision with its *why*. Length tracks the change.

## Exit condition

A written note that accounts for all ten areas — the implicated ones decided in depth, the rest discharged in one not-implicated line — with numeric gates, a rollback and roll-forward plan, and evidence of done stated as explicit criteria. Hand off to `deployment-authoring`.
