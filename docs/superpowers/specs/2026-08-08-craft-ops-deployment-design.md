# craft-ops — Deployment & release domain (deployment-design skill)

*Design spec — 2026-08-08*

## Purpose

Add the third domain to the `craft-ops` DevOps suite: **Deployment & release**. This build delivers
one skill, `deployment-design`, plus the full deployment-and-release principle set — following the
pattern established by CI/CD (`cicd-pipeline-design`) and IaC (`infrastructure-design`). It is a
**thinking / decision** skill that decides how a new version is released to real traffic and reviews
existing release setups, producing a short design note. It **never performs or authors the rollout**
— that is a future `deployment-authoring` skill.

## The boundary with cicd-pipeline-design

Clean split at "an artifact reaches an environment." `cicd-pipeline-design` owns the pipeline shape
up to promoting a built artifact into an environment (build, gate, promote the same artifact, evidence
the deploy is healthy). `deployment-design` takes over from there: how that version is released to
real traffic — progressive delivery, decoupling deploy from release, health-gated promotion,
blast-radius control, and rollback. At the seam, `deployment-design` cross-references
`cicd-pipeline-design` rather than re-deciding promotion.

## Non-goals

- Does **not** perform or author rollout configuration (feature-flag config, canary specs, service-mesh
  traffic rules, etc.) — that is the deferred `deployment-authoring` skill.
- Does **not** re-decide CI/CD promotion or pipeline shape (defers to `cicd-pipeline-design`), and does
  not build the observability/incident domain or any conventions skill — those remain named stubs.
- Tool-agnostic: names specific tools/techniques only as examples of a category, never as a required
  choice, and hands over no authored config.

## Shape

`craft-ops/skills/deployment-design/` mirrors `cicd-pipeline-design` / `infrastructure-design`: a
thinking phase whose output is a design note, not rollout code. Same design-vs-authoring split,
`-design` naming, generic wording, PRINCIPLES citations, and the scope-down house rule: on a
**targeted change** decide the implicated areas in depth and one-line the rest; on a **new rollout /
whole release strategy** decide them all.

## PRINCIPLES.md — Deployment & release expansion

The current one-line Deployment & release stub is replaced with a full principle set, each citing its
root. Final wording refined during implementation; intent fixed here.

1. **Deploy is not release** — shipping the bits (deploy) is decoupled from exposing the behavior
   (release); a version can run in production without being live to users, via feature flags / dark
   launch. *(expands craft-ops CI/CD principle 5; craft: the domain is independent of how data enters
   or leaves — exposure is a runtime decision, not a build/deploy one.)*
2. **Progressive delivery — widen on a healthy signal** — never flip 100% at once; expose to a small
   blast radius first (a canary, a ring, a traffic percentage) and widen only as real health signals
   stay good. *(craft: judgment is independent and rests on evidence — advance on evidence, not hope.)*
3. **Rollback-first — never ship what you can't cheaply undo** — every release has a fast, rehearsed
   way back (roll back or roll forward), decided before the rollout starts, not improvised during an
   incident. *(craft-ops IaC reversibility / protect-and-migrate.)*
4. **Health-gated promotion; automatic halt on regression** — the rollout advances and aborts on
   objective signals (error rate, latency, saturation, a key business metric), not a human eyeballing
   a dashboard; a regression auto-halts and/or auto-rolls-back. *(craft: "done" rests on evidence from
   the real target.)*
5. **Backward/forward compatibility across the transition** — during a rollout old and new versions
   run at once, so each must tolerate the other (expand-contract; N-1 compatible schemas, APIs,
   messages). *(craft-ops CI/CD promote-the-same-artifact + IaC migrate-don't-teardown; craft: small
   reversible steps.)*
6. **Control the blast radius** — rings (internal → canary → wider); a bad release harms the fewest
   users and is caught while small.
7. **Release is a decision; deploy is routine** — deploying artifacts is continuous and automated;
   turning a release on and widening it is a deliberate, reversible, owned decision.
8. **You can only progressively deliver what you can observe** — the signals that gate a rollout must
   exist before the rollout does. *(previews the observability & incident-response domain.)*
9. **State the why; keep the escape hatch** — inherited verbatim from craft.

The observability & incident-response domain remains a one-line stub.

## The deployment-design skill — what it decides

Nine decision areas (each ties back to a principle):

1. **Release strategy** — canary / blue-green / rolling / ring-based, and why it fits (traffic shape,
   statefulness, infra constraints).
2. **Deploy-vs-release decoupling** — what ships dark vs. what's exposed; the feature-flag / toggle
   plan; who flips the switch.
3. **Rollout steps & blast radius** — the concrete progression (e.g. internal → 1% → 10% → 50% →
   100%), the population at each step, and the pace.
4. **Health gates & abort criteria** — the objective signals that promote each step and the
   thresholds that auto-halt / roll back.
5. **Rollback / roll-forward plan** — the reversible path decided up front: how fast, what it costs,
   and when roll-forward is chosen instead.
6. **Compatibility across the transition** — how old and new coexist (expand-contract for
   schema/API/message/contract); what had to ship in a prior release to make this one safe.
7. **State & data during rollout** — sessions, in-flight work, sticky routing, migrations; ties to the
   IaC durable tier.
8. **Ownership & the release decision** — who starts/advances/aborts, and what gate (automated vs.
   human) precedes widening to prod-at-large.
9. **Evidence of done** — the release is done when it's fully live *and* the health signals held
   through 100% *and* the rollback path was proven available — not when the deploy job finished.

### Output

A short deployment design note saved where the work lives (e.g.
`docs/craft-ops/deployments/YYYY-MM-DD-<name>.md`): the strategy, decoupling, rollout steps, health
gates, rollback, compatibility, state, ownership, and evidence decisions — each with its *why*. Enough
for the future `deployment-authoring` skill to implement.

### Guardrails (mirror the other design skills)

- **YAGNI** — only the release machinery the change actually needs (not every rollout needs canary +
  flags + rings).
- **Never perform or author the rollout here** — that belongs to the authoring skill, behind its own
  review.
- **Prefer the existing shape** — if the current release process already fits the conventions, the
  note is short.
- **Match the note's length to the change** — depth on implicated areas, one line for the rest.
- **Defer to `cicd-pipeline-design` at the seam** — don't re-decide promotion / pipeline shape.

### references/

Mirrors the 3-file split; the SKILL.md cites rather than restates:

- `progressive-delivery.md` — canary / blue-green / rolling / rings, blast-radius widening, and
  health-gating with automatic abort.
- `deploy-vs-release.md` — decoupling deploy from release via flags / dark launch; release as an
  owned decision; who flips the switch.
- `rollback-and-compatibility.md` — rollback-first, roll-forward vs. roll-back, and expand-contract /
  N-1 compatibility across the transition.

## Scope of this build

**Delivered:**
- `PRINCIPLES.md` — the Deployment & release stub replaced with the full ~9-principle set;
  observability remains a one-line stub.
- `deployment-design` skill: `SKILL.md` + the three `references/` docs.
- README domain table: Deployment & release / `deployment-design` marked **Built**;
  `deployment-authoring` added as **Planned**.
- Version bump to `0.3.0` in `plugin.json`, the marketplace entry, and `CHANGELOG.md`.
- Skill-creator behavioral eval loop run after the build.

**Deferred (named, not built):** `deployment-authoring`; observability & incident response;
`pipeline-authoring`; `infrastructure-authoring`; the `.craft-ops.yml` conventions skill.

**Branch:** built directly on `feat/craft-ops-cicd`, folding into the single consolidated PR #3.

## Success criteria

- `PRINCIPLES.md` states the full Deployment & release principle set, each citing its root, including
  deploy-is-not-release, progressive delivery, rollback-first, and health-gated promotion.
- The `deployment-design` skill triggers on release/rollout design and review situations and produces
  a design note covering the nine decision areas — and never performs or authors the rollout.
- The skill defers to `cicd-pipeline-design` at the promotion seam rather than re-deciding it.
- On a targeted change the note is scoped; on a new rollout it covers all nine.
- README marks Deployment & release Built and `deployment-authoring` Planned; the plugin version is
  `0.3.0` across plugin.json, marketplace, and CHANGELOG.
