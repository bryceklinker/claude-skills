---
name: observability-design
description: "Use when standing up observability for a service or feature, defining SLOs/SLIs and alerts, deciding what to instrument (logs/metrics/traces), making a service debuggable, ensuring a deployment has the health signals its gates and rollback need, or designing the runtime levers that ramp observability up and down without a redeploy. Produces a short observability design note — SLOs and error budget, symptom-based alerting, the signals to emit and the question each answers, runtime levers (verbosity/sampling/trace detail) with default vs incident settings and cost guardrails, the health signals deployment consumes, correlation/context, cost/retention, and ownership — each decision with its why. It DESIGNS observability; it never authors the instrumentation, dashboards, or alert configuration (a separate authoring skill). Not for CI/CD pipeline design, infrastructure provisioning, deployment/rollout strategy, or running a live incident — those are other craft-ops skills."
---

# Observability Design — decide what a service reveals before you need it

## Why this exists

A service you can't observe can't be operated, debugged, or safely deployed. Deciding the SLOs, the signals, the alerts, and the runtime levers once, up front, means that when something breaks you turn detail *up* and read facts instead of guessing under pressure. Skipping this step doesn't remove the decisions — it just defers them to 3 a.m., made once each, badly, one incident at a time.

It is a **thinking** phase, not a doing one. The output is a short design note, not instrumentation code, dashboard JSON, or alert configuration — that is handed off to the `observability-authoring` skill, behind its own review.

## Seams

This skill sits between two other domains and hands each of them exactly what they need:

- **To `deployment-design`:** it defines the **health signals** — the user-facing SLIs — that deployment's health gates and rollback decisions consume. A rollout can only auto-halt or auto-roll-back on a signal this skill decided to emit; a behavior with no signal means deployment is flying blind.
- **To `incident-response`:** it defines the **runtime levers** — verbosity, sampling, trace detail — that incident response turns up during a live incident to gather facts, and back down once calm. This skill designs the dials and their default vs. incident settings; it does not run the incident.

## What it decides

Work from the change's actual observability needs, and settle only what they demand. Each decision below ties back to a principle in `craft-ops/PRINCIPLES.md` ("Observability & incident response").

The eight areas are a **coverage checklist, not a required table of contents.** How much each gets depends on the ask:

- **Standing up observability for a new service or feature:** decide all eight — they're all in play.
- **A targeted change** (adding an alert, tightening an SLO, fixing a lever that never got wired up): go deep on the areas the change actually touches, and dispatch the rest in a **single one-line "not implicated" note** naming them together. The checklist exists so you don't *silently* skip an area that turns out to matter — a one-liner confirming an area is untouched discharges it completely.

- **User-facing SLIs/SLOs & error budget** — define SLIs from the user's perspective, not the system's internals; the error budget they produce is the contract that decides ship-more vs. stabilize. *(Observability 3.)* (see `references/slos-and-alerting.md`)
- **Signals to emit and the question each answers** — structured, correlatable signals (wide events, trace context) chosen for the questions you'll actually ask under pressure, not a hopeful dashboard built for calm days. Every signal earns its place by naming the question it answers. *(Observability 5.)*
- **Alert on symptoms, not causes** — page a human only on user-facing pain (SLO burn), not on every internal cause; noise is what makes real pages get ignored. *(Observability 2.)* (see `references/slos-and-alerting.md`)
- **Observability levers (runtime ramp up/down)** — the runtime-adjustable dials (verbosity, sampling rate, trace/span detail, debug logging), scoped as narrowly as possible (service, route, tenant, request), with their default setting and their incident setting, plus the cost guardrail that brings them back down. This is the mechanism `incident-response` reaches for first. *(Observability 4 — the precondition for mitigate-before-you-diagnose.)* (see `references/observability-levers.md`)
- **Health signals for deployment** — the specific SLIs, at the specific granularity, that `deployment-design`'s health gates and rollback thresholds will read. Named explicitly, not left implicit in the SLO list above — deployment can only gate on a signal this skill decided exists. *(Observability 1 — the precondition for safe deployment.)*
- **Correlation & context** — trace context and shared identifiers (request ID, tenant, version, route) that let signals be sliced and joined mid-incident, across services and across the deploy that may have caused the regression. *(Observability 5.)*
- **Cost & retention** — cardinality and retention are a budget, not a free good; decide what's sampled, what's aggregated, and what's kept how long, deliberately rather than emitting everything and hoping the bill sorts itself out. *(Observability 6.)* (see `references/signals-and-cardinality.md`)
- **Ownership & who's paged** — which team or on-call owns each SLO and each alert, and who is paged when the error budget burns. Unowned alerts rot into noise that gets ignored. *(Observability 2 & 3.)*

## Write it down

Save a short design note where the work lives (e.g. `docs/craft-ops/observability/YYYY-MM-DD-<name>.md`): the SLOs, signals, alerts, levers, and deployment health-signal decisions, each with its *why*. If the repo has a `.craft-ops.yml`, read it first for the project's existing observability stack and conventions — see `craft-ops-conventions`, which records and reads it.

## Guardrails

- **YAGNI on instrumentation.** Instrument for the SLOs and questions this design actually names — not everything a library can emit. A signal with no question behind it is cost with no payoff.
- **Never author instrumentation, dashboards, or alert config here.** If you catch yourself writing a metrics client call, a dashboard JSON blob, or an alert-rule YAML, stop — that belongs to the `observability-authoring` skill, behind its own review.
- **Prefer existing signals.** If a signal already answers the question, reuse or extend it before adding a new one. Not every design needs a new metric.
- **Match the note's length to the change.** A targeted alert tweak gets a targeted note — depth on the implicated areas, one line for the rest. Length signals importance; padding every area to equal weight hides which decision actually mattered.

## Exit condition

A written observability design note that accounts for all eight checklist items — SLIs/SLOs & error budget, signals to emit, symptom-based alerting, observability levers, health signals for deployment, correlation & context, cost & retention, and ownership — with the implicated ones decided in depth (each with its *why*) and any the change doesn't touch acknowledged in a single one-line not-implicated note. Nothing silently skipped; nothing padded. Hand off to the `observability-authoring` skill to implement it.
