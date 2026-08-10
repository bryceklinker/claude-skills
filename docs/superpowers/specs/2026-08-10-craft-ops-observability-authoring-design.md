# craft-ops — observability-authoring skill (authoring slice 4, final)

*Design spec — 2026-08-10*

## Purpose

Fourth and final authoring slice: **`observability-authoring`** — the skill that turns an
`observability-design` note into the actual observability-as-code. It replicates the proven
`pipeline-authoring` / `infrastructure-authoring` / `deployment-authoring` pattern with
observability-specific content, and **completes the craft-ops suite**: every domain now has both a
design skill and an authoring skill, plus the two-agent team.

Chosen slicing: **one domain per spec.** No agent changes — `craft-ops-author` is generic, so this
skill plugs in unchanged.

## The pattern being replicated (proven in slices 1–3)

- **Authoring = domain guidance over craft's pipeline.** Takes the matching design note as input,
  adds the domain's *how to write it well* rules, and defers the production loop to craft
  (`strict-tdd` / `verification` / `code-style` / `self-review`), named generically so it degrades
  without craft. The `-design` skills stay standalone.
- **The production-discipline split:** real logic → `strict-tdd`; declarative glue → `verification`.
- **Prefer extracted/generated over inline duplication** (the domain form of script-files-not-inline).
- **A minimum, always-runnable verification** even without a full environment: validate/lint the
  declarative artifacts + **entrypoint-smoke-invoke** the extracted scripts.
- **Boundary:** writes the code; defers the design decision upstream; does not reimplement
  TDD/verification.

## The `observability-authoring` skill

Takes an `observability-design` note as input and writes the actual **observability-as-code** —
tool-agnostic (an instrumentation library / OpenTelemetry, dashboards-as-code such as Grafana
Jsonnet/Terraform, an alerting system such as Prometheus/Alertmanager), never naming one as required.

### The production-discipline split, observability form

- **Real logic → craft `strict-tdd`:** metric / SLO / burn-rate computation, custom instrumentation
  helpers, alert-expression generators, and the runtime-lever toggle logic — production code,
  unit-tested with a failing test first.
- **Declarative glue → craft `verification`:** the dashboards-as-code and alert-rule configuration are
  proven by running them — the alert fires on a synthetic/replayed signal that should trip it and
  stays quiet on a healthy one; the dashboard's queries resolve — not by reading the config.

### The minimum, always-runnable verification (carried forward)

Validate/lint the alert rules and dashboard definitions, and **smoke-invoke each extracted script
through the exact entrypoint the pipeline/instrumentation calls** — the always-runnable minimum that
catches a malformed rule, a broken query, or a wrong entrypoint offline, before any live signal.

### Signature observability domain rules

- **Prefer generated/extracted over hand-maintained duplication.** Dashboards and alerts are code —
  templated or generated, version-controlled, reviewed — never clicked together in a UI; instrumentation
  goes through a shared, tested helper, not copy-pasted per call site. Hand-maintained duplication is
  how dashboards drift from reality and alerts rot silently.
- **Prove the alert fires.** An alert rule is *verified* by firing it against a synthetic or replayed
  signal that should trip it — and confirming it stays quiet on a healthy signal — before it is
  trusted. An alert that has never been observed to fire is not verified, no matter how correct the
  expression looks; the failure mode is discovering during the incident that the page never came.
  This is observability's signature emphasis, the direct analog of deployment's prove-the-rollback.
- **Wire the runtime levers for real.** The design decided the observability levers (verbosity,
  sampling rate, trace/span detail); authoring wires them to actual runtime config/flags with their
  default-vs-incident settings, their cost/cardinality guardrails, and their auto-revert — so detail
  can be ramped up and down without a redeploy, as the design intended.
- Plus: **alert on symptoms, not causes** (implement the design's symptom-based, SLO-burn alerting —
  page on user pain, not every internal cause); **cardinality guardrails** honored in the authored
  instrumentation (bounded label sets — never emit an unbounded dimension); **no secrets** in
  dashboard, datasource, or alert configuration (injected, never committed).

### Boundary

- It *writes* the observability-as-code — that is the point of an authoring skill.
- It does **not** re-decide the design (defers upstream to `observability-design`: SLOs, signals,
  alerting strategy, levers were decided there).
- It does **not** reimplement TDD/verification — defers to craft, named generically so it degrades
  without craft.

### Input / output

- **Input:** an `observability-design` note (SLIs/SLOs & error budget, signals to emit, symptom-based
  alerting, runtime levers, health signals for deployment, correlation/context, cost/retention,
  ownership).
- **Output:** the actual observability-as-code — instrumentation (via a tested helper), dashboards
  as code, alert rules proven to fire, the runtime-lever wiring, and any SLO/burn-rate logic covered
  by tests — produced under craft's discipline and committed the craft way.

### references/ (2)

- `observability-as-code-hygiene.md` — the domain rules with their *why*, leading with
  generated/extracted-over-duplication and wire-the-runtime-levers-for-real, then symptom-based
  alerting, cardinality guardrails, no-secrets.
- `testing-and-verifying-observability.md` — the split made concrete: metric/SLO/lever logic →
  `strict-tdd`; dashboards and alert rules → `verification`; the validate + entrypoint-smoke-invoke
  always-runnable minimum; and the observability-specific emphasis: **proving an alert fires by
  actually firing it against a synthetic/replayed signal — an alert never observed to fire is not
  verified.**

## Scope of this build

**Delivered:** the `observability-authoring` skill + 2 references; README row flipped to Built (and
any stale "future `observability-authoring`" prose in `observability-design` retargeted); CHANGELOG
entry + version bump to `0.9.0`; folded into PR #3. Then a behavioral validation (dispatch
`craft-ops-author` on a sample `observability-design` note; confirm dashboards/alerts as code, an
alert proven to fire against a synthetic signal, runtime levers wired to flip without a redeploy,
cardinality guardrails, no secrets, and validate/entrypoint-smoke-invoke verification).

**Deferred (named):** a `.craft-ops.yml` conventions skill (the last named-but-unbuilt piece).

## Success criteria

- `observability-authoring` triggers when turning an observability design note into observability-as-code;
  it produces dashboards/alerts as code, an alert proven to fire by firing it against a synthetic
  signal, runtime levers wired to flip without a redeploy, instrumentation via a tested helper with
  cardinality guardrails, no secrets in config; it verifies via validate + entrypoint-smoke-invoke
  (the always-runnable minimum) and by firing the alert.
- It defers the design to `observability-design` and the production loop to craft (naming the split),
  rather than re-deciding the design or reimplementing TDD.
- README marks `observability-authoring` Built; plugin + marketplace at `0.9.0`; all in PR #3. With
  this, every craft-ops domain has both a design and an authoring skill.
