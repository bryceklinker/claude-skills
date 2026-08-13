---
name: cicd-pipeline-design
description: "Use when setting up CI/CD for a repo, adding or reordering pipeline stages, reviewing an existing pipeline against conventions, or deciding how an artifact is built, gated, and promoted across environments. Produces a short pipeline design note — the artifact strategy, stage ordering, gate map, promotion flow, reproducibility seams, secrets boundary, and evidence-of-done — with each decision's why. It DESIGNS the pipeline; it never writes the pipeline code or configurations (that is a separate authoring skill). Not for provisioning infrastructure, deployment/release strategy, or observability — those are other craft-ops domains."
---

# CI/CD Pipeline Design — decide the shape before you wire it

## Why this exists

A pipeline wired by guesswork rebuilds per environment, leaks secrets into places they shouldn't be, and orders stages so the slowest, least-likely-to-fail check runs first — burning a feedback cycle on every commit. Deciding the shape once, deliberately, against the conventions, makes the authoring that follows mechanical rather than another set of judgment calls.

It is a **thinking** phase, not a building one. The output is a short design note, not pipeline code or configurations — that is handed off to the `pipeline-authoring` skill, behind its own review.

## What it decides

Work from the repo's actual build, test, and deploy needs, and settle only what they demand. Each decision below ties back to a principle in `craft-ops/PRINCIPLES.md`.

The seven areas are a **coverage checklist, not a required table of contents.** How much each gets depends on the ask:

- **Designing a whole pipeline** (greenfield, or a redesign): decide all seven — they're all in play.
- **A targeted change** (reviewing or reorganizing an existing pipeline — reordering stages, fixing a rebuild, tightening one gate): go deep on the areas the change actually touches, and dispatch the rest in a **single one-line "not implicated" note** naming them together. The checklist exists so you don't *silently* skip an area that turns out to matter — a one-liner confirming an area is untouched discharges it completely. A paragraph defending why each unrelated area is unchanged is noise that buries the decision the person actually asked for.

- **Artifact strategy** — the single immutable artifact this pipeline produces, where it's stored, and how it's identified (a content or commit digest, never a mutable tag alone). *Build once.*
- **Stage ordering for fast feedback** — cheapest and most-likely-to-fail first: lint/format → unit tests → build the artifact → integration/acceptance → deploy. *Fail early.* (see `references/stage-ordering.md`)
- **The gate map** — which stages are hard automated gates that block the pipeline outright, and which are human promotion gates; where "green main is sacred" stop-the-line applies.
- **Promotion flow** — the same built artifact moves dev → staging → prod without a rebuild; only config and secrets differ per environment. (see `references/promotion.md`)
- **Reproducibility seams** — pinned toolchain and dependency versions, a hermetic/ephemeral build environment, no network-dependent build steps. (see `references/reproducible-builds.md`)
- **Secrets & config boundary** — nothing secret lives in the pipeline definition or gets baked into the artifact; both are injected at deploy time from the environment.
- **Evidence of done** — the health signal that proves the deploy is good in the target environment (a passing health check, real traffic served, a metric that moved) — not just a green pipeline job.

## Write it down

Save a short design note where the work lives (e.g. `docs/craft-ops/pipelines/YYYY-MM-DD-<name>.md`): the artifact, stage, gate, and promotion decisions, each with its *why*. If the repo has a `.craft-ops.yml`, read it first for the project's build/test commands and target environments — see `craft-ops-conventions`, which records and reads it.

## Guardrails

- **YAGNI on stages and environments.** Don't add a stage or an environment "in case" — only what the repo's actual delivery needs demand today.
- **Never write the pipeline code or configurations here.** If you catch yourself drafting the actual pipeline definition, stop — that belongs to the authoring skill, behind its own review.
- **Prefer the existing shape.** If a pipeline already fits the conventions, the right design note is short: confirm it, note the one thing that changed, and move on. Not every change needs a redesign.
- **Match the note's length to the change.** A targeted fix gets a targeted note — depth on the implicated areas, one line for the rest. If you find yourself writing a full section explaining why an area the ask never touched is "unchanged," collapse it into the one-line not-implicated note. Length signals importance; padding every area to equal weight hides which decision actually mattered.

## Exit condition

A written pipeline design note that accounts for all seven checklist items — artifact strategy, stage ordering, gate map, promotion flow, reproducibility seams, secrets & config boundary, and evidence of done — with the implicated ones decided in depth (each with its *why*) and any the change doesn't touch acknowledged in a single one-line not-implicated note. Nothing silently skipped; nothing padded. Hand off to the `pipeline-authoring` skill to implement it.
