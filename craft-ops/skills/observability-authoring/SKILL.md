---
name: observability-authoring
description: "Use when turning an observability design note (from observability-design) into the actual observability-as-code — writing the real instrumentation, dashboards-as-code, alert rules, and runtime-lever wiring. Applies opinionated authoring rules: prefer generated/extracted dashboards-and-alerts-as-code over click-ops; PROVE each alert fires by firing it against a synthetic/replayed signal before trusting it; wire the runtime levers (verbosity/sampling/trace detail) to flip without a redeploy; alert on symptoms not causes; cardinality guardrails (no unbounded labels); no secrets in config. It WRITES the observability-as-code (unlike observability-design, which only designs it), but defers the production loop to craft: metric/SLO/lever logic is built under strict-tdd, and the declarative dashboards/alerts are proven by verification — validate + entrypoint-smoke-invoke as the minimum, and firing the alert on a synthetic signal. Not for deciding what to observe (that is observability-design), nor for pipeline, infrastructure, or deployment authoring."
---

# Observability Authoring — write the observability the design already decided

## Why this exists

A design note is not running instrumentation. Left to guesswork, the gap between the two fills in with dashboards clicked together by hand and never reproduced, alert thresholds copy-pasted between environments until they drift, and an alert nobody has ever actually watched fire. This skill turns an `observability-design` note into real, reviewed observability-as-code — without re-deciding the design and without hand-waving the discipline that makes the result trustworthy.

Unlike the `-design` skills, it *does* write code — so it leans on craft to write it well.

## Seams

- **Consumes** the `observability-design` note as input. That note already made the decisions — SLOs, signals, alerting strategy, the runtime levers to expose. This skill does not re-decide them.
- **Reads `.craft-ops.yml`** for this project's `observability.metrics`, `observability.dashboards`, and `observability.alerts` before authoring — see `craft-ops-conventions`, which records and reads it.
- **Defers the production loop to craft** — named generically so this skill degrades gracefully without craft installed: `strict-tdd` for metric/SLO/burn-rate/lever logic, `verification` for the declarative dashboards and alert rules, `code-style` and `self-review` for how it's written and checked.
- **Review and verification** go to `craft-code-reviewer` / `craft-code-verifier` where those agents exist.

## The production-discipline split

State it plainly, because the two halves are proven differently:

- **Metric/SLO/burn-rate/instrumentation-helper/alert-generator/lever-toggle logic** — anything with a computation or a decision in it — is production code. It goes through craft `strict-tdd`: a failing test first, then the minimal code to pass it.
- **The declarative dashboards-as-code and alert-rule config** — isn't unit-testable in the same sense. It's proven by craft `verification`: fire the alert against a synthetic/replayed signal — it trips on a bad signal, it stays quiet on a healthy one — and confirm dashboard queries resolve. At minimum, even when no live signal replay is available, **validate/lint the alert rules + dashboard definitions + entrypoint-smoke-invoke each extracted script is the always-runnable minimum verification.**

This skill's job is to maximize how much lands on the testable side of that split. Every computation pushed out of the declarative alert/dashboard config and into a shared, tested helper is more of the observability covered by strict-tdd instead of resting on "the dashboard looked right."

## Domain rules

**Prefer generated/extracted over hand-maintained duplication.** Dashboards and alerts are code — generated or extracted, never click-ops or copy-pasted between environments. Instrumentation goes through a shared, tested helper, not ad hoc calls scattered and re-typed at every call site. Hand-maintained duplication drifts the moment one copy changes and the others don't. See `references/observability-as-code-hygiene.md`.

**Prove the alert fires.** Verify an alert rule by firing it against a synthetic or replayed signal that should trip it — and confirm it stays quiet on a healthy one — before trusting it. An alert never observed to fire is not verified; it's a guess dressed up as coverage. This is the observability analog of deployment's prove-the-rollback.

Then:

- **Wire the runtime levers for real.** Verbosity, sampling, and trace-detail levers are wired to runtime config or flags, not left as constants baked into a build. Default-vs-incident settings, cost guardrails, and auto-revert are part of the wiring, so a lever flips without a redeploy.
- **Alert on symptoms, not causes.** Page on what the user or the SLO actually experiences — error rate, latency, saturation — not on an internal cause that may or may not be user-visible.
- **Cardinality guardrails.** Labels are bounded; no unbounded dimension (user ID, raw URL, request ID) goes on a metric label.
- **No secrets in dashboard/datasource/alert config.** Dashboards, datasource definitions, and alert-rule config reference secrets by indirection — never hold them in plaintext.

Testing/verifying depth is in `references/testing-and-verifying-observability.md`.

## Guardrails

- **Do not re-decide the design.** If the design note is missing, ambiguous, or looks wrong, stop and send it back to `observability-design` rather than deciding what to observe here.
- **Do not reimplement TDD or verification.** Defer to craft's `strict-tdd` and `verification`; this skill supplies the domain rules, not a competing test methodology.
- **Never trust an alert you haven't fired against a signal that should trip it** — not "just this once," not "it's an obvious threshold."
- **No secrets in config, ever.**
- **No unbounded-cardinality labels** — no exceptions for "it's probably fine at current scale."

## Exit condition

The instrumentation (via a shared tested helper), dashboards-as-code, alert rules proven to fire, and runtime-lever wiring exist in the repo. Metric/SLO/burn-rate/lever logic is covered by tests written under strict-tdd; the declarative dashboards and alert rules are verified by validate/lint + entrypoint-smoke-invoke at minimum, and by firing each alert against a synthetic or replayed signal — it trips on bad, stays quiet on healthy. All of it is committed the craft way — reviewed, no secrets, bounded cardinality, no dead scaffolding left behind.
