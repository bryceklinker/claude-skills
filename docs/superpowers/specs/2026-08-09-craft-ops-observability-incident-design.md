# craft-ops — Observability & incident response domain

*Design spec — 2026-08-09*

## Purpose

Add the fourth and final originally-scoped domain to `craft-ops`: **observability &
incident response**. It extends the same opinionated worldview as the three built domains
(CI/CD, Infrastructure as Code, Deployment & release) — a `PRINCIPLES.md` section where
every rule is stated with its *why* and cites its craft / craft-ops root, plus the skills
that apply those principles to a work item.

This domain covers two genuinely different activities, so it ships as **two skills**:

- **`observability-design`** — a *design-note* skill like the other three: decide what a
  service emits and measures (SLOs, signals, alerts, runtime levers) so it can be operated
  and safely deployed.
- **`incident-response`** — a *live-discipline* skill (the operational sibling to craft's
  `systematic-debugging`): run an incident in progress and the blameless review after.

Both are built in this one spec and plan.

## Non-goals

- No orchestrator (craft-ops remains a library of skills reached for per concern).
- `observability-design` does **not** author instrumentation, dashboards, or alert
  configuration — that is a future `observability-authoring` skill, name-stubbed only.
- `incident-response` has **no** authoring split — it is already the live-doing discipline,
  not a design note (explicit decision).
- `incident-response` does not restate root-cause *mechanics*; it defers them to craft's
  `systematic-debugging` and owns the incident-specific wrapper (declare, mitigate, verify,
  blameless postmortem).

## Structural decisions

- Expand the existing one-line `PRINCIPLES.md` stub ("Observability & incident response")
  into a full section with the principle set below.
- Two skills under `craft-ops/skills/`, each mirroring the built skills' shape: SKILL.md
  with a strong trigger description, plus a `references/` directory for the mechanics the
  body cites rather than restates.
- README domain table: both skills marked **Built**; `observability-authoring` marked
  **Planned**; the Observability row no longer says "—".
- Version bump to **0.4.0** (a new domain is a minor bump), CHANGELOG entry, folded into the
  consolidated PR #3.
- After build, run the `skill-creator` behavioral eval loop on each new skill using the
  discriminating-assertion discipline recorded in `tools/craft-ops-evals/README.md` (an
  assertion earns its place only if a strong baseline can plausibly fail it).

## PRINCIPLES.md — Observability & incident response

Final wording is refined during implementation; the intent is fixed here. Each cites its
root.

*Observability*

1. **Observability is a design input, not an afterthought — and the precondition for safe
   deployment.** Instrument as you build. A rollout's health gates and rollback decisions
   can only read signals observability defined; a behavior with no signal means deployment
   is flying blind. *(craft-ops Deployment 8 → its precondition.)*
2. **Alert on symptoms, not causes.** Page a human only on user-facing pain (SLO burn), not
   every internal cause — noise is what makes real pages get ignored. *(craft: done rests on
   evidence from the real target.)*
3. **SLOs and error budgets are the contract.** Define SLIs from the user's perspective; the
   error budget decides ship-more vs. stabilize.
4. **Observability has runtime levers — ramp detail up and down without a redeploy.**
   Verbosity, sampling rate, trace/span detail, and debug logging are runtime-adjustable
   dials (config/flags), scoped as narrowly as possible (service, route, tenant, request),
   so the moment something breaks you turn observation *up* to gather facts instead of
   guessing — and back *down* when calm to control cost. The dials, their default vs.
   incident settings, and their cost guardrails are part of the design. *(craft: find the
   cause with method, not guesses; craft-ops deploy-is-not-release — the capability ships in
   the artifact, the dial is flipped at runtime.)*
5. **Instrument for the questions you'll ask under pressure.** Structured, high-cardinality,
   correlatable signals (wide events, trace context) that let you slice by tenant/version/
   route mid-incident — not hopeful dashboards. *(craft: find the cause with method.)*
6. **Signals cost.** Cardinality and retention are a budget; sample and aggregate
   deliberately. *(craft-ops IaC cost-awareness.)*

*Incident response*

7. **Mitigate before you diagnose.** Stop user harm first with the reversible lever — roll
   back the recent deploy, flip the flag off, shed load, fail over — and turn the
   observability levers up. Root cause comes after the bleeding stops. *(craft-ops Deployment
   rollback-first.)*
8. **Blameless.** Incidents are system and process failures, not people failures; the review
   targets the conditions that allowed it.
9. **Every incident tightens the ratchet.** It yields a tracked action item and, wherever
   possible, a new test or alert that would have caught it. *(craft: every defect becomes a
   test.)*
10. **Find the cause with method, not guesses.** Reproduce, bisect, one hypothesis at a time,
    against the ramped-up signals, keeping a written timeline. *(cross-references craft
    `systematic-debugging`.)*
11. **State the why; keep the escape hatch.** Inherited from craft.

## The `observability-design` skill

A thinking/design skill; the output is a short design note, not instrumentation code.

**Triggers:** standing up observability for a service or feature; defining SLOs/alerts;
deciding what to instrument; making a service debuggable; ensuring a deploy has the health
signals it needs; designing or adjusting the observability levers.

**What it decides (opinionated checklist):**

- **User-facing SLIs/SLOs & error budget** — what "healthy" means from the user's view; the
  budget that governs ship-vs-stabilize.
- **Signals to emit, and the question each answers** — structured/wide-event logs, metrics,
  traces; instrument for the questions you'll actually ask under pressure, not decoration.
- **Alert on symptoms** — page only on SLO burn / user pain; everything else is a dashboard
  or ticket. Severity and routing.
- **Observability levers (runtime ramp up/down)** — the dials, their scope, default vs.
  incident settings, how they flip *without a redeploy*, and the cost/cardinality guardrails
  when turned up.
- **Health signals for deployment** — the explicit SLIs the deployment gates and rollback
  consume; the named seam to `deployment-design` so a rollout can tell healthy from
  unhealthy.
- **Correlation & context** — trace/request IDs and high-cardinality keys to slice by
  tenant/version/route mid-incident.
- **Cost & retention** — cardinality budget, sampling strategy, retention tiers.
- **Ownership / who's paged** — the on-call target per SLO; the seam to `incident-response`.

**Output:** an observability design note saved where the work lives (e.g.
`docs/craft-ops/observability/YYYY-MM-DD-<name>.md`), each decision with its *why*. Reads
`.craft-ops.yml` for project conventions if present.

**Guardrails:** YAGNI — instrument for real questions and SLOs, not everything; never author
the instrumentation, dashboards, or alert config here (that's the future
`observability-authoring`); prefer existing signals; match the note's length to the change.

**references/:** `slos-and-alerting.md` (symptom-based alerting, SLIs/SLOs, error budgets),
`observability-levers.md` (runtime ramp up/down dials, scope, guardrails),
`signals-and-cardinality.md` (wide events, correlation, cost/retention).

## The `incident-response` skill

A live-discipline skill; it runs an incident and its review. It defers root-cause mechanics
to craft's `systematic-debugging`.

**Triggers:** an active incident — prod down, errors spiking, SLO burning, latency elevated,
a bad deploy in progress — and running the postmortem afterward; deciding incident
severity/process.

**The discipline (phases):**

1. **Declare and set roles early** — bias to declaring; a single incident commander owns the
   response, a comms lead owns updates. Ambiguity about who's driving is an outage
   multiplier.
2. **Mitigate before you diagnose** — stop user harm first with the reversible lever
   (rollback, flag off, shed load, fail over) and turn the observability levers up. Seams:
   `deployment-design` rollback-first, `observability-design` levers.
3. **Diagnose with method** — reproduce, narrow, one hypothesis at a time against the
   ramped-up signals, keeping a running timeline. Defers the mechanics to
   `systematic-debugging`.
4. **Resolve and verify on evidence** — confirm the SLO actually recovered from the real
   signal, not by vibes. *(craft: done rests on evidence.)*
5. **Blameless postmortem that ratchets** — a timeline and the contributing conditions
   (system and process, never a person), producing tracked action items and at least one new
   test or alert that would have caught it.

**Output:** live — a running incident timeline plus the mitigation decision; after — a
blameless postmortem with action items and the new test/alert. Save where the work lives
(e.g. `docs/craft-ops/incidents/YYYY-MM-DD-<name>.md`).

**Guardrails:** mitigate before root-causing (don't debug while users bleed); blameless,
always; declare early; the postmortem must produce a ratchet, not just a narrative; defer
root-cause technique to `systematic-debugging`.

**references/:** `incident-command.md` (declaration, severity, roles), `mitigation-first.md`
(reversible levers, ramping observability up), `blameless-postmortem.md` (timeline,
contributing conditions, the action-item + test/alert ratchet).

## Scope of this build

**Delivered:** the full `PRINCIPLES.md` Observability & incident-response section; the
`observability-design` skill + 3 references; the `incident-response` skill + 3 references;
README domain table updated (both Built, `observability-authoring` Planned); CHANGELOG entry
+ version bump to 0.4.0; all folded into PR #3. Then a `skill-creator` behavioral eval loop
on each new skill.

**Deferred (named stubs):** `observability-authoring`. No `incident-response` authoring
split.

## Success criteria

- `PRINCIPLES.md` states the observability & incident-response principles, each citing its
  root, with the runtime-levers principle and the deployment-precondition tie explicit.
- `observability-design` triggers on the described situations and produces a design note
  covering SLOs, signals, symptom-based alerting, **runtime levers**, **health signals for
  deployment**, correlation, cost, and ownership — and never authors instrumentation/config.
- `incident-response` triggers on an active incident and drives declare → mitigate-first →
  method diagnosis (deferring to `systematic-debugging`) → evidence-verified resolve →
  blameless ratcheting postmortem — never restating root-cause mechanics.
- README marks both skills Built and `observability-authoring` Planned; plugin at 0.4.0.
- Each new skill passes a behavioral eval loop whose assertions are discriminating (a strong
  baseline can plausibly fail them).
