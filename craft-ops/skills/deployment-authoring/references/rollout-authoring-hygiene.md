# Rollout Authoring Hygiene — automation that earns the traffic it's given

A rollout definition is the last thing standing between a design note's decisions and real user traffic, and it's easy to let that gap fill in with shortcuts: gate logic typed straight into the canary resource because it's "just a threshold," a rollback section that exists in the YAML but has never actually been run, a release flipped to 100% the moment the forward path "looked fine." Hygiene here isn't cosmetic — it's the set of structural habits that keep the automation testable, reversible, and honest about what it's actually proven, instead of a manifest that only looks trustworthy until the first bad release. This document makes the domain rules from the skill's `SKILL.md` concrete, each with the failure it exists to prevent.

## Table of contents
- Prefer extracted scripts over inline
- Author and prove the rollback path
- Health gates are code and tested
- Deploy decoupled from release
- No secrets in the config
- Honor the compatibility the design decided
- Idempotent and re-runnable

## Prefer extracted scripts over inline

**Gate evaluation, promotion/halt decisions, and flag-targeting logic live in scripts or programs the rollout calls — never as inline shell, templated expressions, or embedded rules buried in the canary/blue-green resource itself.**

Inline logic in a rollout manifest is invisible to everything that makes code trustworthy: it can't be unit-tested because it has no independent existence to target, can't be run locally to check an edge case, and can't be reviewed as a diff of *behavior* because it's tangled up with the diff of *wiring*. A reviewer looking at a changed threshold buried in a manifest attribute has no way to tell whether it was tested against the boundary condition that actually matters, or just typed in and hoped for. Extraction is what moves that decision from "hoped correct" to "proven correct": once the gate or promotion logic is a file on disk, it goes through `strict-tdd` like any other production code, with the edge cases — a metric exactly at threshold, a missing data point, a flag targeting rule that has to resolve a conflicting override — pinned down by tests instead of left to whatever the dashboard happened to show the day someone eyeballed it. This is the rule everything else in this document assumes, because it's the one that determines how much of the rollout is actually covered by tests versus resting entirely on a human reading a manifest and reasoning it looks fine.

## Author and prove the rollback path

**The reverse operation — how the rollout undoes a bad release — is written *and exercised*: rolled back in a test environment, observed to actually revert, before the forward rollout is trusted with real traffic. Rollback-first: the undo is proven before the forward path earns any confidence at all.**

A rollback path that exists only as YAML nobody has ever triggered is a plan, not a capability — it carries the same false confidence as a backup that has never been restored from. The moment it's needed is the worst possible moment to discover that the previous revision's config drifted, that a migration it depends on isn't actually reversible, or that the automation's `abort` step silently no-ops on this particular controller version. None of that shows up by reading the manifest; all of it shows up on the first real run. A rollout whose undo has never been run is not a safety net, it's an outage waiting for the first bad release — the forward path can only be trusted with production traffic once its reverse has already been proven to work, in a real environment, under real conditions. This is why rollback-first outranks every other rule here: extracted, tested gate logic and decoupled deploy/release are what make a *good* rollout, but an unproven rollback is what makes a *survivable* one, and survivability is the property this document exists to protect.

## Health gates are code and tested

**Promotion and halt decisions evaluate against objective, numeric thresholds — error rate, latency, saturation, a business metric — defined and covered by tests, with edge cases (a metric exactly at the threshold, a missing or delayed data point, a metric that flaps across the boundary) pinned down explicitly. A human glancing at a dashboard before clicking promote is not a health gate.**

A dashboard glance is unrepeatable and unreviewable: it depends on which panel the person happened to be looking at, what "looks fine" meant to them in that moment, and whether they noticed a metric that was trending toward the threshold rather than already past it. It leaves no artifact a reviewer can check, and it means the exact same rollout can pass on Tuesday and fail on Wednesday for reasons that have nothing to do with the release. Extracted, tested gate code makes the decision reproducible and inspectable — the same inputs always produce the same promote/halt outcome, and the edge cases that determine *where* the line actually falls are pinned by a test instead of by whoever was on call. This is the health-gate instance of "prefer extracted scripts over inline," made explicit because it's the rule most likely to get skipped under the excuse that "the threshold is obvious."

## Deploy decoupled from release

**Getting new code into production and exposing it to users are two separate, deliberate actions. The rollout ships dark — bits deployed behind a flag, unexposed, or with zero traffic weight — and a human or the automation flips exposure as its own distinct decision, never conflated into a single deploy-and-release step.**

Conflating the two means every deploy is also an exposure event, which means every deploy carries release-level risk even when the change is trivial, and it means there's no way to get a build running in production — to smoke it, warm caches, watch its resource footprint — without simultaneously putting it in front of users. Decoupling turns "did the deploy succeed" and "should this be exposed" into two questions that can be answered independently: a build can go out, sit dark, get inspected, and only then get flipped on, with the flip itself gated by whatever the design decided. Shipping is not exposing, and a rollout that treats them as the same step has quietly removed the option to catch a problem between the two.

## No secrets in the config

**Rollout manifests, flag configs, and the scripts they call reference secrets by indirection — a secret-store path, an injected environment variable, a reference resolved at deploy time — never a plaintext credential, token, or connection string authored directly into any of it.**

A rollout definition is reviewed, diffed, and stored the same way the rest of the codebase is, which means anything written into it in plaintext is visible to everyone with read access to the repo, cached in every clone, and permanent in history even after a later commit "removes" it. Injection at deploy time keeps a secret's exposure scoped to the moment it's actually needed and the system that needs it, and keeps rotation a matter of updating the secret store rather than a rollout-definition change that has to be re-reviewed. This is the same failure mode "no secrets in the pipeline" and "no secrets in IaC" both guard against, applied to the last stage before traffic — the stage where a leaked secret has the shortest possible distance to real production access.

## Honor the compatibility the design decided

**Whatever compatibility window the design note settled — expand-contract for a schema or API change, N-1 compatibility between old and new versions during the rollout — the automation respects it across the entire transition, not just at the start and end states.**

A progressive rollout means old and new versions of a service, and old and new shapes of whatever they share, coexist for the full duration of the canary or blue-green window — which can be minutes or days depending on how cautious the steps are. Authoring automation that only accounts for the before-state and after-state, and assumes the transition itself is instantaneous, breaks the moment a canary step holds at partial traffic for any meaningful length of time: old instances reading a field the new schema removed, or new instances writing a shape the old code can't parse. The design note already decided how the old and new sides coexist during that window; authoring's job is to make sure every step of the rollout — not just the final promote — actually honors it, rather than re-deciding compatibility on the fly because the manifest made a shortcut convenient.

## Idempotent and re-runnable

**Re-running the rollout automation with nothing else having changed — after a transient failure, a retry, or a manual re-trigger — converges to the same state without double-acting: it doesn't re-fire a promotion that already happened, re-apply a migration a second time, or duplicate a notification.**

Rollouts fail partway through for reasons that have nothing to do with the release itself — a network blip, a controller restart, a flaky health check that timed out rather than genuinely failed. If retrying the automation isn't safe, every one of those transient failures becomes a manual incident: someone has to figure out exactly what state the rollout was left in before they dare re-run it. Idempotence is what keeps "just re-run it" a safe, boring answer instead of a gamble — a promotion step that checks whether it already promoted before acting, a rollback that checks the current revision before reverting, a flag flip that's a set rather than a toggle. This is the same convergence property that makes an IaC apply-twice a no-op, applied to the moment where the cost of getting it wrong is a duplicated action against live traffic instead of a spurious diff.
