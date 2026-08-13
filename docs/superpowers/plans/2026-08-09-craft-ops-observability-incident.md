# craft-ops Observability & incident response domain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring either `SKILL.md`, also use **superpowers:writing-skills** for frontmatter, trigger-description, and progressive-disclosure structure.

**Goal:** Add the Observability & incident response domain to `craft-ops`: expand `PRINCIPLES.md` with the full principle set and ship two skills — `observability-design` (a design-note skill) and `incident-response` (a live-discipline skill) — bumping the plugin to `0.4.0` and folding into PR #3.

**Architecture:** Extends the existing `craft-ops/` plugin, mirroring the three built domains exactly. `observability-design` follows the `-design` thinking-skill shape (design note + `references/`). `incident-response` is a live-discipline skill paralleling craft's `systematic-debugging` (phased runbook + `references/`), and defers root-cause mechanics to `systematic-debugging`. No new plugin, no orchestrator, no `incident-response` authoring split.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin/marketplace manifests. No application code. Validation is structural: YAML-frontmatter parse, required-section/keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Two skills, named exactly `observability-design` and `incident-response`, under `craft-ops/skills/`.
- `observability-design` **never authors** instrumentation, dashboards, or alert configuration — that is a future `observability-authoring` skill (name-stub only). Use generic wording; never tool-specific product names as the deliverable.
- `incident-response` has **no authoring split** and **defers root-cause mechanics to craft's `systematic-debugging`** rather than restating them.
- Two requirements are FIRST-CLASS in `observability-design` and must be explicit checklist items: **runtime observability levers** (ramp detail up/down without a redeploy) and **health signals for deployment** (the SLIs deployment gates/rollback consume).
- Every strict rule is stated with its *why*, matching the suite's voice; cite the craft / craft-ops root where the spec gives one.
- Follow the spec verbatim for principle text and the skill checklists: `docs/superpowers/specs/2026-08-09-craft-ops-observability-incident-design.md`.
- Bump plugin to `0.4.0` (new domain = minor bump); add a CHANGELOG entry; update the README domain table.
- Commit after every task. New files live under `craft-ops/`. Build on branch `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/observability-design/SKILL.md`
- `craft-ops/skills/observability-design/references/slos-and-alerting.md`
- `craft-ops/skills/observability-design/references/observability-levers.md`
- `craft-ops/skills/observability-design/references/signals-and-cardinality.md`
- `craft-ops/skills/incident-response/SKILL.md`
- `craft-ops/skills/incident-response/references/incident-command.md`
- `craft-ops/skills/incident-response/references/mitigation-first.md`
- `craft-ops/skills/incident-response/references/blameless-postmortem.md`

Modified:
- `craft-ops/PRINCIPLES.md` — expand the observability stub into a full section; update "Coming domains".
- `craft-ops/README.md` — domain table (both skills Built, `observability-authoring` Planned) + a short prose paragraph.
- `craft-ops/CHANGELOG.md` — `0.4.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.3.1` → `0.4.0`.

Independence for parallel execution: **Task 1 (principles) lands first** — both skills cite principle names from it. After Task 1, **Tasks 2+3 (observability) and 4+5 (incident) are independent** and may run in parallel (they touch disjoint skill directories; the cross-skill seams are by name only, fixed in this plan). **Task 6 (docs/version) lands after the skills exist**; Task 7 is controller verification.

---

### Task 1: PRINCIPLES.md — Observability & incident response section

**Files:**
- Modify: `craft-ops/PRINCIPLES.md` (replace the observability stub bullet with a full section; update "Coming domains")

**Interfaces:**
- Produces: the eleven numbered principles both skills cite by title.

- [ ] **Step 1: Add the full principles section**

In `craft-ops/PRINCIPLES.md`, add a new `## Observability & incident response` section (placed after the `## Deployment & release` section, before `## Coming domains`), formatted like the Deployment section (`### N. <title>` + a paragraph + an *(citation)* where the spec gives one). Use the eleven principles from the spec verbatim in intent:

1. **Observability is a design input, not an afterthought — and the precondition for safe deployment.** *(craft-ops Deployment 8 → its precondition.)*
2. **Alert on symptoms, not causes.** *(craft: done rests on evidence from the real target.)*
3. **SLOs and error budgets are the contract.**
4. **Observability has runtime levers — ramp detail up and down without a redeploy.** *(craft: find the cause with method, not guesses; craft-ops deploy-is-not-release.)*
5. **Instrument for the questions you'll ask under pressure.** *(craft: find the cause with method.)*
6. **Signals cost.** *(craft-ops IaC cost-awareness.)*
7. **Mitigate before you diagnose.** *(craft-ops Deployment rollback-first.)*
8. **Blameless.**
9. **Every incident tightens the ratchet.** *(craft: every defect becomes a test.)*
10. **Find the cause with method, not guesses.** *(cross-references craft `systematic-debugging`.)*
11. **State the why; keep the escape hatch.** *(craft.)*

- [ ] **Step 2: Update the "Coming domains" section**

The observability stub is now a full section, so all four originally-scoped design domains are covered. Rewrite `## Coming domains` so it no longer lists observability as a stub — state that the four design domains are complete and what remains scaffolded is the authoring skills (`pipeline-authoring`, `infrastructure-authoring`, `deployment-authoring`, `observability-authoring`). Keep the closing *Lineage* line.

- [ ] **Step 3: Verify the section and citations are present**

Run: `grep -c '^### ' craft-ops/PRINCIPLES.md` — expected: increased by 11 vs. before (record the before-count first with the same command on a fresh checkout if unsure; the observability section adds 11 `### ` headers).
Run: `grep -iE 'runtime levers|precondition for safe deployment|mitigate before|blameless|tightens the ratchet' craft-ops/PRINCIPLES.md` — expected: all five phrases appear.
Run: `grep -i 'observability & incident response' craft-ops/PRINCIPLES.md` — expected: the new section header appears; the old `*(stub)*` line is gone (`! grep -q 'incident response.*stub' craft-ops/PRINCIPLES.md`).

- [ ] **Step 4: Commit**

```bash
git add craft-ops/PRINCIPLES.md
git commit -m "feat(craft-ops): add Observability & incident response principles"
```

---

### Task 2: The `observability-design` skill

**Files:**
- Create: `craft-ops/skills/observability-design/SKILL.md`

**Interfaces:**
- Consumes: principle titles from Task 1; reference filenames from Task 3 (`slos-and-alerting.md`, `observability-levers.md`, `signals-and-cardinality.md`).
- Produces: a skill named `observability-design` emitting an observability design note.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/observability-design/SKILL.md` with this frontmatter (name fixed; description mirrors the other `-design` skills' trigger style and states the hard boundary):

```yaml
---
name: observability-design
description: "Use when standing up observability for a service or feature, defining SLOs/SLIs and alerts, deciding what to instrument (logs/metrics/traces), making a service debuggable, ensuring a deployment has the health signals its gates and rollback need, or designing the runtime levers that ramp observability up and down without a redeploy. Produces a short observability design note — SLOs and error budget, symptom-based alerting, the signals to emit and the question each answers, runtime levers (verbosity/sampling/trace detail) with default vs incident settings and cost guardrails, the health signals deployment consumes, correlation/context, cost/retention, and ownership — each decision with its why. It DESIGNS observability; it never authors the instrumentation, dashboards, or alert configuration (a separate authoring skill). Not for CI/CD pipeline design, infrastructure provisioning, deployment/rollout strategy, or running a live incident — those are other craft-ops skills."
---
```

Body mirrors `deployment-design/SKILL.md`'s shape:
- `# Observability Design — decide what a service reveals before you need it`
- `## Why this exists` — a service you can't observe can't be operated or safely deployed; deciding the SLOs, signals, alerts, and levers once, up front, means that when something breaks you turn detail *up* and read facts instead of guessing. A thinking phase; output is a design note, not instrumentation code.
- `## Seams` — names the two seams: it **defines the health signals `deployment-design`'s gates and rollback consume**, and **the levers `incident-response` turns up** during an incident.
- `## What it decides` — the eight checklist items from the spec, each a bullet tied to a principle, with `observability-levers` and `health-signals-for-deployment` explicit: User-facing SLIs/SLOs & error budget; Signals to emit and the question each answers; Alert on symptoms; **Observability levers (runtime ramp up/down)** (see `references/observability-levers.md`); **Health signals for deployment**; Correlation & context; Cost & retention (see `references/signals-and-cardinality.md`); Ownership/who's paged. SLO/alerting depth in `references/slos-and-alerting.md`.
- `## Write it down` — save an observability design note (e.g. `docs/craft-ops/observability/YYYY-MM-DD-<name>.md`); read `.craft-ops.yml` if present.
- `## Guardrails` — YAGNI (instrument for real questions/SLOs, not everything); **never author instrumentation/dashboards/alert config here**; prefer existing signals; match note length to the change.
- `## Exit condition` — a note covering all eight items (levers and deployment-health-signals included), each with its *why*; hand off to the future `observability-authoring` skill.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('craft-ops/skills/observability-design/SKILL.md').read().split('---')[1]); assert d['name']=='observability-design'; assert 'description' in d; print('OK')"` — expected `OK`. (If PyYAML is missing, eyeball `head -5`.)

- [ ] **Step 3: Verify the boundary and the two first-class items**

Run: `grep -iE 'never author|does not author|not .* author' craft-ops/skills/observability-design/SKILL.md` — expected: the never-author boundary is stated.
Run: `grep -iE 'runtime lever|ramp .* up|without a redeploy' craft-ops/skills/observability-design/SKILL.md` — expected: the levers item is present.
Run: `grep -iE 'health signal|deployment' craft-ops/skills/observability-design/SKILL.md` — expected: the deployment-health-signals seam is present.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/observability-design/SKILL.md
git commit -m "feat(craft-ops): add observability-design skill"
```

---

### Task 3: `observability-design` references

**Files:**
- Create: `craft-ops/skills/observability-design/references/slos-and-alerting.md`
- Create: `craft-ops/skills/observability-design/references/observability-levers.md`
- Create: `craft-ops/skills/observability-design/references/signals-and-cardinality.md`

**Interfaces:**
- Produces: the three files cited by Task 2's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write slos-and-alerting.md**

Cover: SLIs defined from the user's perspective; SLOs and error budgets as the ship-vs-stabilize contract; alert on symptoms (SLO burn / user pain), not causes; multi-window burn-rate alerting vs. static thresholds; severity/routing; why paging on causes creates the noise that gets real pages ignored. Each rule with its *why*.

- [ ] **Step 2: Write observability-levers.md**

Cover: the runtime dials (log verbosity, sampling rate, trace/span detail, debug logging); scoping a lever as narrowly as possible (service, route, tenant, request) so you can turn it up for the blast radius, not the whole fleet; default vs. incident settings; flipping them via runtime config/flags **without a redeploy** (deploy-is-not-release: the capability ships in the artifact, the dial is flipped when needed); cost/cardinality guardrails and auto-revert so a turned-up lever doesn't become a bill or an outage. Each rule with its *why*.

- [ ] **Step 3: Write signals-and-cardinality.md**

Cover: structured/wide events over sparse logs; correlation via trace/request IDs and consistent high-cardinality fields (tenant/version/route) so you can slice mid-incident; instrument for the questions you'll ask under pressure; cardinality and retention as a budget; sampling (head vs. tail) and aggregation strategy. Each rule with its *why*.

- [ ] **Step 4: Verify files exist, non-empty, and are cited**

Run: `for f in slos-and-alerting observability-levers signals-and-cardinality; do p="craft-ops/skills/observability-design/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/observability-design/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for all three.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/skills/observability-design/references/
git commit -m "feat(craft-ops): add observability-design reference conventions"
```

---

### Task 4: The `incident-response` skill

**Files:**
- Create: `craft-ops/skills/incident-response/SKILL.md`

**Interfaces:**
- Consumes: principle titles from Task 1; reference filenames from Task 5 (`incident-command.md`, `mitigation-first.md`, `blameless-postmortem.md`); the seams to `deployment-design`, `observability-design`, and craft `systematic-debugging`.
- Produces: a skill named `incident-response` driving the incident discipline.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/incident-response/SKILL.md` with this frontmatter:

```yaml
---
name: incident-response
description: "Use when an incident is active or imminent — production down, error rate or latency spiking, an SLO burning, a bad deploy in progress — or when running the postmortem afterward, or deciding incident severity and process. Drives the response as a discipline: declare and assign an incident commander early, mitigate before you diagnose (roll back / flip the flag / shed load / fail over, and turn observability levers up), diagnose with method against the ramped-up signals, resolve and verify on real evidence, then run a blameless postmortem that ratchets — tracked action items plus at least one new test or alert that would have caught it. It defers root-cause mechanics to systematic-debugging and owns the incident wrapper. Not for designing observability/SLOs, CI/CD, infrastructure, or deployment strategy — those are other skills."
---
```

Body (a phased live-discipline runbook, paralleling `systematic-debugging`'s shape):
- `# Incident Response — stop the harm, then find the cause`
- `## Why this exists` — under an active incident, the instinct is to debug the interesting puzzle while users are still hurting; the discipline forces mitigation first, method second, and a review that makes the next occurrence less likely. It is a *doing* phase, not a design one.
- `## Seams` — mitigation uses `deployment-design`'s reversible levers (rollback/flag/shed/failover); diagnosis turns up `observability-design`'s levers and reads its signals; the root-cause *mechanics* belong to craft's `systematic-debugging` — this skill owns the incident wrapper around it, not the technique.
- `## The discipline` — the five phases from the spec, each with its *why*: **1. Declare and set roles early** (single incident commander + comms lead; bias to declaring) — see `references/incident-command.md`; **2. Mitigate before you diagnose** (reversible lever + ramp observability up) — see `references/mitigation-first.md`; **3. Diagnose with method** (reproduce/narrow/one hypothesis, running timeline; defer mechanics to `systematic-debugging`); **4. Resolve and verify on evidence** (SLO recovered from the real signal, not vibes); **5. Blameless postmortem that ratchets** (timeline + contributing conditions + tracked action items + at least one new test/alert) — see `references/blameless-postmortem.md`.
- `## Guardrails` — mitigate before root-causing; blameless always; declare early; the postmortem must produce a ratchet, not just a narrative; defer root-cause technique to `systematic-debugging`.
- `## Exit condition` — user harm stopped and verified from the real signal; a blameless postmortem exists with tracked action items and at least one new test or alert.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('craft-ops/skills/incident-response/SKILL.md').read().split('---')[1]); assert d['name']=='incident-response'; assert 'description' in d; print('OK')"` — expected `OK`.

- [ ] **Step 3: Verify the discipline, ratchet, and deferral are present**

Run: `grep -iE 'mitigate before|incident commander|blameless|ratchet|new test or alert' craft-ops/skills/incident-response/SKILL.md` — expected: all present.
Run: `grep -i 'systematic-debugging' craft-ops/skills/incident-response/SKILL.md` — expected: the deferral to systematic-debugging is stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/incident-response/SKILL.md
git commit -m "feat(craft-ops): add incident-response skill"
```

---

### Task 5: `incident-response` references

**Files:**
- Create: `craft-ops/skills/incident-response/references/incident-command.md`
- Create: `craft-ops/skills/incident-response/references/mitigation-first.md`
- Create: `craft-ops/skills/incident-response/references/blameless-postmortem.md`

**Interfaces:**
- Produces: the three files cited by Task 4's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write incident-command.md**

Cover: declaring early and why bias-to-declare beats waiting-to-be-sure; the single incident commander role (decides, delegates, is not also heads-down debugging) and a comms lead; severity levels and what each triggers; hand-off and follow-the-sun for long incidents. Each rule with its *why*.

- [ ] **Step 2: Write mitigation-first.md**

Cover: the reversible levers in priority order (roll back the recent deploy, flip the feature flag off, shed/limit load, fail over) and why reversibility beats a clever forward fix under pressure; turning observability levers **up** immediately to gather facts; when roll-forward is genuinely the only path; not chasing root cause while users are still harmed. Ties to `deployment-design` rollback-first and `observability-design` levers. Each rule with its *why*.

- [ ] **Step 3: Write blameless-postmortem.md**

Cover: a factual timeline; contributing conditions across system and process (never a person); the ratchet — tracked action items AND at least one new test or alert that would have caught it (the operational form of the test-ratchet); why blame suppresses the information a postmortem needs; keeping actions owned and time-bound. Each rule with its *why*.

- [ ] **Step 4: Verify files exist, non-empty, and are cited**

Run: `for f in incident-command mitigation-first blameless-postmortem; do p="craft-ops/skills/incident-response/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/incident-response/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for all three.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/skills/incident-response/references/
git commit -m "feat(craft-ops): add incident-response reference conventions"
```

---

### Task 6: README, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: the two skill names (Tasks 2, 4).

- [ ] **Step 1: Update the README domain table**

In `craft-ops/README.md`, replace the single `| Observability & incident response | — | Planned |` row with three rows:

```markdown
| Observability & incident response | `observability-design` | Built |
| Observability & incident response | `incident-response` | Built |
| Observability & incident response | `observability-authoring` (writes the instrumentation/dashboards/alerts) | Planned |
```

Then add a short prose paragraph after the existing per-skill paragraphs, describing the two new skills in one or two sentences each (observability-design decides SLOs/signals/alerts/runtime-levers and the health signals deployment consumes; incident-response drives declare → mitigate-first → method → verify → blameless ratcheting postmortem, deferring root-cause mechanics to systematic-debugging).

- [ ] **Step 2: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.4.0] — 2026-08-09` section (above `## [0.3.1]`) under `### Added`: the Observability & incident-response principles; the `observability-design` skill + 3 references (call out runtime levers and health-signals-for-deployment); the `incident-response` skill + 3 references (call out mitigate-before-diagnose, blameless ratcheting postmortem, deferral to systematic-debugging); README + version updates.

- [ ] **Step 3: Bump the version**

Set `version` in `craft-ops/.claude-plugin/plugin.json` to `0.4.0`.

- [ ] **Step 4: Verify docs and version**

Run: `grep -q 'observability-design' craft-ops/README.md && grep -q 'incident-response' craft-ops/README.md && grep -q '0.4.0' craft-ops/CHANGELOG.md && python3 -c "import json;assert json.load(open('craft-ops/.claude-plugin/plugin.json'))['version']=='0.4.0'" && echo DOCS_OK` — expected: `DOCS_OK`.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json
git commit -m "docs(craft-ops): mark Observability & incident response built; bump to 0.4.0"
```

---

### Task 7: Final domain verification (controller-run)

**Files:** none — verifies the whole domain against the spec's success criteria.

- [ ] **Step 1: Verify the tree is complete**

Run: `find craft-ops/skills/observability-design craft-ops/skills/incident-response -type f | sort` — expected: 2 SKILL.md + 6 references (3 each).

- [ ] **Step 2: Verify frontmatter of both skills parses with exact names**

Run the two `python3 -c` yaml checks from Tasks 2 and 4 — expected: `OK` for both.

- [ ] **Step 3: Verify seams and boundaries hold**

Run: `grep -il 'observability-authoring\|never author\|does not author' craft-ops/skills/observability-design/SKILL.md` (observability never-author boundary present) and `grep -il 'systematic-debugging' craft-ops/skills/incident-response/SKILL.md` (incident defers root-cause). Confirm both print their file.

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec's "Success criteria" and confirm each holds: principles present with runtime-levers + deployment-precondition explicit; observability-design covers all eight items incl. levers and health-signals-for-deployment and never authors config; incident-response drives the five phases and defers mechanics; README/version updated. Note any gap as a follow-up task rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## After the plan: behavioral eval loop (not a plan task)

Once the domain is built, run the `skill-creator` behavioral eval loop on **each** new skill (as done for the prior domains), using the discriminating-assertion discipline in `tools/craft-ops-evals/README.md` — an assertion earns its place only if a strong baseline can plausibly fail it. Candidate discriminators: for `observability-design`, whether the note designs **runtime levers** and the **deployment health signals** (a baseline often omits both); for `incident-response`, whether it **mitigates before diagnosing** and produces a **ratcheting** postmortem (a baseline tends to jump to root cause and write a narrative-only writeup). Save reusable sets under `tools/craft-ops-evals/`. This step is interactive (user reviews outputs) and runs after the plan completes.

---

## Notes for the executor

- These are skill/prose deliverables; "tests" are structural checks (frontmatter parse, section/keyword presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm regardless.
- Author every `SKILL.md` under **superpowers:writing-skills**.
- Match the suite's voice: strict rules each stated with their *why*; no *what*-comments; concise; cite craft / craft-ops roots.
- Do not build `observability-authoring` or any incident authoring — stubs only.
