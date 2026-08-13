# craft-ops deployment-authoring (authoring slice 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Ship the third authoring skill for `craft-ops`: `deployment-authoring`, which turns a `deployment-design` note into real rollout automation, bumping the plugin to `0.8.0` and folding into PR #3.

**Architecture:** Extends the existing `craft-ops/` plugin, replicating the proven `pipeline-authoring` / `infrastructure-authoring` shape with deployment-specific content. It defers the production loop to craft (`strict-tdd` for gate/promotion/flag logic, `verification` for the declarative rollout config) and the design decision upstream to `deployment-design`. No agent changes — `craft-ops-author` is generic.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin manifest. No application code. Validation is structural: YAML-frontmatter parse, required-keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Skill named exactly `deployment-authoring`.
- It WRITES the rollout automation (unlike `deployment-design`) but must (a) defer the design decision upstream to `deployment-design` and NOT re-decide it, and (b) defer the production loop to craft — named generically (test-first for logic, verification for the declarative config, review the diff) pointing to craft's `strict-tdd`/`verification`/`code-style`/`self-review` as canonical, so it degrades without craft.
- The split, explicit and correct: **gate/promotion/flag logic (health-gate evaluation, promotion/halt decisions, flag-targeting, generators, scripting) → craft `strict-tdd`; the declarative rollout config (rollout manifests / flag configuration) → craft `verification` (run the rollout against a test env and observe: canary progresses on a healthy signal, a bad metric halts it, rollback reverts).**
- Carry forward slice 1's lesson: **validate/lint the rollout manifest + entrypoint-smoke-invoke each extracted script through the exact entrypoint the rollout calls** is the always-runnable minimum verification; a tool dry-run is part of it where supported.
- SIGNATURE deployment rules (do not omit), lead with the first two: (1) **prefer extracted scripts over inline** — gate/promotion/flag logic in version-controlled scripts the rollout calls, never inline in the manifest; (2) **author AND prove the rollback path** — the reverse operation is written and *exercised* (rolled back in a test env, observed to revert) BEFORE the forward rollout is trusted (rollback-first). Then: **health gates are code, and tested** (extracted logic under strict-tdd, objective thresholds, not a dashboard glance); **deploy is decoupled from release** (ship dark, flip deliberately); no secrets in the config; honor the compatibility (expand-contract / N-1) the design decided; idempotent/re-runnable.
- Tool-agnostic — name Argo Rollouts / Flagger / Spinnaker / a feature-flag system only as examples, never as required.
- Every rule stated with its *why*; house style mirrors `craft-ops/skills/pipeline-authoring/` and `infrastructure-authoring/`.
- Follow the spec verbatim: `docs/superpowers/specs/2026-08-10-craft-ops-deployment-authoring-design.md`.
- Bump plugin to `0.8.0`; add a CHANGELOG entry; update README (flip the row; retarget the two stale "(future) `deployment-authoring`" refs in `deployment-design`'s SKILL.md, lines ~12 and ~50). Keep the marketplace craft-ops entry version in sync with plugin.json. Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/deployment-authoring/SKILL.md`
- `craft-ops/skills/deployment-authoring/references/rollout-authoring-hygiene.md`
- `craft-ops/skills/deployment-authoring/references/testing-and-verifying-rollouts.md`

Modified:
- `craft-ops/README.md` — flip the `deployment-authoring` row to Built.
- `craft-ops/skills/deployment-design/SKILL.md` — retarget the two stale "(future) `deployment-authoring`" refs to present tense.
- `craft-ops/CHANGELOG.md` — `0.8.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.7.0` → `0.8.0`.
- `.claude-plugin/marketplace.json` — craft-ops entry version `0.7.0` → `0.8.0`.

Independence: **Task 1 (skill) lands first** (Task 2's references are cited by it). After Task 1, **Task 2 (references)** is independent. **Task 3 (docs/version)** lands after the skill exists. Task 4 is controller verification.

---

### Task 1: The `deployment-authoring` skill

**Files:**
- Create: `craft-ops/skills/deployment-authoring/SKILL.md`

**Interfaces:**
- Consumes: the `deployment-design` note as input; reference filenames from Task 2 (`rollout-authoring-hygiene.md`, `testing-and-verifying-rollouts.md`).
- Produces: a skill named `deployment-authoring`.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/deployment-authoring/SKILL.md`. Read `craft-ops/skills/infrastructure-authoring/SKILL.md` first and mirror its section shape exactly (Why this exists → Seams → The production-discipline split → Domain rules → Guardrails → Exit condition). Use this frontmatter (name fixed; description states the write-vs-design boundary and the deferral):

```yaml
---
name: deployment-authoring
description: "Use when turning a deployment design note (from deployment-design) into the actual rollout automation — writing the real progressive-delivery config (a canary/blue-green controller such as Argo Rollouts or Flagger), feature-flag wiring, deploy scripts, and health-gate definitions. Applies opinionated authoring rules: prefer extracted scripts over inline rollout logic; author AND prove the rollback path (exercise the undo in a test env) before trusting the forward rollout; health gates are extracted, tested code, not a dashboard glance; deploy is decoupled from release (ship dark, flip deliberately); no secrets in the config; honor the compatibility the design decided; idempotent. It WRITES the rollout automation (unlike deployment-design, which only designs it), but defers the production loop to craft: gate/promotion/flag logic is built under strict-tdd, and the declarative rollout config is proven by verification — validate + entrypoint-smoke-invoke as the minimum, and a rollout run in a test environment. Not for deciding the rollout strategy (that is deployment-design), nor for pipeline, infrastructure, or observability authoring."
---
```

Body sections:
- `# Deployment Authoring — write the rollout the design already decided`
- `## Why this exists` — a design note is not a running rollout; this turns it into real, reviewed rollout automation without re-deciding the design or hand-waving the discipline. Unlike `-design` skills it writes code, so it leans on craft.
- `## Seams` — consumes the `deployment-design` note (strategy, gates, rollback plan, compatibility already decided — do not re-decide); defers the production loop to craft (`strict-tdd`, `verification`, `code-style`, `self-review`), named generically so it degrades without craft; review/verify go to `craft-reviewer`/`craft-verifier`.
- `## The production-discipline split` — gate/promotion/flag logic → craft `strict-tdd` (failing test first); the declarative rollout config → craft `verification` (run the rollout in a test env — canary progresses on a healthy signal, a bad metric halts it, rollback reverts). Add the minimum-verification rule: **validate/lint the rollout manifest + entrypoint-smoke-invoke each extracted script through the exact entrypoint the rollout calls is the always-runnable minimum; a tool dry-run is part of it where supported.**
- `## Domain rules` — lead with **prefer extracted scripts over inline** (see `references/rollout-authoring-hygiene.md`) and **author and prove the rollback path** (write the reverse operation and exercise it — roll back in a test env, observe it revert — before trusting the forward rollout; rollback-first). Then: **health gates are code, and tested** (extracted logic under strict-tdd; objective thresholds; not a dashboard glance); **deploy is decoupled from release** (ship dark, flip deliberately); no secrets in the config; honor the compatibility (expand-contract/N-1) the design decided; idempotent/re-runnable. Testing/verifying depth in `references/testing-and-verifying-rollouts.md`.
- `## Guardrails` — do not re-decide the design (defer to `deployment-design`); do not reimplement TDD/verification (defer to craft); never trust a forward rollout whose rollback you haven't authored and exercised; no secrets in the config; health gates are tested code, not a dashboard glance.
- `## Exit condition` — the rollout config, extracted gate/promotion/flag scripts, and a proven rollback path exist; the logic is covered by strict-tdd tests; the declarative config is verified by validate + entrypoint-smoke-invoke (minimum) and a rollout run in a test env; the rollback was exercised; committed the craft way — reviewed, no secrets.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `grep -m1 '^name:' craft-ops/skills/deployment-authoring/SKILL.md` — expected: `name: deployment-authoring`. Confirm a `description:` line exists.

- [ ] **Step 3: Verify the signature rules, the split, and the deferral are present**

Run: `grep -iE 'extracted script|inline' craft-ops/skills/deployment-authoring/SKILL.md` — expected: extraction rule present.
Run: `grep -iE 'rollback' craft-ops/skills/deployment-authoring/SKILL.md` — expected: the author-and-prove-the-rollback-path rule present.
Run: `grep -iE 'health gate' craft-ops/skills/deployment-authoring/SKILL.md` — expected: health-gates-as-tested-code present.
Run: `grep -iE 'strict-tdd' craft-ops/skills/deployment-authoring/SKILL.md && grep -iE 'verif' craft-ops/skills/deployment-authoring/SKILL.md && grep -iE 'entrypoint|smoke-invoke|validate' craft-ops/skills/deployment-authoring/SKILL.md` — expected: split + minimum-verification present.
Run: `grep -iE 'deployment-design' craft-ops/skills/deployment-authoring/SKILL.md` — expected: upstream design deferral stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/deployment-authoring/SKILL.md
git commit -m "feat(craft-ops): add deployment-authoring skill"
```

---

### Task 2: `deployment-authoring` references

**Files:**
- Create: `craft-ops/skills/deployment-authoring/references/rollout-authoring-hygiene.md`
- Create: `craft-ops/skills/deployment-authoring/references/testing-and-verifying-rollouts.md`

**Interfaces:**
- Produces: the two files cited by Task 1's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write rollout-authoring-hygiene.md**

Read `craft-ops/skills/infrastructure-authoring/references/iac-authoring-hygiene.md` and `craft-ops/skills/pipeline-authoring/references/pipeline-as-code-hygiene.md` first to match style (title+subtitle, intro, table of contents, `##` sections). Cover the domain rules, each with its *why*, LEADING with **prefer extracted scripts over inline** (gate/promotion/flag logic in scripts the rollout calls; inline can't be tested, bloats the manifest, hides the decision from review; extraction makes it testable) and **author and prove the rollback path** (the reverse operation is written and exercised in a test env before the forward rollout is trusted; a rollout whose undo has never been run is an outage waiting for the first bad release; rollback-first). Then: health gates are code and tested (objective thresholds, edge cases pinned by tests, not a dashboard glance); deploy decoupled from release (ship dark, flip deliberately, so shipping ≠ exposing); no secrets in the config (injected at deploy); honor the compatibility the design decided (expand-contract / N-1 across the transition); idempotent/re-runnable (a re-applied rollout definition converges, doesn't double-act).

- [ ] **Step 2: Write testing-and-verifying-rollouts.md**

Read `craft-ops/skills/infrastructure-authoring/references/testing-and-verifying-infrastructure.md` and `craft-ops/skills/pipeline-authoring/references/testing-and-verifying-pipelines.md` first (they carry the analogous split + entrypoint-smoke-invoke minimum — mirror that shape). Cover: what to unit-test under `strict-tdd` (health-gate evaluation, promotion/halt decisions, flag-targeting logic, generators — real logic with edge cases); how to verify the declarative rollout config under `verification` (run the rollout against a test env and observe: canary progresses on a healthy signal, a bad metric halts it, rollback reverts — evidence not inspection); the always-runnable minimum: **validate/lint the rollout manifest + smoke-invoke each extracted script through the exact entrypoint the rollout calls (`./gate.sh --dry-run`, `python -m rollout.promote --help`) catches a wrong module/CLI path or malformed manifest offline before any rollout — plus a tool dry-run where supported**; and the deployment-specific emphasis: **proving the rollback path by actually exercising it — a rollout whose undo has never been run is not verified, no matter how green the forward path looks.** Each rule with its *why*.

- [ ] **Step 3: Verify files exist, non-empty, and are cited**

Run: `for f in rollout-authoring-hygiene testing-and-verifying-rollouts; do p="craft-ops/skills/deployment-authoring/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/deployment-authoring/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for both.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/deployment-authoring/references/
git commit -m "feat(craft-ops): add deployment-authoring reference conventions"
```

---

### Task 3: README, deployment-design retarget, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/skills/deployment-design/SKILL.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name (Task 1).

- [ ] **Step 1: Update the README**

In `craft-ops/README.md` "Domains and skills" table, change the row `| Deployment & release | `deployment-authoring` (performs the rollout) | Planned |` to `| Deployment & release | `deployment-authoring` | Built |`.

- [ ] **Step 2: Retarget the stale deployment-design refs**

In `craft-ops/skills/deployment-design/SKILL.md`, retarget the two "(future) `deployment-authoring`" references (around line 12 in "Why this exists" and line 50 in the exit condition) to present tense — refer to `deployment-authoring` as the now-built sibling that authors the rollout, consistent with the table. Mirror how the `infrastructure-design` refs were retargeted (e.g. "handed off to the `deployment-authoring` skill"). Keep the design-vs-authoring boundary intact (deployment-design still only designs).

- [ ] **Step 3: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.8.0] — 2026-08-10` section above `## [0.7.0]`, under `### Added`: the `deployment-authoring` skill + 2 references (call out author-and-prove-the-rollback-path, health-gates-as-tested-code, extracted-scripts-over-inline, deploy-decoupled-from-release, and the validate/entrypoint-smoke-invoke minimum; deferring the production loop to craft and the design to deployment-design). Note the deployment-design "(future)" refs were retargeted. Match the format of existing entries.

- [ ] **Step 4: Bump both manifest versions**

Set `version` to `0.8.0` in `craft-ops/.claude-plugin/plugin.json`, and set the `craft-ops` plugin entry's `version` to `0.8.0` in `.claude-plugin/marketplace.json` (they track together). Keep both valid JSON.

- [ ] **Step 5: Verify docs and versions**

Run: `grep -q 'deployment-authoring' craft-ops/README.md && grep -q '0.8.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.8.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK` — expected: `DOCS_OK`.
Run: `grep -rn -i 'future' craft-ops/skills/deployment-design/SKILL.md | grep -i 'deployment-authoring' || echo "NO_STALE_FUTURE_REF"` — expected: `NO_STALE_FUTURE_REF`.
Confirm the marketplace craft-ops entry reads `0.8.0` and both JSON files are valid.

- [ ] **Step 6: Commit**

```bash
git add craft-ops/README.md craft-ops/skills/deployment-design/SKILL.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark deployment-authoring built; bump to 0.8.0"
```

---

### Task 4: Final slice verification (controller-run)

**Files:** none — verifies the slice against the spec's success criteria.

- [ ] **Step 1: Verify the tree**

Run: `find craft-ops/skills/deployment-authoring -type f | sort` — expected: 1 SKILL.md + 2 references.

- [ ] **Step 2: Verify frontmatter name**

Run: `grep -m1 '^name:' craft-ops/skills/deployment-authoring/SKILL.md` — expected: `name: deployment-authoring`.

- [ ] **Step 3: Verify signature rules and seams hold**

Confirm the SKILL.md and references state: extracted-scripts-over-inline; author-and-prove-the-rollback-path; health-gates-as-tested-code; deploy-decoupled-from-release; the strict-tdd/verification split with the validate + entrypoint-smoke-invoke minimum; the `deployment-design` upstream deferral; both references cited.

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec "Success criteria" and confirm each holds. Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## After the plan: behavioral validation (not a plan task)

Validate behaviorally like the prior authoring skills: dispatch `craft-ops-author` on a sample `deployment-design` note for a small service (a canary rollout with error-rate/latency gates and a rollback plan), and confirm the produced rollout automation honored the rules — gate/promotion logic extracted into scripts and covered by tests, a rollback path authored AND exercised (rolled back in a test env), deploy decoupled from release, no secrets in the config, and verification via validate + entrypoint-smoke-invoke. Interactive; runs after the plan completes.

## Notes for the executor

- Skill/prose deliverables; "tests" are structural checks (frontmatter parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author the `SKILL.md` under **superpowers:writing-skills**; mirror `craft-ops/skills/infrastructure-authoring/` and `pipeline-authoring/` throughout (the proven templates).
- Match the suite's voice: strict rules each with their *why*; no *what*-comments; concise; cite craft / craft-ops roots. Tool-agnostic — rollout tools named only as examples.
- Do not build `observability-authoring` — this slice is deployment only.
