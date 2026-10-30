---
name: observability-design
description: "Use when standing up observability for a service or feature, defining SLOs/SLIs and alerts, deciding what to instrument (logs/metrics/traces), making a service debuggable, ensuring a deployment has the health signals its gates and rollback need, or designing the runtime levers that ramp observability up and down without a redeploy. Produces a short observability design note — SLOs and error budget, symptom-based alerting, the signals to emit and the question each answers, runtime levers (verbosity/sampling/trace detail) with default vs incident settings and cost guardrails, the health signals deployment consumes, correlation/context, cost/retention, and ownership — each decision with its why. It DESIGNS observability; it never authors the instrumentation, dashboards, or alert configuration (that is observability-authoring). Not for CI/CD pipeline design, infrastructure provisioning, deployment/rollout strategy, or running a live incident — those are other craft-ops skills."
---

# Observability Design

Decide what a service reveals before you need it, so that when something breaks you turn detail up and read facts instead of adding log lines and redeploying. The output is a short design note, not instrumentation or alert config; those go to `observability-authoring`. Read `.craft-ops.yml` first if it exists (`craft-ops-conventions`).

Two seams: the **health signals** defined here are what `deployment-design`'s gates and rollback read, and the **runtime levers** defined here are what `incident-response` turns up first.

Instrument for the SLOs and questions this design names, not everything a library can emit; reuse an existing signal before adding one.

## Areas to account for

For a new service or feature, decide all eight. For a targeted change, go deep on the areas it touches and discharge the rest together in one line.

- **User-facing SLIs, SLOs, and error budget** — from the user's perspective; the budget decides ship-more vs. stabilize. (`references/slos-and-alerting.md`)
- **Signals to emit, and the question each answers** — structured, correlatable logs, metrics, and traces; a signal with no question is cost with no payoff.
- **Symptom-based alerting** — page on user pain (SLO burn), not every internal cause. (`references/slos-and-alerting.md`)
- **Runtime levers** — verbosity, sampling, and trace detail adjustable without a redeploy, scoped narrowly (service, route, tenant, request), with default and incident settings, a cost guardrail, and an automatic revert. (`references/observability-levers.md`)
- **Health signals for deployment** — the specific SLIs, at the granularity a canary needs (sliceable per version, comparable to a baseline), that deployment gates on.
- **Correlation and context** — trace context and shared identifiers (request ID, tenant, version, route) to slice and join signals mid-incident.
- **Cost and retention** — what's sampled, aggregated, and kept how long; cardinality as a budget. (`references/signals-and-cardinality.md`)
- **Ownership** — who owns each SLO and alert, and who's paged when the budget burns.

## Write it down

Save the note under `paths.observability` (e.g. `docs/craft-ops/observability/YYYY-MM-DD-<name>.md`), each decision with its *why*. Length tracks the change. Then hand off to `observability-authoring`.
