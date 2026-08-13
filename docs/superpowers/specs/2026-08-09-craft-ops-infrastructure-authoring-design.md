# craft-ops — infrastructure-authoring skill (authoring slice 2)

*Design spec — 2026-08-09*

## Purpose

Spec 1 shipped and validated the first authoring skill (`pipeline-authoring`) plus the two agents.
This spec is the second authoring slice: **`infrastructure-authoring`** — the skill that turns an
`infrastructure-design` note into the actual infrastructure-as-code. It replicates the proven
`pipeline-authoring` pattern with IaC-specific domain content.

Chosen slicing: **one domain per spec.** This spec is IaC only; `deployment-authoring` and
`observability-authoring` follow as their own slices. No agent changes — `craft-ops-author` was
written generically, so this skill plugs into it unchanged.

## The pattern being replicated (from `pipeline-authoring`, proven in Spec 1)

- **Authoring = domain guidance over craft's pipeline.** Takes the matching design note as input,
  adds the domain's *how to write it well* rules, and defers the production loop to craft
  (`strict-tdd` / `verification` / `code-style` / `self-review`), named generically so it degrades
  without craft. The `-design` skills stay standalone.
- **The production-discipline split:** real logic → `strict-tdd`; declarative glue → `verification`.
- **Prefer extracted, reusable units over inline duplication** (the domain form of
  script-files-not-inline).
- **A minimum, always-runnable verification** that catches broken wiring even without a full
  environment (Spec 1's entrypoint smoke-invoke; the IaC form is `validate` + `plan`).
- **Boundary:** writes the code (the point); defers the design decision upstream; does not reimplement
  TDD/verification.

## The `infrastructure-authoring` skill

Takes an `infrastructure-design` note as input and writes the actual IaC — tool-agnostic
(Terraform / Pulumi / CloudFormation / Bicep / CDK / etc.), never naming one as required.

### The production-discipline split, IaC form

- **Real logic → craft `strict-tdd`:** policy-as-code checks (OPA/Sentinel/etc.), modules with
  computed values, generators, and any scripting around the IaC — production code, unit-tested with a
  failing test first.
- **Declarative resources → craft `verification`:** the resource definitions themselves are proven by
  running the tool — `validate` + `plan`/diff reviewed, then `apply` against a throwaway/sandbox
  environment observed for convergence — not by reasoning about the config.

### The minimum, always-runnable verification (Spec 1 lesson, IaC form)

`validate` + `plan` is the always-runnable minimum: it catches broken references, type errors, bad
interpolations, and unexpected destroy/replace *offline, before any apply* — the IaC analog of Spec
1's requirement to smoke-invoke each script through its real entrypoint. The plan is a **diff you must
read**, not skim. Whenever a real environment to `apply` against isn't available, `validate` + `plan`
+ reading the plan is the verification that still must happen.

### Signature IaC domain rules

- **Prefer small composable modules over duplicated resource blocks.** The IaC analog of
  script-files-not-inline: extract and parameterize reusable modules; never copy-paste resource blocks
  per environment. Duplication is how one environment silently drifts from another.
- **Never co-locate a durable resource inside a compute unit.** A durable resource (db, object store,
  queue, topic, bus) is defined in its **own composable unit** with its own lifecycle — never as a
  module/construct/member *within* a compute unit (instance, container, function, cluster, ASG/MIG).
  Compute units receive **references** to durable resources (IDs, ARNs, endpoints, connection info)
  passed in as inputs; they never create them. *Why:* compute is disposable and gets
  destroyed/replaced/recreated routinely; a durable resource sharing that lifecycle can be torn down
  with it. Separating the units makes "destroy the compute" inherently safe and the durable resource's
  lifecycle independent. This is the structural companion to *protect durable resources* and
  *review-before-apply*.
- **Protect durable resources.** The durable tier gets lifecycle guards (`prevent_destroy`-style) and
  migrate-not-teardown; it is never destroyed or replaced in place.
- **Review the plan before every apply.** The signature IaC gate: the plan's first job is to catch a
  destroy/replace of a durable resource — or a durable resource caught inside a compute unit's
  lifecycle — before it happens.
- **Remote, locked, sensitive state.** Never local state; state is remote and locked; no secrets in
  code *or* state (injected via a secret manager).
- **Idempotent / convergent, pinned, no manual drift.** Apply-twice is a no-op; provider and module
  versions are pinned; nothing is hand-edited outside the code (import, don't console-tweak).

### Boundary

- It *writes* the IaC — that is the point of an authoring skill.
- It does **not** re-decide the design (defers upstream to `infrastructure-design`: resource tiers,
  module boundaries, state strategy, review-before-apply were decided there).
- It does **not** reimplement TDD/verification — defers to craft, named generically so it degrades
  without craft.

### Input / output

- **Input:** an `infrastructure-design` note (resource tiers disposable-vs-durable, module boundaries,
  state strategy, the change's shape).
- **Output:** the actual IaC — composable modules with durable and compute resources in separate
  units, any policy/generator logic covered by tests, provider versions pinned, state remote/locked,
  no secrets — produced under craft's discipline and committed the craft way.

### references/ (2)

- `iac-authoring-hygiene.md` — the domain rules with their *why*, leading with
  modules-over-duplication and the never-co-locate-durable-in-compute rule, then protect-durable,
  remote-locked-sensitive-state, pinned providers, no-manual-drift.
- `testing-and-verifying-infrastructure.md` — the split made concrete: policy/module logic →
  `strict-tdd`; declarative resources → `verification` via `validate`/`plan`/apply-to-sandbox;
  `validate` + `plan` as the always-runnable minimum verification and the plan-is-a-diff-you-must-read
  rule; the durable-resource destroy/replace (and co-location) guard.

## Scope of this build

**Delivered:** the `infrastructure-authoring` skill + 2 references; README row flipped to Built;
CHANGELOG entry + version bump to `0.6.0`; folded into PR #3. Then a behavioral validation (dispatch
`craft-ops-author` on a sample `infrastructure-design` note; confirm modules-over-duplication,
durable/compute separation, protect-durable guards, pinned providers, no secrets in code/state, and
`validate`/`plan` verification).

**Deferred (named):** `deployment-authoring`, `observability-authoring` (their own slices); a
`.craft-ops.yml` conventions skill.

## Success criteria

- `infrastructure-authoring` triggers when turning an IaC design note into infrastructure code; it
  produces composable modules (durable and compute resources in *separate* units, compute referencing
  durable by input), any policy/generator logic covered by strict-tdd tests, provider versions pinned,
  remote/locked state, no secrets in code or state; it verifies via `validate`/`plan` (the
  always-runnable minimum) and apply-to-sandbox, and reviews the plan before apply.
- It defers the design to `infrastructure-design` and the production loop to craft (naming the split),
  rather than re-deciding the design or reimplementing TDD.
- README marks `infrastructure-authoring` Built; plugin + marketplace at `0.6.0`; all in PR #3.
