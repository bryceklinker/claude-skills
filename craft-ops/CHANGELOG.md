# Changelog

All notable changes to the `craft-ops` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/). While pre-1.0, minor versions may
introduce new domains and skills; the suite's core discipline stays stable.

## [0.4.0] — 2026-08-09

### Added
- **Observability & incident response principles** — a new
  `## Observability & incident response` section in `PRINCIPLES.md`:
  observability as a design input and the precondition for safe deployment,
  alert on symptoms not causes, SLOs and error budgets as the contract,
  runtime levers that ramp detail up and down without a redeploy, instrumenting
  for the questions you'll ask under pressure, signals as a cost, mitigate
  before you diagnose, blameless review, every incident tightening the
  ratchet, finding the cause with method not guesses, and the same
  state-the-why/escape-hatch discipline as the other domains.
- **`observability-design` skill** — decides what a service reveals before
  anything breaks: SLIs/SLOs and error budget, the signals to emit, symptom-based
  alerting, the runtime levers (verbosity, sampling, trace detail) that ramp
  observability up and down without a redeploy, and the health signals
  `deployment-design`'s gates and rollback decisions consume, plus correlation,
  cost/retention, and ownership. Ships with three references:
  `references/observability-levers.md`, `references/slos-and-alerting.md`, and
  `references/signals-and-cardinality.md`.
- **`incident-response` skill** — drives the live response as a discipline:
  declare and assign roles early, mitigate before you diagnose (the reversible
  levers and observability dials pulled up, not invented under pressure),
  diagnose with method, verify resolution on the real signal, then a blameless
  postmortem that ratchets — tracked action items plus at least one new test or
  alert that would have caught it. Root-cause mechanics are deferred entirely
  to craft's `systematic-debugging`; this skill owns only the incident
  wrapper. Ships with three references: `references/incident-command.md`,
  `references/mitigation-first.md`, and `references/blameless-postmortem.md`.
- **README domain table** — Observability & incident response marked `Built`
  with the `observability-design` and `incident-response` skills; the future
  `observability-authoring` skill (writes the instrumentation/dashboards/alerts)
  added as a `Planned` row. Plugin version bumped to `0.4.0`.

## [0.3.1] — 2026-08-09

### Changed
- **`deployment-design` — added a tenth coverage item, "Dependency & integration
  readiness."** A behavioral eval surfaced that new-integration rollouts weren't
  being forced to reason about the new dependency's operational readiness. The item
  is *conditional* — it fires only when a change introduces or swaps an external
  dependency (provider, API, queue, datastore), covering its capacity/rate-limit
  headroom for full production volume and its failure mode (fail-open vs. fail-closed,
  timeouts, fallback); for a change with no new dependency it's discharged in the
  one-line not-implicated note, preserving scope-down. Ties to blast-radius control
  and health-gated abort (`PRINCIPLES.md` Deployment 6 & 4). Re-eval: with-skill
  100% vs. prior-skill 92% across three prompts, no scope-down regression and no
  time/token cost.

## [0.3.0] — 2026-08-08

### Added
- **Deployment & release principles** — a new `## Deployment & release`
  section in `PRINCIPLES.md`: deploy is not release, progressive delivery
  that widens on a healthy signal, rollback-first (never ship what you
  can't cheaply undo), health-gated promotion with automatic halt on
  regression, backward/forward compatibility across the transition,
  controlling the blast radius, release as a deliberate decision versus
  deploy as routine, progressive delivery bounded by what you can observe,
  and the same state-the-why/escape-hatch discipline as the other domains.
- **`deployment-design` skill** — decides how a release reaches users
  before the rollout starts: strategy, deploy-vs-release decoupling,
  rollout steps and blast radius, health gates and abort criteria, the
  rollback/roll-forward plan, compatibility across the transition, state
  during rollout, ownership, and evidence of done. Ships with three
  references: `references/progressive-delivery.md`,
  `references/deploy-vs-release.md`, and
  `references/rollback-and-compatibility.md`.
- **README domain table** — Deployment & release marked `Built` with the
  `deployment-design` skill; the future `deployment-authoring` skill
  (performs the rollout) added as a `Planned` row.

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

[0.3.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.3.0
[0.2.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.2.0
[0.1.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.1.0
