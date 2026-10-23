---
name: deployment-authoring
description: "Use when turning a deployment design note (from deployment-design) into the actual rollout automation — progressive-delivery config (a canary/blue-green controller such as Argo Rollouts or Flagger), feature-flag wiring, deploy scripts, and health-gate definitions. Opinionated rules: gate and promotion logic visible and runnable, not buried inline; author AND exercise the rollback in a test environment before trusting the forward rollout; health gates are objective thresholds proven by halting on a bad signal; deploy decoupled from release; no secrets in config; honor the designed compatibility window; idempotent. It WRITES the automation and proves it by running it — a test-environment rollout that progresses, halts, and rolls back — with no unit-test suite for deploy scripts unless one carries substantial decision logic. Not for deciding the rollout strategy (deployment-design), nor pipeline, infrastructure, or observability authoring."
---

# Deployment Authoring

Turn a `deployment-design` note into real rollout automation without re-deciding the strategy. Read `deployment.*` and `environments.order` from `.craft-ops.yml` first (`craft-ops-conventions`). If the note is missing, ambiguous, or wrong, send it back to `deployment-design`.

## Prove it by running it

A rollout is tested by rolling out (`PRINCIPLES.md` core 2). In a test environment, observe all three:

1. **It progresses** through its steps on a healthy signal.
2. **It halts** when the signal goes bad — make the metric bad and watch the halt; don't assume it.
3. **It rolls back** — trigger the rollback and confirm the system lands on the prior version. A rollback that has only been read is a guess.

When no test environment is available, the minimum is validating the rollout manifest against the controller's schema (plus its dry-run where supported) and running every deploy script through the exact entrypoint the rollout calls. Say what remains unproven.

Don't write a unit-test suite for deploy scripts by default. A gate script whose threshold logic has many cases — boundaries, missing data points, flapping — can earn a small test, built with craft-code's `strict-tdd` where installed. `references/testing-and-verifying-rollouts.md` has the detail.

## Domain rules

- **Rollback before forward.** The undo is authored and exercised before the forward path is trusted with real traffic.
- **Health gates are objective thresholds** (error rate, latency, saturation, a business metric) evaluated automatically — not a dashboard glance.
- **Gate and promotion logic is visible and runnable** — in a script or the controller's analysis config, not scattered through inline manifest fields. `references/rollout-authoring-hygiene.md`.
- **Deploy is decoupled from release.** Ship dark; flip exposure deliberately, as its own decision.
- **No secrets in the config.**
- **Honor the compatibility window** the design decided (expand-contract, N-1).
- **Idempotent** — re-running does nothing harmful.
- **Only the mechanism the risk needs** — no flags, rings, or gates the design didn't call for.

## Writing it well

Apply craft-code's `code-style` to scripts, commit each piece once it's been run and seen working, commit refactors separately, and send the finished diff to `adversarial-review` and `verification` (`craft-code-reviewer` / `craft-code-verifier` where available). Without craft-code installed, apply the same discipline directly.

## Exit condition

The rollout config, scripts, and rollback path are in the repo; a test-environment rollout was seen progressing, halting on a bad signal, and rolling back (or, without one, the manifest validated and every script run through its entrypoint, with the gap named); reviewed, no secrets, no leftover scaffolding.
