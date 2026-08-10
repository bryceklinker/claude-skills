# craft-ops — deployment-authoring skill (authoring slice 3)

*Design spec — 2026-08-10*

## Purpose

Third authoring slice: **`deployment-authoring`** — the skill that turns a `deployment-design` note
into the actual rollout automation. It replicates the proven `pipeline-authoring` / `infrastructure-authoring`
pattern with deployment-specific domain content.

Chosen slicing: **one domain per spec.** This spec is deployment only; `observability-authoring`
follows as its own slice. No agent changes — `craft-ops-author` is generic, so this skill plugs in
unchanged.

## The pattern being replicated (proven in slices 1–2)

- **Authoring = domain guidance over craft's pipeline.** Takes the matching design note as input,
  adds the domain's *how to write it well* rules, and defers the production loop to craft
  (`strict-tdd` / `verification` / `code-style` / `self-review`), named generically so it degrades
  without craft. The `-design` skills stay standalone.
- **The production-discipline split:** real logic → `strict-tdd`; declarative glue → `verification`.
- **Prefer extracted, tested units over inline** (the domain form of script-files-not-inline).
- **A minimum, always-runnable verification** even without a full environment: validate/lint the
  declarative artifact + **entrypoint-smoke-invoke** the extracted scripts through the exact
  entrypoint the glue calls (the lesson from slice 1's behavioral validation).
- **Boundary:** writes the code; defers the design decision upstream; does not reimplement
  TDD/verification.

## The `deployment-authoring` skill

Takes a `deployment-design` note as input and writes the actual **rollout automation** —
tool-agnostic (a canary/blue-green controller such as Argo Rollouts, Flagger, Spinnaker; a
feature-flag system; deploy scripts; health-gate definitions), never naming one as required.

### The production-discipline split, deployment form

- **Real logic → craft `strict-tdd`:** health-gate evaluation, promotion/halt decisions,
  flag-targeting logic, generators, and any scripting — production code, unit-tested with a failing
  test first.
- **Declarative glue → craft `verification`:** the rollout manifests / flag configuration are proven
  by running the rollout against a test environment and observing the real behavior — the canary
  progresses on a healthy signal, a bad metric halts it, the rollback actually reverts.

### The minimum, always-runnable verification (carried from slice 1)

Validate/lint the rollout manifest, and **smoke-invoke each extracted script through the exact
entrypoint the rollout calls** (`./gate.sh --dry-run`, `python -m rollout.promote --help`) — the
always-runnable minimum that catches a wrong module/CLI path or a malformed manifest offline, before
any real rollout. A dry-run of the rollout where the tool supports one is part of this minimum.

### Signature deployment domain rules

- **Prefer extracted scripts over inline.** Health-gate evaluation, promotion/halt decisions, and
  flag-targeting logic live in version-controlled scripts the rollout *calls*, never inline in the
  rollout manifest. Inline logic can't be unit-tested, bloats the manifest, and hides the decision
  from review. Extraction is what turns that logic into the testable side of the split.
- **Author and *prove* the rollback path.** The reverse operation is written and *verified* — rolled
  back in a test environment and observed to actually revert — **before** the forward rollout is
  trusted. Rollback-first: never author a rollout you have not authored and exercised the undo for.
  This is deployment's signature emphasis, the analog of IaC's protect-durable.
- **Health gates are code, and tested.** The promote/halt decision is extracted logic under
  `strict-tdd` — objective thresholds on error rate, latency, saturation, or a business metric, with
  their edge cases pinned by tests — not a human glancing at a dashboard.
- **Deploy is decoupled from release.** The flag/toggle is wired so shipping the bits and exposing
  the behavior are separate actions; the authored artifact ships dark and is flipped on deliberately.
- Plus: **no secrets in the rollout config** (injected at deploy time); **honor the compatibility the
  design decided** (expand-contract / N-1 across the transition); **idempotent / re-runnable** (a
  re-applied rollout definition converges, not double-acts).

### Boundary

- It *writes* the rollout automation — that is the point of an authoring skill.
- It does **not** re-decide the design (defers upstream to `deployment-design`: strategy, gates,
  rollback plan, compatibility were decided there).
- It does **not** reimplement TDD/verification — defers to craft, named generically so it degrades
  without craft.

### Input / output

- **Input:** a `deployment-design` note (rollout strategy, deploy-vs-release decoupling, rollout
  steps, health gates & abort criteria, rollback plan, compatibility, state, ownership, evidence).
- **Output:** the actual rollout automation — the rollout manifest/config, the extracted gate and
  promotion scripts with their tests, the flag wiring, and a proven rollback path — produced under
  craft's discipline and committed the craft way.

### references/ (2)

- `rollout-authoring-hygiene.md` — the domain rules with their *why*, leading with
  extracted-scripts-over-inline and author-and-prove-the-rollback-path, then health-gates-as-code,
  deploy-decoupled-from-release, no-secrets, honor-compatibility, idempotent.
- `testing-and-verifying-rollouts.md` — the split made concrete: gate/promotion/flag logic →
  `strict-tdd`; rollout manifests → `verification` by running the rollout in a test env; the
  validate + entrypoint-smoke-invoke always-runnable minimum; and proving the rollback path by
  actually exercising it (a rollout whose undo has never been run is not verified).

## Scope of this build

**Delivered:** the `deployment-authoring` skill + 2 references; README row flipped to Built (and any
stale "future `deployment-authoring`" prose retargeted); CHANGELOG entry + version bump to `0.8.0`;
folded into PR #3. Then a behavioral validation (dispatch `craft-ops-author` on a sample
`deployment-design` note; confirm extracted-and-tested gate logic, a proven rollback path,
deploy-decoupled-from-release, no secrets, and validate/entrypoint-smoke-invoke verification).

**Deferred (named):** `observability-authoring` (its own slice); a `.craft-ops.yml` conventions skill.

## Success criteria

- `deployment-authoring` triggers when turning a deployment design note into rollout automation; it
  produces the rollout config plus extracted gate/promotion scripts covered by strict-tdd tests, a
  rollback path authored and proven by exercising it, deploy decoupled from release, no secrets in
  the config; it verifies via validate + entrypoint-smoke-invoke (the always-runnable minimum) and a
  rollout run in a test environment.
- It defers the design to `deployment-design` and the production loop to craft (naming the split),
  rather than re-deciding the design or reimplementing TDD.
- README marks `deployment-authoring` Built; plugin + marketplace at `0.8.0`; all in PR #3.
