---
name: cicd-pipeline-design
description: "Use when setting up CI/CD for a repo, adding or reordering pipeline stages, reviewing an existing pipeline against conventions, or deciding how an artifact is built, gated, and promoted across environments. Produces a short pipeline design note — the artifact strategy, stage ordering, gate map, promotion flow, reproducibility seams, secrets boundary, evidence-of-done, and failure diagnostics — with each decision's why. It DESIGNS the pipeline; it never writes the pipeline code or configurations (that is pipeline-authoring). Not for provisioning infrastructure, deployment/release strategy, or observability — those are other craft-ops domains."
---

# CI/CD Pipeline Design

Decide the pipeline's shape once, deliberately, so authoring is mechanical. The output is a short design note, not pipeline code — that goes to `pipeline-authoring`. Read `.craft-ops.yml` first if it exists (`craft-ops-conventions`).

Design the least pipeline that delivers: only the stages, environments, and gates the repo's real delivery needs today. If the existing pipeline already fits, the note confirms it and records the one thing that changed.

## Areas to account for

For a whole pipeline, decide all eight. For a targeted change, go deep on the areas it touches and discharge the rest together in one line ("not implicated: promotion, secrets, …") — nothing silently skipped, nothing padded.

- **Artifact strategy** — the single immutable artifact, where it's stored, identified by digest rather than a mutable tag alone. (`PRINCIPLES.md` core 3)
- **Stage ordering** — cheapest and most-likely-to-fail first: lint/format → unit tests → build → integration/acceptance → deploy. (`references/stage-ordering.md`)
- **Gate map** — which stages are hard automated gates, which are human promotion gates, where a red main stops the line.
- **Promotion flow** — the same artifact moves dev → staging → prod; only config and secrets differ. (`references/promotion.md`)
- **Reproducibility seams** — pinned toolchains and dependencies, ephemeral build environments, no network-dependent build steps. (`references/reproducible-builds.md`)
- **Secrets and config boundary** — nothing secret in the definition or the artifact; injected at deploy time.
- **Evidence of done** — the signal that proves the deploy is good in the target (health check, real traffic, a metric that moved), not a green job.
- **Failure diagnostics** — what a red run leaves behind: service logs collected before teardown, traces and videos, test reports, uploaded on failure *and* on cancel/timeout, named per job and attempt, retained long enough to read. Captured by default in the shared harness.

## Write it down

Save the note under `paths.pipelines` (e.g. `docs/craft-ops/pipelines/YYYY-MM-DD-<name>.md`), each decision with its *why*. Length tracks the change: depth where it's implicated, one line for the rest. Then hand off to `pipeline-authoring`.
