---
name: observability-authoring
description: "Use when turning an observability design note (from observability-design) into the actual observability-as-code — writing the real instrumentation, dashboards-as-code, alert rules, and runtime-lever wiring. Applies opinionated authoring rules: dashboards and alerts as code, never click-ops or copy-paste; PROVE each alert fires by firing it against a synthetic/replayed signal (and stays quiet on a healthy one) before trusting it; wire the runtime levers (verbosity/sampling/trace detail) to flip without a redeploy; alert on symptoms not causes; cardinality guardrails (no unbounded labels); no secrets in config. It WRITES the observability-as-code (unlike observability-design, which only designs it) and proves it by running it — rules validated, queries resolving to real data, alerts fired — with no separate unit-test suite for generator scripts unless one carries substantial computation. Not for deciding what to observe (that is observability-design), nor for pipeline, infrastructure, or deployment authoring."
---

# Observability Authoring

Turn an `observability-design` note into real observability-as-code without re-deciding what to observe. Read `observability.*` from `.craft-ops.yml` first (`craft-ops-conventions`). If the note is missing, ambiguous, or wrong, send it back to `observability-design`.

## Prove it by running it

Observability is tested by watching it work (`PRINCIPLES.md` core 2):

- **Validate the rules and dashboards** with the backend's own tools (`promtool check rules`, `amtool config check`, the dashboard tool's lint) and run any generator script through its real entrypoint.
- **Every dashboard query resolves to real data** — not an empty series.
- **Every alert fires** against a synthetic or replayed signal that should trip it, and stays quiet on a healthy one. An alert never seen firing is a guess; one that fires on everything is noise.
- **Every runtime lever flips** without a redeploy, and you see the change in the emitted signals.

Don't write a unit-test suite for generator or lever scripts by default. A burn-rate or SLO computation with real edge cases (empty windows, missing points, boundary flapping) can earn a small test, built with craft-code's `strict-tdd` where installed. `references/testing-and-verifying-observability.md` has the detail.

## Domain rules

- **As code, not click-ops.** Dashboards and alerts live in the repo, generated or declared once, never copy-pasted between environments. `references/observability-as-code-hygiene.md`.
- **Instrumentation through one shared helper** where the same fields are emitted in many places — not before.
- **Alert on symptoms** — error rate, latency, saturation, SLO burn — not internal causes.
- **Bounded cardinality** — no user IDs, raw URLs, or request IDs as metric labels.
- **Levers wired to runtime config or flags**, with default and incident settings and a way back down.
- **No secrets in dashboard, datasource, or alert config.**
- **Only the signals the design names** — a signal with no question behind it is cost with no payoff.

## Writing it well

Apply craft-code's `code-style` to scripts, commit each piece once it's been run and seen working, commit refactors separately, and send the finished diff to `adversarial-review` and `verification` (`craft-code-reviewer` / `craft-code-verifier` where available). Without craft-code installed, apply the same discipline directly.

## Exit condition

Instrumentation, dashboards, alert rules, and lever wiring are in the repo; rules validated, queries resolve, each alert was seen firing on a bad signal and quiet on a healthy one, and each lever flipped at runtime; reviewed, no secrets, bounded cardinality, no leftover scaffolding.
