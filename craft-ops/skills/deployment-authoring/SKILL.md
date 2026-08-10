---
name: deployment-authoring
description: "Use when turning a deployment design note (from deployment-design) into the actual rollout automation — writing the real progressive-delivery config (a canary/blue-green controller such as Argo Rollouts or Flagger), feature-flag wiring, deploy scripts, and health-gate definitions. Applies opinionated authoring rules: prefer extracted scripts over inline rollout logic; author AND prove the rollback path (exercise the undo in a test env) before trusting the forward rollout; health gates are extracted, tested code, not a dashboard glance; deploy is decoupled from release (ship dark, flip deliberately); no secrets in the config; honor the compatibility the design decided; idempotent. It WRITES the rollout automation (unlike deployment-design, which only designs it), but defers the production loop to craft: gate/promotion/flag logic is built under strict-tdd, and the declarative rollout config is proven by verification — validate + entrypoint-smoke-invoke as the minimum, and a rollout run in a test environment. Not for deciding the rollout strategy (that is deployment-design), nor for pipeline, infrastructure, or observability authoring."
---

# Deployment Authoring — write the rollout the design already decided

## Why this exists

A design note is not a running rollout. Left to guesswork, the gap between the two fills in with gate and promotion logic inlined directly into the rollout manifest where it can't be unit-tested, a rollback path nobody has ever actually triggered, and a release flipped to 100% because the forward path "looked fine" in the plan. This skill turns a `deployment-design` note into real, reviewed rollout automation — without re-deciding the design and without hand-waving the discipline that makes the result trustworthy.

Unlike the `-design` skills, it *does* write code — so it leans on craft to write it well.

## Seams

- **Consumes** the `deployment-design` note as input. That note already made the strategy decisions — release strategy, deploy-vs-release decoupling, rollout steps, health gates, rollback/roll-forward plan, compatibility. This skill does not re-decide them.
- **Defers the production loop to craft** — named generically so this skill degrades gracefully without craft installed: `strict-tdd` for gate/promotion/flag logic, `verification` for the declarative rollout config, `code-style` and `self-review` for how it's written and checked.
- **Review and verification** go to `craft-reviewer` / `craft-verifier` where those agents exist.

## The production-discipline split

State it plainly, because the two halves are proven differently:

- **Gate/promotion/flag logic** — health-gate evaluation, promotion/halt decisions, flag-targeting rules, generators, anything with scripting or a decision in it — is production code. It goes through craft `strict-tdd`: a failing test first, then the minimal code to pass it.
- **The declarative rollout config** — the canary/blue-green manifest and its wiring — isn't unit-testable in the same sense. It's proven by craft `verification`: run the rollout in a test env — a canary progresses on a healthy signal, a bad metric halts it, rollback reverts. At minimum, even when no live test env is available, **validate/lint the rollout manifest + entrypoint-smoke-invoke each extracted script through the exact entrypoint the rollout calls is the always-runnable minimum verification**; a tool dry-run is part of it where supported.

This skill's job is to maximize how much lands on the testable side of that split. Every decision pushed out of the declarative rollout config and into an extracted script is more of the deployment covered by strict-tdd instead of resting on "the rollout looked fine."

## Domain rules

**Prefer extracted scripts over inline.** Gate/promotion/flag logic belongs in scripts the rollout calls, never inline in the manifest. Inline logic in a canary/blue-green resource can't be unit-tested, can't be reviewed as a diff of behavior, and can't be reused across environments — it can only be eyeballed. See `references/rollout-authoring-hygiene.md`.

**Author AND prove the rollback path.** Write the reverse operation and *exercise* it — roll back in a test env, observe it revert — before trusting the forward rollout. A rollback path that has only ever been read, never run, is a guess dressed up as a plan. Rollback-first: the undo is proven before the forward path is trusted with real traffic.

Then:

- **Health gates are code, and tested.** The gate logic is extracted, covered by strict-tdd, and evaluated against objective thresholds — error rate, latency, saturation, a business metric. Not a dashboard a human glances at before clicking promote.
- **Deploy is decoupled from release.** Ship dark — get the bits into production behind a flag or unexposed — and flip exposure deliberately, as its own decision. Never conflate the two into a single flip.
- **No secrets in the config.** Rollout manifests, flag configs, and scripts reference secrets by indirection (a secret store, an injected reference) — never hold them in plaintext.
- **Honor the compatibility the design decided.** Expand-contract migrations, N-1 compatible schemas/APIs — whatever the design note settled for the old-and-new-coexist window, the automation respects it rather than assuming a clean cutover.
- **Idempotent, re-runnable.** Re-running the rollout automation with no intervening change is safe; a retried step doesn't double-apply or corrupt state.

Testing/verifying depth is in `references/testing-and-verifying-rollouts.md`.

## Guardrails

- **Do not re-decide the design.** If the design note is missing, ambiguous, or looks wrong, stop and send it back to `deployment-design` rather than deciding the strategy here.
- **Do not reimplement TDD or verification.** Defer to craft's `strict-tdd` and `verification`; this skill supplies the domain rules, not a competing test methodology.
- **Never trust a forward rollout whose rollback you haven't authored and exercised** — not "just this once," not "it's a small change."
- **No secrets in the config, ever.**
- **Health gates are tested code, not a dashboard glance** — no exceptions for "obviously safe" thresholds.

## Exit condition

The rollout config, extracted gate/promotion/flag scripts, and a proven rollback path exist in the repo. The logic is covered by tests written under strict-tdd; the declarative rollout config is verified by validate/lint + entrypoint-smoke-invoke at minimum, and by a rollout run in a test env — canary progresses on a healthy signal, a bad metric halts it, rollback reverts. The rollback was exercised, not just written. All of it is committed the craft way — reviewed, no secrets, compatibility honored, no dead scaffolding left behind.
