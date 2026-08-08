# Changelog

All notable changes to the `craft-ops` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/). While pre-1.0, minor versions may
introduce new domains and skills; the suite's core discipline stays stable.

## [0.2.0] — 2026-08-08

### Added
- **Infrastructure as Code principles** — a new `## Infrastructure as Code`
  section in `PRINCIPLES.md`: declarative desired state, idempotent &
  convergent, immutable where disposable and protected where durable, review
  before apply (catching a destroy/replace of a durable resource), state as
  shared/locked/sensitive, no manual drift, small composable modules with
  environment parity through inputs, least privilege with secrets never in
  code or state, preferring portable cloud-agnostic tooling, and the same
  state-the-why/escape-hatch discipline as the CI/CD principles.
- **`infrastructure-design` skill** — decides an infrastructure change's shape
  before anything is applied. Ships with three references:
  `references/state-and-modules.md`, `references/review-before-apply.md`, and
  `references/resource-tiers.md`.
- **README domain table** — Infrastructure as Code marked `Built` with the
  `infrastructure-design` skill; the future `infrastructure-authoring` skill
  (writes the config) added as a `Planned` row.

## [0.1.0] — 2026-08-06

Initial release of the craft-ops DevOps suite, covering the CI/CD domain first.

### Added
- **`craft-ops` plugin** — a sibling to `craft`, distributed through the same
  marketplace but installable and usable entirely on its own.
- **`PRINCIPLES.md`** — the canonical CI/CD principles (build once and promote the
  same artifact, the pipeline as versioned code, fast feedback and fail early,
  reproducible hermetic builds, deploy is not release, config/secrets from the
  environment, done rests on evidence from the real target, state the why and keep
  the escape hatch), plus one-line stubs previewing the domains still to come:
  infrastructure as code, deployment & release, and observability & incident
  response.
- **`cicd-pipeline-design` skill** — decides a pipeline's shape before anything is
  wired: artifact strategy, stage ordering for fast feedback, the gate map,
  promotion flow, reproducibility seams, the secrets/config boundary, and the
  evidence that proves a deploy is done. A thinking skill that produces a design
  note, never pipeline code or configuration. Ships with three references:
  `references/stage-ordering.md`, `references/promotion.md`, and
  `references/reproducible-builds.md`.
- **Marketplace registration** — `craft-ops` added alongside `craft` in
  `.claude-plugin/marketplace.json`, installable independently via
  `/plugin install craft-ops@craft-marketplace`.

[0.2.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.2.0
[0.1.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.1.0
