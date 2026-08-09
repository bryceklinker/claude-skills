# craft-ops Deployment & release domain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Add the Deployment & release domain to `craft-ops`: expand `PRINCIPLES.md` with the full deployment-and-release principle set and ship the `deployment-design` skill (design/review only — never performs or authors the rollout), bumping the plugin to `0.3.0`.

**Architecture:** Extends the existing `craft-ops/` plugin, mirroring `cicd-pipeline-design` and `infrastructure-design` exactly: a thinking/decision skill producing a design note, with `references/` for the mechanics, principles anchored in `PRINCIPLES.md` and citing craft. No new plugin, no orchestrator. Built directly on `feat/craft-ops-cicd` (the consolidated PR #3 branch).

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin/marketplace manifests. No application code. Validation is structural: JSON parse, YAML-frontmatter parse, required-section/keyword presence, cross-reference resolution.

## Global Constraints

- Skill name is exactly `deployment-design` (mirrors `cicd-pipeline-design` / `infrastructure-design` — the name signals it *designs*, not performs).
- The skill **never performs or authors the rollout** (feature-flag config, canary specs, traffic rules, etc.). Performing/authoring is a future `deployment-authoring` skill, name-stubbed only.
- **Tool-agnostic prose:** name specific tools/techniques ONLY as examples of a category (e.g. "a progressive-delivery approach such as canary or blue-green"), never as a required choice; never hand over authored rollout config as the deliverable.
- Five signature opinions MUST be present and unmistakable: (a) **deploy is not release** (decouple shipping bits from exposing behavior, via flags/dark launch); (b) **progressive delivery** — widen on a healthy signal, never flip 100% at once; (c) **rollback-first** — a fast, rehearsed way back decided before the rollout; (d) **health-gated promotion with automatic halt/rollback on regression** (objective signals, not a human eyeballing a dashboard); (e) **backward/forward compatibility across the transition** (expand-contract, N-1).
- **Defer to `cicd-pipeline-design` at the promotion seam** — the skill takes over once an artifact has reached an environment; it does not re-decide CI/CD promotion or pipeline shape.
- Every strict rule is stated with its *why*.
- The skill inherits the scope-down house rule: on a targeted change decide the implicated areas in depth and one-line the rest; on a new rollout / whole release strategy decide all nine.
- `references/` are exactly `progressive-delivery.md`, `deploy-vs-release.md`, `rollback-and-compatibility.md`.
- Plugin version becomes `0.3.0` in `craft-ops/.claude-plugin/plugin.json`, the `craft-ops` entry of `.claude-plugin/marketplace.json`, and a new `CHANGELOG.md` entry.
- Observability & incident response remains a one-line stub in `PRINCIPLES.md` and Planned in the README.
- Follow the spec at `docs/superpowers/specs/2026-08-08-craft-ops-deployment-design.md` verbatim for principle text and the decision checklist.
- Commit after every task. New skill files live under `craft-ops/skills/deployment-design/`.

---

## File structure

Created:
- `craft-ops/skills/deployment-design/SKILL.md`
- `craft-ops/skills/deployment-design/references/progressive-delivery.md`
- `craft-ops/skills/deployment-design/references/deploy-vs-release.md`
- `craft-ops/skills/deployment-design/references/rollback-and-compatibility.md`

Modified:
- `craft-ops/PRINCIPLES.md` — add the Deployment & release principle set; update the "Coming domains" section.
- `craft-ops/README.md` — mark Deployment & release Built; add `deployment-authoring` Planned; refresh the intro lede (line ~5).
- `craft-ops/CHANGELOG.md` — add `0.3.0` entry + link.
- `craft-ops/.claude-plugin/plugin.json` — version `0.3.0`.
- `.claude-plugin/marketplace.json` — `craft-ops` entry version `0.3.0`.

Independence: all four content tasks are logically independent (Task 2 cites Task 1's principles and Task 3's reference filenames by name only, fixed in this plan). Because they share one working tree, **run implementers sequentially**. Order: Task 1 → Task 2 → Task 3 → Task 4, then Task 5.

---

### Task 1: PRINCIPLES.md — Deployment & release principle set

**Files:**
- Modify: `craft-ops/PRINCIPLES.md`

**Interfaces:**
- Produces: the numbered Deployment & release principle titles that `deployment-design/SKILL.md` (Task 2) cites.

- [ ] **Step 1: Read the current file**

Read `craft-ops/PRINCIPLES.md`. Current shape: CI/CD principles `## 1.`–`## 8.`; then a `## Infrastructure as Code` section with `### 1.`–`### 10.`; then `## Coming domains` (intro paragraph + two `*(stub)*` bullets: Deployment & release, Observability); then `*Lineage:*`.

- [ ] **Step 2: Insert the Deployment & release principle section**

Immediately **before** `## Coming domains`, insert a new domain section headed `## Deployment & release` followed by these nine principles as `### N. <title>` sub-sections (matching the Infrastructure as Code section's format) — each a short paragraph stating the rule with its *why*, and the `*(…)*` citation where given. Copy the intent verbatim from the spec:

1. **Deploy is not release** — shipping the bits (deploy) is decoupled from exposing the behavior (release); a version can run in production without being live to users, via feature flags / dark launch. *(expands craft-ops CI/CD principle 5; craft: the domain is independent of how data enters or leaves.)*
2. **Progressive delivery — widen on a healthy signal** — never flip 100% at once; expose to a small blast radius first (a canary, a ring, a traffic percentage) and widen only as real health signals stay good. *(craft: judgment is independent and rests on evidence.)*
3. **Rollback-first — never ship what you can't cheaply undo** — every release has a fast, rehearsed way back (roll back or roll forward), decided before the rollout starts, not improvised during an incident. *(craft-ops IaC reversibility / protect-and-migrate.)*
4. **Health-gated promotion; automatic halt on regression** — the rollout advances and aborts on objective signals (error rate, latency, saturation, a key business metric), not a human eyeballing a dashboard; a regression auto-halts and/or auto-rolls-back. *(craft: "done" rests on evidence from the real target.)*
5. **Backward/forward compatibility across the transition** — during a rollout old and new versions run at once, so each must tolerate the other (expand-contract; N-1 compatible schemas, APIs, messages). *(craft-ops CI/CD promote-the-same-artifact + IaC migrate-don't-teardown.)*
6. **Control the blast radius** — rings (internal → canary → wider); a bad release harms the fewest users and is caught while small.
7. **Release is a decision; deploy is routine** — deploying artifacts is continuous and automated; turning a release on and widening it is a deliberate, reversible, owned decision.
8. **You can only progressively deliver what you can observe** — the signals that gate a rollout must exist before the rollout does. *(previews the observability & incident-response domain.)*
9. **State the why; keep the escape hatch** — inherited verbatim from craft. *(craft: state the why; keep the escape hatch.)*

(Note: match the citation *style* of the existing sections — a trailing `*(…)*` parenthetical, as Infrastructure as Code principle 10 uses; do NOT open principle 9 with leading "Inherited verbatim" prose.)

- [ ] **Step 3: Update the "Coming domains" section**

Remove the `**Deployment & release** … *(stub)*` bullet (now a full section). Update the intro sentence so it names CI/CD, Infrastructure as Code, **and** Deployment & release as covered in full, with the rest (Observability) scaffolded as stubs. Leave the Observability stub bullet unchanged.

- [ ] **Step 4: Verify**

Run: `grep -c '^### ' craft-ops/PRINCIPLES.md`
Expected: `19` or more (10 IaC + 9 Deployment sub-principles).

Run: `grep -icE 'deploy is not release|progressive delivery|rollback-first|health-gated|expand-contract|blast radius' craft-ops/PRINCIPLES.md`
Expected: `5` or more (the signature opinions present).

Run: `grep -i 'observability' craft-ops/PRINCIPLES.md`
Expected: still present as a stub.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/PRINCIPLES.md
git commit -m "feat(craft-ops): add Deployment & release principles"
```

---

### Task 2: The `deployment-design` skill

**Files:**
- Create: `craft-ops/skills/deployment-design/SKILL.md`

**Interfaces:**
- Consumes: Deployment & release principle titles from `craft-ops/PRINCIPLES.md` (Task 1); reference filenames from Task 3 (`references/progressive-delivery.md`, `references/deploy-vs-release.md`, `references/rollback-and-compatibility.md`).
- Produces: a skill named `deployment-design` that emits a deployment/release design note.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/deployment-design/SKILL.md`. Read `craft-ops/skills/cicd-pipeline-design/SKILL.md` and `craft-ops/skills/infrastructure-design/SKILL.md` first for shape/voice. Use this frontmatter (name fixed; description mirrors the sibling design skills — when to use + the design-not-perform boundary + exclusions + the CI/CD seam):

```yaml
---
name: deployment-design
description: "Use when deciding HOW a new version is released to real traffic, or reviewing an existing release/rollout setup — the rollout strategy (canary, blue-green, rolling, rings), decoupling deploy from release (feature flags / dark launch), health-gated promotion and automatic rollback, blast-radius control, and backward/forward compatibility across the transition. Produces a short deployment design note — strategy, deploy-vs-release decoupling, rollout steps, health gates, rollback plan, compatibility, state during rollout, ownership, and evidence-of-done — each decision with its why. It DESIGNS the release; it never performs or authors the rollout (that is a separate authoring skill). It takes over once an artifact has reached an environment and defers to cicd-pipeline-design for pipeline shape and promotion. Not for CI/CD pipeline design, infrastructure provisioning, or observability — those are other craft-ops domains."
---
```

Then a body mirroring the sibling design skills' sections:
- `# Deployment Design — decide how the release reaches users before you roll it out`
- `## Why this exists` — a release flipped 100% at once with no way back turns a bad version into an outage; deciding strategy, gates, and rollback once — against the conventions — makes the rollout mechanical. A thinking phase; output is a design note, not rollout code. Note the seam: it takes over once `cicd-pipeline-design` has promoted an artifact into an environment.
- `## What it decides` — the nine decision areas, each one bullet tied to its principle:
  - **Release strategy** — canary / blue-green / rolling / ring-based, and why it fits. (see `references/progressive-delivery.md`)
  - **Deploy-vs-release decoupling** — what ships dark vs. exposed; the flag/toggle plan; who flips it. (see `references/deploy-vs-release.md`)
  - **Rollout steps & blast radius** — the concrete progression (internal → 1% → 10% → 50% → 100%), population per step, pace.
  - **Health gates & abort criteria** — objective signals that promote each step; thresholds that auto-halt / roll back.
  - **Rollback / roll-forward plan** — the reversible path decided up front; how fast, what it costs, when roll-forward is chosen. (see `references/rollback-and-compatibility.md`)
  - **Compatibility across the transition** — old and new coexist (expand-contract; N-1); what had to ship earlier to make this safe.
  - **State & data during rollout** — sessions, in-flight work, sticky routing, migrations; ties to the IaC durable tier.
  - **Ownership & the release decision** — who starts/advances/aborts; the gate (automated vs. human) before widening to prod-at-large.
  - **Evidence of done** — fully live AND signals held through 100% AND the rollback path was proven available — not "the deploy job finished."
- `## Write it down` — save a short design note (e.g. `docs/craft-ops/deployments/YYYY-MM-DD-<name>.md`); mention reading `.craft-ops.yml` if present.
- `## Guardrails` — YAGNI (not every rollout needs canary+flags+rings); **never perform or author the rollout here**; prefer the existing shape; match the note's length to the change; **defer to `cicd-pipeline-design` at the promotion seam**.
- `## Exit condition` — a written design note accounting for the nine areas (implicated in depth, others one-lined); hand off to the future `deployment-authoring` skill.

- [ ] **Step 2: Verify frontmatter and name**

Run: `python3 -c "import yaml; t=open('craft-ops/skills/deployment-design/SKILL.md').read().split('---')[1]; d=yaml.safe_load(t); assert d['name']=='deployment-design', d['name']; print('OK', d['name'])"`
Expected: `OK deployment-design`
(Use the default `python3` on PATH — it has PyYAML; `/opt/homebrew/bin/python3.14` does not.)

- [ ] **Step 3: Verify the boundary, seam, and signature opinions**

Run: `grep -in 'never perform' craft-ops/skills/deployment-design/SKILL.md`
Expected: a "never performs or authors the rollout" guardrail line.

Run: `grep -c 'cicd-pipeline-design' craft-ops/skills/deployment-design/SKILL.md`
Expected: `1` or more (the CI/CD seam is referenced).

Run: `grep -icE 'canary|blue-green|rollback|health gate|deploy is not release|flag' craft-ops/skills/deployment-design/SKILL.md`
Expected: `3` or more (signature opinions in the body).

Run: `for f in progressive-delivery deploy-vs-release rollback-and-compatibility; do grep -q "references/$f.md" craft-ops/skills/deployment-design/SKILL.md && echo "cited $f" || echo "NOT CITED $f"; done`
Expected: all three cited.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/deployment-design/SKILL.md
git commit -m "feat(craft-ops): add deployment-design skill"
```

---

### Task 3: The three `references/` convention docs

**Files:**
- Create: `craft-ops/skills/deployment-design/references/progressive-delivery.md`
- Create: `craft-ops/skills/deployment-design/references/deploy-vs-release.md`
- Create: `craft-ops/skills/deployment-design/references/rollback-and-compatibility.md`

**Interfaces:**
- Consumes: nothing (standalone reference prose).
- Produces: the three files cited by `SKILL.md` (Task 2) — filenames must match exactly.

- [ ] **Step 1: Write progressive-delivery.md**

Read `craft-ops/skills/cicd-pipeline-design/references/stage-ordering.md` and `craft-ops/skills/infrastructure-design/references/review-before-apply.md` for voice. Create `references/progressive-delivery.md`: the rollout strategies and health-gating. Cover: canary / blue-green / rolling / ring-based (what each is, when it fits — traffic shape, statefulness, cost of a second environment); widening the blast radius on a healthy signal (internal → canary → wider); health-gated promotion with automatic halt/rollback on objective signals (error rate, latency, saturation, a key metric), not a human watching a dashboard; and that you can only gate on signals that already exist. State each rule with its *why*.

- [ ] **Step 2: Write deploy-vs-release.md**

Create `references/deploy-vs-release.md`: decoupling deploy from release. Cover: the distinction (a version can be deployed/running without being released/exposed); feature flags / dark launch / traffic routing as the decoupling mechanism; release as an owned, reversible decision distinct from the routine, automated deploy; who flips the switch and how the flip is itself reversible; and the operational hygiene of flags (cleanup, not leaving permanent forks). State each rule with its *why*.

- [ ] **Step 3: Write rollback-and-compatibility.md**

Create `references/rollback-and-compatibility.md`: rollback-first + compatibility across the transition. Cover: every release has a fast, rehearsed way back decided before the rollout, and rehearsing it (an untested rollback is not a rollback); roll-forward vs. roll-back and when each is right; the requirement that old and new versions coexist during a rollout, so each must tolerate the other; expand-contract / N-1 compatibility for schemas, APIs, and messages (and what must ship in a prior release to make the current one safely reversible); and the tie to the IaC durable-tier rule (data/durable resources are migrated, never torn down, so a rollback of code doesn't require a rollback of data). State each rule with its *why*.

- [ ] **Step 4: Verify all three exist and are cited**

Run: `for f in progressive-delivery deploy-vs-release rollback-and-compatibility; do p="craft-ops/skills/deployment-design/references/$f.md"; test -s "$p" && echo "OK $f" || echo "MISSING $f"; done`
Expected: `OK` for all three.

Run: `grep -il -E 'expand.contract|N-1|backward' craft-ops/skills/deployment-design/references/rollback-and-compatibility.md`
Expected: matches (the compatibility rule is present).

- [ ] **Step 5: Commit**

```bash
git add craft-ops/skills/deployment-design/references/
git commit -m "feat(craft-ops): add deployment-design reference conventions"
```

---

### Task 4: README, CHANGELOG, and version bump to 0.3.0

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name `deployment-design` (Task 2).
- Produces: user-facing docs + the `0.3.0` version.

- [ ] **Step 1: Update the README domain table and intro lede**

In `craft-ops/README.md`:
- Change the row `| Deployment & release | — | Planned |` to `| Deployment & release | \`deployment-design\` | Built |`, and add immediately below it a new row: `| Deployment & release | \`deployment-authoring\` (performs the rollout) | Planned |`. Leave the Observability row as Planned.
- Refresh the intro lede (around line 5): it currently reads roughly "(CI/CD and Infrastructure as Code today; deployment and observability as the suite grows)". Update it so CI/CD, Infrastructure as Code, **and** Deployment & release are named as covered today, and only observability remains as the growing/future set. Match the existing tone.

- [ ] **Step 2: Bump plugin.json and marketplace.json to 0.3.0**

In `craft-ops/.claude-plugin/plugin.json`, change `"version": "0.2.0"` to `"version": "0.3.0"`. In `.claude-plugin/marketplace.json`, change the `craft-ops` plugin entry's `"version": "0.2.0"` to `"version": "0.3.0"` (do not touch the `craft` entry).

- [ ] **Step 3: Add the CHANGELOG 0.3.0 entry**

In `craft-ops/CHANGELOG.md`, add a new `## [0.3.0] — 2026-08-08` section above the `0.2.0` entry, under `### Added`: the Deployment & release principle set in `PRINCIPLES.md`; the `deployment-design` skill and its three references; the README domain-table update. Add a matching link reference near the other link lines (`[0.3.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.3.0`).

- [ ] **Step 4: Verify**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -c "import json; print([(p['name'],p['version']) for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']])"`
Expected: valid JSON; prints `[('craft', ...), ('craft-ops', '0.3.0')]`.

Run: `grep -q 'deployment-design' craft-ops/README.md && grep -qi 'deployment-authoring' craft-ops/README.md && grep -q '0.3.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.3.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK`
Expected: `DOCS_OK`

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark Deployment & release built; bump to 0.3.0"
```

---

### Task 5: Final suite verification

**Files:** none created — verifies the whole build against the spec's success criteria.

- [ ] **Step 1: Verify the new skill tree**

Run: `find craft-ops/skills/deployment-design -type f | sort`
Expected exactly:
```
craft-ops/skills/deployment-design/SKILL.md
craft-ops/skills/deployment-design/references/deploy-vs-release.md
craft-ops/skills/deployment-design/references/progressive-delivery.md
craft-ops/skills/deployment-design/references/rollback-and-compatibility.md
```

- [ ] **Step 2: Verify the signature opinions + seam across the domain**

Run: `grep -rilE 'deploy is not release|progressive delivery|rollback' craft-ops/PRINCIPLES.md craft-ops/skills/deployment-design/`
Expected: PRINCIPLES.md, SKILL.md, and the references all match — the opinions are consistent across principles, skill, and references.

Run: `grep -rl 'cicd-pipeline-design' craft-ops/skills/deployment-design/SKILL.md`
Expected: the CI/CD seam is referenced from the skill.

- [ ] **Step 3: Verify manifests and version**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([(p['name'],p['version']) for p in d['plugins']])"`
Expected: valid; `craft-ops` at `0.3.0`, both plugins listed.

- [ ] **Step 4: Confirm against the spec success criteria**

Re-read `docs/superpowers/specs/2026-08-08-craft-ops-deployment-design.md` "Success criteria" and confirm each holds: full principle set with the signature opinions; skill triggers/decides the nine areas and never performs/authors the rollout; defers to cicd-pipeline-design at the seam; scope-down behavior available; README marks Built and version is 0.3.0. Note any gap and open a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## Notes for the executor

- Skill/prose deliverables: "tests" are structural checks (JSON/YAML parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author `SKILL.md` under **superpowers:writing-skills**.
- Match `craft-ops`'s established voice: strict rules each with their *why*; no *what*-comments; concise; tools/techniques named only as examples, never mandated.
- Do not build `deployment-authoring` or the other deferred domains — named stubs only.
- Use the default `python3` on PATH for the frontmatter YAML check (it has PyYAML); plain JSON checks work on either interpreter.
