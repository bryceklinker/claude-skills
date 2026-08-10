# Changelog

All notable changes to the `craft-ops` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/). While pre-1.0, minor versions may
introduce new domains and skills; the suite's core discipline stays stable.

## [0.9.0] — 2026-08-10

### Added
- **`observability-authoring` skill** — turns an `observability-design` note
  into the real observability-as-code: instrumentation, dashboards-as-code,
  alert rules, and runtime-lever wiring. It draws two hard lines: **prove the
  alert fires** — an alert rule is verified by firing it against a
  synthetic/replayed signal that should trip it (and confirming it stays
  quiet on a healthy one), never trusted on the strength of a threshold that
  merely looks right; and **wire the runtime levers for real** — verbosity,
  sampling, and trace-detail levers are wired to runtime config or flags,
  with default-vs-incident settings and cost guardrails, so a lever flips
  without a redeploy rather than sitting as a constant baked into a build.
  It also prefers generated/extracted dashboards-and-alerts-as-code over
  click-ops or copy-pasted duplication, alerts on symptoms rather than
  causes, and enforces cardinality guardrails against unbounded metric
  labels. Metric/SLO/burn-rate/lever logic goes through craft's `strict-tdd`;
  the declarative dashboards and alert rules are proven by craft's
  `verification` — validate/lint + an entrypoint smoke-invoke of each
  extracted script is the always-runnable minimum, mirroring
  `pipeline-authoring`, `infrastructure-authoring`, and
  `deployment-authoring`. Both halves defer to `craft`'s `strict-tdd` and
  `verification` skills rather than reimplementing them, named generically so
  the skill degrades gracefully without `craft` installed. Deciding what to
  observe stays with `observability-design`; the production loop itself is
  deferred entirely to `craft`. Ships with two references:
  `references/observability-as-code-hygiene.md` and
  `references/testing-and-verifying-observability.md`.
- **README & `observability-design`** — the Observability & incident response
  row's `observability-authoring` skill marked `Built`; the
  `observability-design` `SKILL.md` prose retargeted from the "(future)
  `observability-authoring` skill" to the now-built sibling. This completes
  the suite: every domain (CI/CD, Infrastructure as Code, Deployment &
  release, Observability & incident response) now has both a design and an
  authoring skill. Plugin version bumped to `0.9.0`.

## [0.8.0] — 2026-08-10

### Added
- **`deployment-authoring` skill** — turns a `deployment-design` note into the
  real rollout: the progressive-delivery mechanics, feature-flag/toggle
  wiring, and health-gated promotion the design decided. It draws four hard
  lines: **author and prove the rollback path** — the revert isn't merely
  described, it's exercised as part of authoring, never assumed to work
  because it was written down; **health gates as tested code** — the
  thresholds that promote or halt a step are gated logic proven the same way
  as any other production code, never a human eyeballing a dashboard;
  **extracted scripts over inline** — non-trivial rollout logic (gate
  evaluation, flag flips, rollback triggers) lives in script files driven
  through `strict-tdd`, never buried un-testable in the rollout definition;
  and **deploy decoupled from release** — the authored rollout ships dark by
  default and exposes behavior only through the flag/toggle the design
  specified, deploy and release kept as separate, separately-owned actions.
  Declarative rollout glue is proven by craft's `verification`, with
  `validate` + an entrypoint smoke-invoke of each extracted script as the
  always-runnable minimum, mirroring `pipeline-authoring` and
  `infrastructure-authoring`. Both halves defer to `craft`'s `strict-tdd` and
  `verification` skills rather than reimplementing them, named generically so
  the skill degrades gracefully without `craft` installed. Deciding the
  rollout's shape stays with `deployment-design`; the production loop itself
  is deferred entirely to `craft`. Ships with two references:
  `references/rollout-authoring-hygiene.md` and
  `references/testing-and-verifying-rollouts.md`.
- **README & `deployment-design`** — the Deployment & release row's
  `deployment-authoring` skill marked `Built`; the `deployment-design`
  `SKILL.md` prose retargeted from the "(future) `deployment-authoring` skill"
  to the now-built sibling. Plugin version bumped to `0.8.0`.

## [0.7.0] — 2026-08-10

### Added
- **Network topology & segmentation, across `infrastructure-design` and
  `infrastructure-authoring`.** Two conventions on either side of the
  design→authoring seam:
  - `infrastructure-design` gains a tenth coverage item — **network topology &
    segmentation**: the core virtual network is its own foundational component
    provisioned before the resources that attach to it, and durable resources
    sit in an isolated network segment reachable *by default only from the
    compute network* (default-deny; every exception named and justified up
    front).
  - `infrastructure-authoring` gains the enforcement rule **isolate durable
    resources in their own network segment** (dedicated subnet or separate
    network; ingress only from the compute network; exceptions defined
    explicitly, never ad hoc). With "provision the networking foundation
    first" (0.6.1) and "never co-locate a durable resource in a compute unit,"
    the three now cover distinct axes — lifecycle (co-location), dependency
    (foundation-first), and reachability (segmentation).

### Changed
- Retargeted the stale "(future) `infrastructure-authoring`" references in
  `infrastructure-design`'s `SKILL.md` now that the skill is built.

## [0.6.1] — 2026-08-10

### Changed
- **`infrastructure-authoring` — added the "provision the networking
  foundation first" rule.** A behavioral validation (dispatching
  `craft-ops-author` on a sample orders-infra design note) surfaced that the
  core virtual network (VPC/subnets) was being placed alongside the resources
  that plug into it, which forces a circular dependency or a scramble to
  reverse-engineer network IDs. `SKILL.md` and
  `references/iac-authoring-hygiene.md` now require the core network — VPC/VNet,
  subnets, routing, base security groups — to be authored as its own
  foundational unit applied *before* any durable or disposable resource; those
  resources receive network identifiers (VPC/subnet/security-group IDs) as
  inputs and plug in, never co-creating the network. It is the ordering
  companion to never-co-locate-durable-in-compute — that rule separates units
  along the lifecycle axis, this one along the dependency axis.

## [0.6.0] — 2026-08-10

### Added
- **`infrastructure-authoring` skill** — turns an `infrastructure-design` note
  into the real infrastructure-as-code: it prefers small composable modules
  over duplicated resource blocks, and draws a hard line that a durable
  resource — a database, object store, queue, topic, or bus — is never
  co-located inside a compute unit's module or stack; compute references
  durable resources by input, never creates them. Durable resources are
  further protected with lifecycle guards, and every apply goes out only
  after the plan has been read — `review-before-apply`, no exceptions for
  "obviously safe" changes. Like `pipeline-authoring`, it splits production
  discipline in two: policy/module logic goes through craft's `strict-tdd`,
  while the declarative resources are proven by craft's `verification` —
  `validate` + `plan`/`diff` is the always-runnable minimum, catching broken
  references, type errors, and unexpected destroy/replace even with no apply
  target available, with a full apply against a sandbox where one exists.
  Deciding the infrastructure's shape stays with `infrastructure-design`; the
  production loop itself is deferred entirely to `craft`, named generically
  so the skill degrades gracefully without `craft` installed. Ships with two
  references: `references/iac-authoring-hygiene.md` and
  `references/testing-and-verifying-infrastructure.md`.
- **README** — the Infrastructure as Code row's `infrastructure-authoring`
  skill marked `Built`; the `infrastructure-design` prose retargeted from
  "the future `infrastructure-authoring` skill" to the now-built sibling.
  Plugin version bumped to `0.6.0`.

## [0.5.1] — 2026-08-09

### Changed
- **`pipeline-authoring` — added entrypoint smoke-invocation to the
  glue-verification rule.** A behavioral validation (dispatching
  `craft-ops-author` on a sample design note) surfaced a class of bug the
  TDD-for-logic / verification-for-glue split didn't explicitly guard:
  extracted-script unit tests import the functions directly, but the pipeline
  invokes them through an entrypoint (`python -m ci.promote`), so a wrong
  module name or broken CLI path passes a green unit suite and fails on the
  first real run (observed: a definition calling `ci.promote` when the module
  was `ci.promotion`). `SKILL.md` and
  `references/testing-and-verifying-pipelines.md` now require smoke-invoking
  each extracted script through the exact entrypoint the glue calls
  (`python -m ci.promote --help`, `./ci/deploy.sh --dry-run`) as the minimum
  glue verification — the one slice runnable even without a CI runner.

## [0.5.0] — 2026-08-09

### Added
- **`pipeline-authoring` skill** — turns a `cicd-pipeline-design` note into the
  real pipeline-as-code and its step scripts: build once and promote the same
  artifact, pinned/hermetic/idempotent steps, no secrets in the definition, DRY
  across stages, fail-fast ordering matching the design. It is the first
  `-authoring` skill to write real code, so it draws a hard line on how that
  code gets proven: prefer script files over inline scripts, so non-trivial
  step logic is never buried un-testable in the pipeline definition; and a
  production-discipline split where extracted logic (scripts, generators,
  policy code) goes through TDD while the declarative pipeline glue is proven
  by verification — running the real pipeline against a test artifact. Both
  halves defer to `craft`'s `strict-tdd` and `verification` skills rather than
  reimplementing them, named generically so the skill degrades gracefully
  without `craft` installed. Ships with two references:
  `references/pipeline-as-code-hygiene.md` and
  `references/testing-and-verifying-pipelines.md`.
- **`craft-ops-designer` and `craft-ops-author` agents** — a new
  `craft-ops/agents/` directory. `craft-ops-designer` dispatches the matching
  `-design` skill for a domain and writes the design note, read-only over the
  target system. `craft-ops-author` turns that note into real code/config in
  its own worktree, extracting non-trivial step logic under `craft`'s
  `strict-tdd`, verifying the declarative glue by running it, and reusing
  `craft`'s reviewer and verifier agents where present — falling back to their
  underlying skills directly when they aren't.
- **README** — the CI/CD row's `pipeline-authoring` skill marked `Built`; a
  new `## Agents` section describing `craft-ops-designer` and
  `craft-ops-author`. Plugin version bumped to `0.5.0`.

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
