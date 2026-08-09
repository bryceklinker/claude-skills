# Pipeline-as-Code Hygiene — a definition worth trusting

A pipeline definition is code, but it's easy to treat it like configuration nobody really reads: a YAML file people edit by pattern-matching the step above rather than understanding, that accretes inline shell one "just this once" fix at a time until nobody can tell what it actually does without running it. Hygiene is what keeps the definition legible, testable, and safe to change — the properties that let `cicd-pipeline-design`'s decisions (artifact strategy, stage order, secrets boundary) stay true in the actual file instead of eroding one convenient shortcut at a time.

## Table of contents
- Prefer script files over inline scripts
- Build once, promote the same artifact
- Pin every tool version
- Hermetic and idempotent steps
- No secrets in the definition
- DRY across stages
- Fail-fast ordering matching the design
- The pipeline is reviewed like code

## Prefer script files over inline scripts

**Non-trivial step bodies live in version-controlled script files that the pipeline calls — never as inline shell or YAML blocks buried in the step definition.** If a step branches, loops, parses output, or makes more than a one-line decision, extract it to a script under source control and have the pipeline invoke it.

This is the rule everything else in this document assumes, because it's the one that determines whether the rest are even achievable. An inline script is invisible to every tool that makes code trustworthy: it can't be run locally without copy-pasting it out of the YAML first, can't be unit tested because it has no independent existence to target, can't be linted or formatted with the rest of the codebase, and bloats the pipeline definition until the actual control flow — what runs, in what order, gated by what — is buried in a wall of shell. `git diff` on an inline script mixes logic changes with pipeline-structure changes in the same hunk, so a reviewer has to untangle "did the wiring change or did the behavior change" by hand, every time.

Extraction is what moves a step from "hoped correct" to "proven correct": once the logic is a file on disk, it can be run outside the pipeline, given a failing test, and covered by `strict-tdd` like any other production code (see `testing-and-verifying-pipelines.md`). A step that stays inline never crosses that line — it can only ever be verified by re-running the whole pipeline and reading the outcome, which is slower feedback for logic that a unit test would catch in milliseconds. Extraction isn't a style preference; it's the mechanism that makes the production-discipline split in the skill's `SKILL.md` real instead of aspirational.

## Build once, promote the same artifact

**The pipeline produces one immutable, digest-identified artifact and moves that same artifact unchanged across every environment — it never rebuilds per environment.** If the design note already settled the artifact and promotion strategy (see the `cicd-pipeline-design` skill's `promotion.md`), the authored pipeline implements that strategy exactly: one build stage, one digest, reference changes for every later environment transition.

The reason authoring can't quietly deviate from this: every stage after the build — tests, gates, human approval — is a claim about *that specific artifact*. The moment a later environment gets a fresh build instead of the promoted one, every earlier claim becomes a claim about a different, unverified thing wearing the same name.

## Pin every tool version

**Every compiler, runtime, package manager, base image, and action/plugin the pipeline invokes is pinned to an exact version — never `latest`, never a floating tag, never "whatever the runner image ships today."**

An unpinned tool is a hidden input to the build that changes without a corresponding change to the pipeline definition or the source it's building. When the pipeline breaks — or, worse, silently produces a different artifact — because a floating dependency moved out from under it, there's no commit, no diff, no review to point to; the pipeline just quietly started doing something different. Pinning turns every input into something a `git blame` can actually explain.

## Hermetic and idempotent steps

**Steps run in an isolated environment provisioned fresh for that run, and re-running any step — after a transient failure, a retry, or a manual re-trigger — produces the same result without manual cleanup first.**

Hermetic steps close off the same class of hidden-input problem pinning does, but for environment state instead of tool versions: a step that only works because a previous run left a cache, a file, or a partially-created resource behind isn't reliably reproducible, it's dependent on an accident of history. Idempotent steps are what make retries safe to use as a routine recovery mechanism rather than a gamble — a step that fails halfway and leaves the world in a state where re-running it errors out (a resource that already exists, a partially-applied migration) turns every transient failure into a manual incident instead of a re-run.

## No secrets in the definition

**Nothing secret is ever written into the pipeline file, a script it calls, or baked into the built artifact — credentials, tokens, and environment-specific config are injected at run time from a secret store or the environment, not authored into source.**

The pipeline definition is reviewed, diffed, and stored the same way the rest of the codebase is (see "The pipeline is reviewed like code," below) — which means anything written into it is, by construction, visible to everyone with read access to the repo, cached in every clone, and permanent in history even after it's "removed" in a later commit. Injection at run time keeps the secret's exposure limited to the moment it's actually needed, scoped to the systems that need it, and rotatable without touching — or re-reviewing — the pipeline definition itself.

## DRY across stages

**Repeated step logic is factored into a shared script, template, or reusable job — never copy-pasted from one stage into the next.**

Copy-paste is how stages that were identical at authoring time quietly stop being identical: a fix applied to one copy and forgotten in the other, a flag added to the staging deploy step that never made it to the prod deploy step because nobody remembered a third copy existed. A shared script fixed once is fixed everywhere it's called; a duplicated block fixed once is fixed in exactly the one place someone happened to be looking.

## Fail-fast ordering matching the design

**Stages in the authored pipeline run in the order the design note settled on — cheapest and most-likely-to-fail first (see the `cicd-pipeline-design` skill's `stage-ordering.md`) — and the pipeline halts on first failure rather than running every remaining stage regardless.**

Authoring is not the place to re-derive this order; it's the place to implement it faithfully. If the order that falls out naturally while writing the pipeline doesn't match what the design note decided, that's a signal to go back and reconcile with the design — either the note is stale or the authored pipeline drifted — not a license to keep whichever order was more convenient to write.

## The pipeline is reviewed like code

**The pipeline definition and every script it calls go through the same pull-request review the application code does — no jobs clicked together in a CI vendor's UI, no changes pushed directly to the pipeline that bypass the review the rest of the codebase requires.**

Everything above — extraction, pinning, hermeticity, secrets discipline, DRY, ordering — is a convention a reviewer can only enforce if the change is actually visible to them as a diff before it takes effect. A pipeline edited outside the normal review path is a pipeline where these rules are optional by default, because nobody with the authority to say "this violates hygiene" ever sees the change before it runs.
