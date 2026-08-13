# craft-ops observability-authoring (authoring slice 4, final) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Ship the fourth and final authoring skill for `craft-ops`: `observability-authoring`, which turns an `observability-design` note into real observability-as-code, bumping the plugin to `0.9.0` and folding into PR #3 — completing the suite (every domain now has design + authoring).

**Architecture:** Extends the existing `craft-ops/` plugin, replicating the proven `deployment-authoring` shape with observability-specific content. It defers the production loop to craft (`strict-tdd` for metric/SLO/lever logic, `verification` for the declarative dashboards/alerts) and the design decision upstream to `observability-design`. No agent changes — `craft-ops-author` is generic.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin manifest. No application code. Validation is structural: YAML-frontmatter parse, required-keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Skill named exactly `observability-authoring`.
- It WRITES the observability-as-code (unlike `observability-design`) but must (a) defer the design decision upstream to `observability-design` and NOT re-decide it, and (b) defer the production loop to craft — named generically (test-first for logic, verification for the declarative artifacts, review the diff) pointing to craft's `strict-tdd`/`verification`/`code-style`/`self-review` as canonical, so it degrades without craft.
- The split, explicit and correct: **metric/SLO/burn-rate computation, instrumentation helpers, alert-expression generators, runtime-lever toggle logic → craft `strict-tdd`; the declarative dashboards-as-code and alert-rule config → craft `verification` (fire the alert against a synthetic/replayed signal — it trips on a bad signal, stays quiet on a healthy one; the dashboard queries resolve).**
- Carry forward the minimum-verification lesson: **validate/lint the alert rules + dashboard definitions + entrypoint-smoke-invoke each extracted script through the exact entrypoint it's called by** is the always-runnable minimum.
- SIGNATURE observability rules (do not omit), lead with the first two: (1) **prefer generated/extracted over hand-maintained duplication** — dashboards and alerts as code (templated/generated, version-controlled, reviewed), instrumentation via a shared tested helper, never click-ops or copy-paste; (2) **prove the alert fires** — an alert rule is verified by firing it against a synthetic/replayed signal that should trip it (and staying quiet on a healthy one) BEFORE it is trusted; an alert never observed to fire is not verified (the observability analog of deployment's prove-the-rollback). Then: **wire the runtime levers for real** (verbosity/sampling/trace-detail wired to runtime config/flags with default-vs-incident settings, cost guardrails, auto-revert — flip without a redeploy, as the design intended); **alert on symptoms not causes**; **cardinality guardrails** (bounded label sets, no unbounded dimension); no secrets in dashboard/datasource/alert config.
- Tool-agnostic — name OpenTelemetry / Grafana / Prometheus / Alertmanager only as examples, never as required.
- Every rule stated with its *why*; house style mirrors `craft-ops/skills/deployment-authoring/` and the other authoring skills.
- Follow the spec verbatim: `docs/superpowers/specs/2026-08-10-craft-ops-observability-authoring-design.md`.
- Bump plugin to `0.9.0`; add a CHANGELOG entry; update README (flip the row; retarget the THREE stale "(future) `observability-authoring`" refs in `observability-design`'s SKILL.md, lines ~12, ~46, ~52). Keep the marketplace craft-ops entry version in sync with plugin.json. Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/observability-authoring/SKILL.md`
- `craft-ops/skills/observability-authoring/references/observability-as-code-hygiene.md`
- `craft-ops/skills/observability-authoring/references/testing-and-verifying-observability.md`

Modified:
- `craft-ops/README.md` — flip the `observability-authoring` row to Built.
- `craft-ops/skills/observability-design/SKILL.md` — retarget the three stale "(future) `observability-authoring`" refs to present tense.
- `craft-ops/CHANGELOG.md` — `0.9.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.8.0` → `0.9.0`.
- `.claude-plugin/marketplace.json` — craft-ops entry version `0.8.0` → `0.9.0`.

Independence: **Task 1 (skill) lands first** (Task 2's references are cited by it). After Task 1, **Task 2 (references)** is independent. **Task 3 (docs/version)** lands after the skill exists. Task 4 is controller verification.

---

### Task 1: The `observability-authoring` skill

**Files:**
- Create: `craft-ops/skills/observability-authoring/SKILL.md`

**Interfaces:**
- Consumes: the `observability-design` note as input; reference filenames from Task 2 (`observability-as-code-hygiene.md`, `testing-and-verifying-observability.md`).
- Produces: a skill named `observability-authoring`.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/observability-authoring/SKILL.md`. Read `craft-ops/skills/deployment-authoring/SKILL.md` first (the most recent sibling) and mirror its section shape exactly (Why this exists → Seams → The production-discipline split → Domain rules → Guardrails → Exit condition). Use this frontmatter (name fixed; description states the write-vs-design boundary and the deferral):

```yaml
---
name: observability-authoring
description: "Use when turning an observability design note (from observability-design) into the actual observability-as-code — writing the real instrumentation, dashboards-as-code, alert rules, and runtime-lever wiring. Applies opinionated authoring rules: prefer generated/extracted dashboards-and-alerts-as-code over click-ops; PROVE each alert fires by firing it against a synthetic/replayed signal before trusting it; wire the runtime levers (verbosity/sampling/trace detail) to flip without a redeploy; alert on symptoms not causes; cardinality guardrails (no unbounded labels); no secrets in config. It WRITES the observability-as-code (unlike observability-design, which only designs it), but defers the production loop to craft: metric/SLO/lever logic is built under strict-tdd, and the declarative dashboards/alerts are proven by verification — validate + entrypoint-smoke-invoke as the minimum, and firing the alert on a synthetic signal. Not for deciding what to observe (that is observability-design), nor for pipeline, infrastructure, or deployment authoring."
---
```

Body sections:
- `# Observability Authoring — write the observability the design already decided`
- `## Why this exists` — a design note is not running instrumentation; this turns it into real, reviewed observability-as-code without re-deciding the design or hand-waving the discipline. Unlike `-design` skills it writes code, so it leans on craft.
- `## Seams` — consumes the `observability-design` note (SLOs, signals, alerting strategy, levers already decided — do not re-decide); defers the production loop to craft (`strict-tdd`, `verification`, `code-style`, `self-review`), named generically so it degrades without craft; review/verify go to `craft-reviewer`/`craft-verifier`.
- `## The production-discipline split` — metric/SLO/burn-rate/lever logic → craft `strict-tdd` (failing test first); the declarative dashboards/alerts → craft `verification` (fire the alert against a synthetic/replayed signal — trips on bad, quiet on healthy; dashboard queries resolve). Add the minimum-verification rule: **validate/lint the alert rules + dashboard definitions + entrypoint-smoke-invoke each extracted script is the always-runnable minimum.**
- `## Domain rules` — lead with **prefer generated/extracted over hand-maintained duplication** (dashboards/alerts as code, instrumentation via a shared tested helper; see `references/observability-as-code-hygiene.md`) and **prove the alert fires** (fire it against a synthetic/replayed signal that should trip it, confirm it stays quiet on a healthy one, before trusting it; an alert never observed to fire is not verified). Then: **wire the runtime levers for real** (verbosity/sampling/trace-detail wired to runtime config/flags, default-vs-incident settings, cost guardrails, auto-revert — flip without a redeploy); **alert on symptoms not causes**; **cardinality guardrails** (bounded labels, no unbounded dimension); no secrets in dashboard/datasource/alert config. Testing/verifying depth in `references/testing-and-verifying-observability.md`.
- `## Guardrails` — do not re-decide the design (defer to `observability-design`); do not reimplement TDD/verification (defer to craft); never trust an alert you haven't fired against a signal that should trip it; no secrets in config; no unbounded-cardinality labels.
- `## Exit condition` — the instrumentation (via a tested helper), dashboards-as-code, alert rules proven to fire, and runtime-lever wiring exist; metric/SLO/lever logic is covered by strict-tdd tests; the declarative artifacts are verified by validate + entrypoint-smoke-invoke (minimum) and by firing each alert against a synthetic signal; committed the craft way — reviewed, no secrets, bounded cardinality.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `grep -m1 '^name:' craft-ops/skills/observability-authoring/SKILL.md` — expected: `name: observability-authoring`. Confirm a `description:` line exists.

- [ ] **Step 3: Verify the signature rules, the split, and the deferral are present**

Run: `grep -iE 'as code|as-code|generated|duplicat' craft-ops/skills/observability-authoring/SKILL.md` — expected: the generated/extracted-over-duplication rule present.
Run: `grep -iE 'alert.*fire|fire.*alert' craft-ops/skills/observability-authoring/SKILL.md` — expected: the prove-the-alert-fires rule present.
Run: `grep -iE 'lever' craft-ops/skills/observability-authoring/SKILL.md` — expected: wire-the-runtime-levers present.
Run: `grep -iE 'strict-tdd' craft-ops/skills/observability-authoring/SKILL.md && grep -iE 'verif' craft-ops/skills/observability-authoring/SKILL.md && grep -iE 'entrypoint|smoke-invoke|validate' craft-ops/skills/observability-authoring/SKILL.md` — expected: split + minimum-verification present.
Run: `grep -iE 'observability-design' craft-ops/skills/observability-authoring/SKILL.md` — expected: upstream design deferral stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/observability-authoring/SKILL.md
git commit -m "feat(craft-ops): add observability-authoring skill"
```

---

### Task 2: `observability-authoring` references

**Files:**
- Create: `craft-ops/skills/observability-authoring/references/observability-as-code-hygiene.md`
- Create: `craft-ops/skills/observability-authoring/references/testing-and-verifying-observability.md`

**Interfaces:**
- Produces: the two files cited by Task 1's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write observability-as-code-hygiene.md**

Read `craft-ops/skills/deployment-authoring/references/rollout-authoring-hygiene.md` first to match style (title+subtitle, intro, table of contents, `##` sections). Cover the domain rules, each with its *why*, LEADING with **prefer generated/extracted over hand-maintained duplication** (dashboards and alerts as version-controlled, templated/generated code reviewed like any change; instrumentation through a shared tested helper; click-ops and copy-paste are how dashboards drift from reality and alerts rot silently) and **wire the runtime levers for real** (the design decided verbosity/sampling/trace-detail levers; authoring wires them to actual runtime config/flags with default-vs-incident settings, cost/cardinality guardrails, and auto-revert, so detail ramps up/down without a redeploy). Then: alert on symptoms not causes (page on user pain / SLO burn, not every internal cause — cause-paging is the noise that trains people to ignore the page); cardinality guardrails (bounded label sets, never an unbounded dimension like raw user ID or request path — unbounded cardinality is how a metrics bill explodes and a store falls over); no secrets in dashboard/datasource/alert config (injected, never committed).

- [ ] **Step 2: Write testing-and-verifying-observability.md**

Read `craft-ops/skills/deployment-authoring/references/testing-and-verifying-rollouts.md` first (it carries the analogous split + entrypoint-smoke-invoke minimum + a "prove the X by exercising it" signature section — mirror that shape). Cover: what to unit-test under `strict-tdd` (metric/SLO/burn-rate computation, instrumentation helpers, alert-expression generators, runtime-lever toggle logic — real logic with edge cases); how to verify the declarative dashboards/alerts under `verification` (fire the alert against a synthetic/replayed signal and observe it trip; confirm it stays quiet on a healthy signal; the dashboard queries resolve — evidence not inspection); the always-runnable minimum: **validate/lint the alert rules + dashboard definitions + smoke-invoke each extracted script through the exact entrypoint it's called by, catching a malformed rule / broken query / wrong entrypoint offline before any live signal**; and the observability-specific emphasis: **proving an alert fires by ACTUALLY FIRING it against a signal that should trip it — an alert never observed to fire is not verified, no matter how correct the expression looks; the failure mode is discovering during the incident that the page never came.** Each rule with its *why*.

- [ ] **Step 3: Verify files exist, non-empty, and are cited**

Run: `for f in observability-as-code-hygiene testing-and-verifying-observability; do p="craft-ops/skills/observability-authoring/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/observability-authoring/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for both.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/observability-authoring/references/
git commit -m "feat(craft-ops): add observability-authoring reference conventions"
```

---

### Task 3: README, observability-design retarget, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/skills/observability-design/SKILL.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name (Task 1).

- [ ] **Step 1: Update the README**

In `craft-ops/README.md` "Domains and skills" table, change the row `| Observability & incident response | `observability-authoring` (writes the instrumentation/dashboards/alerts) | Planned |` to `| Observability & incident response | `observability-authoring` | Built |`.

- [ ] **Step 2: Retarget the stale observability-design refs**

In `craft-ops/skills/observability-design/SKILL.md`, retarget the THREE "(future) `observability-authoring`" references (around lines 12 "Why this exists", 46 in Guardrails, 52 in the exit condition) to present tense — refer to `observability-authoring` as the now-built sibling that authors the observability-as-code, consistent with the table. Mirror how the `deployment-design` refs were retargeted (grep that file for the phrasing). Keep the design-vs-authoring boundary intact (observability-design still only designs).

- [ ] **Step 3: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.9.0] — 2026-08-10` section above `## [0.8.0]`, under `### Added`: the `observability-authoring` skill + 2 references named by path (call out prove-the-alert-fires, wire-the-runtime-levers-for-real, dashboards/alerts-as-code-over-click-ops, cardinality guardrails, and the validate/entrypoint-smoke-invoke minimum; deferring the production loop to craft and the design to observability-design). Note the observability-design "(future)" refs were retargeted, and that this completes the suite (every domain has design + authoring). Match the format of existing entries (name the reference files).

- [ ] **Step 4: Bump both manifest versions**

Set `version` to `0.9.0` in `craft-ops/.claude-plugin/plugin.json`, and set the `craft-ops` plugin entry's `version` to `0.9.0` in `.claude-plugin/marketplace.json` (they track together). Keep both valid JSON.

- [ ] **Step 5: Verify docs and versions**

Run: `grep -q 'observability-authoring' craft-ops/README.md && grep -q '0.9.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.9.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK` — expected: `DOCS_OK`.
Run: `grep -rn -i 'future' craft-ops/skills/observability-design/SKILL.md | grep -i 'observability-authoring' || echo "NO_STALE_FUTURE_REF"` — expected: `NO_STALE_FUTURE_REF`.
Confirm the marketplace craft-ops entry reads `0.9.0` and both JSON files are valid.

- [ ] **Step 6: Commit**

```bash
git add craft-ops/README.md craft-ops/skills/observability-design/SKILL.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark observability-authoring built; bump to 0.9.0"
```

---

### Task 4: Final slice verification (controller-run)

**Files:** none — verifies the slice against the spec's success criteria.

- [ ] **Step 1: Verify the tree**

Run: `find craft-ops/skills/observability-authoring -type f | sort` — expected: 1 SKILL.md + 2 references.

- [ ] **Step 2: Verify frontmatter name**

Run: `grep -m1 '^name:' craft-ops/skills/observability-authoring/SKILL.md` — expected: `name: observability-authoring`.

- [ ] **Step 3: Verify signature rules and seams hold**

Confirm the SKILL.md and references state: generated/extracted-over-duplication; prove-the-alert-fires; wire-the-runtime-levers-for-real; symptom-based alerting; cardinality guardrails; the strict-tdd/verification split with the validate + entrypoint-smoke-invoke minimum; the `observability-design` upstream deferral; both references cited.

- [ ] **Step 4: Confirm against the spec's success criteria (and the suite is complete)**

Re-read the spec "Success criteria" and confirm each holds. Confirm every craft-ops domain now has both a design and an authoring skill (cicd-pipeline-design + pipeline-authoring; infrastructure-design + infrastructure-authoring; deployment-design + deployment-authoring; observability-design + observability-authoring; plus incident-response). Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## After the plan: behavioral validation (not a plan task)

Validate behaviorally like the prior authoring skills: dispatch `craft-ops-author` on a sample `observability-design` note for a small service (SLOs, a symptom-based alert, runtime levers), and confirm the produced observability-as-code honored the rules — dashboards/alerts as code, an alert proven to fire by firing it against a synthetic signal, runtime levers wired to flip without a redeploy, cardinality guardrails, no secrets, and verification via validate + entrypoint-smoke-invoke. Interactive; runs after the plan completes.

## Notes for the executor

- Skill/prose deliverables; "tests" are structural checks (frontmatter parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author the `SKILL.md` under **superpowers:writing-skills**; mirror `craft-ops/skills/deployment-authoring/` and the other authoring skills throughout (the proven templates).
- Match the suite's voice: strict rules each with their *why*; no *what*-comments; concise; cite craft / craft-ops roots. Tool-agnostic — observability tools named only as examples.
- This is the LAST authoring slice — do not build a `.craft-ops.yml` conventions skill or anything else; observability only.
