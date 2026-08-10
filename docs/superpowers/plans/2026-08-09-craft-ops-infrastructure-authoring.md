# craft-ops infrastructure-authoring (authoring slice 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Ship the second authoring skill for `craft-ops`: `infrastructure-authoring`, which turns an `infrastructure-design` note into real IaC, bumping the plugin to `0.6.0` and folding into PR #3.

**Architecture:** Extends the existing `craft-ops/` plugin, replicating the proven `pipeline-authoring` shape with IaC-specific content. It defers the production loop to craft (`strict-tdd` for policy/module logic, `verification` for declarative resources) and defers the design decision upstream to `infrastructure-design`. No agent changes — `craft-ops-author` is already generic. No new domains beyond IaC in this slice.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin manifest. No application code. Validation is structural: YAML-frontmatter parse, required-keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Skill named exactly `infrastructure-authoring`.
- It WRITES the IaC (unlike `infrastructure-design`) but must (a) defer the design decision upstream to `infrastructure-design` and NOT re-decide it, and (b) defer the production loop to craft — named generically (test-first for logic, verification for declarative resources, review the diff/plan) pointing to craft's `strict-tdd`/`verification`/`code-style`/`self-review` as canonical, so it degrades without craft.
- The split, explicit and correct: **policy/module logic (policy-as-code, modules with computed values, generators, scripting) → craft `strict-tdd`; the declarative resources → craft `verification` (validate + plan/diff reviewed, then apply against a throwaway/sandbox env).**
- Carry forward Spec 1's lesson: **`validate` + `plan` is the always-runnable minimum verification** — it catches broken references/types/interpolations and unexpected destroy/replace offline before any apply (the IaC analog of entrypoint smoke-invoke). The plan is a diff you must READ.
- FIRST-CLASS signature rules (do not omit): **prefer small composable modules over duplicated resource blocks** (the extraction rule); and **never co-locate a durable resource inside a compute unit** — durable resources (db, object store, queue, topic, bus) live in their OWN composable unit; compute units (instance, container, function, cluster, ASG/MIG) receive references (IDs/ARNs/endpoints) to durable resources as inputs and never create them, because compute is disposable and would take a co-located durable resource down with it. Plus: protect durable resources (lifecycle guards, migrate-not-teardown); review the plan before every apply; remote/locked state, no secrets in code or state; pinned providers; idempotent/convergent, no manual drift.
- Tool-agnostic — name Terraform/Pulumi/CloudFormation/CDK/etc. only as examples, never as required.
- Every rule stated with its *why*; house style mirrors `craft-ops/skills/pipeline-authoring/`.
- Follow the spec verbatim: `docs/superpowers/specs/2026-08-09-craft-ops-infrastructure-authoring-design.md`.
- Bump plugin to `0.6.0`; add a CHANGELOG entry; update README (flip the row; retarget the stale "future infrastructure-authoring" prose). Keep the marketplace craft-ops entry version in sync with plugin.json. Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/infrastructure-authoring/SKILL.md`
- `craft-ops/skills/infrastructure-authoring/references/iac-authoring-hygiene.md`
- `craft-ops/skills/infrastructure-authoring/references/testing-and-verifying-infrastructure.md`

Modified:
- `craft-ops/README.md` — flip the `infrastructure-authoring` row to Built; retarget the stale "future `infrastructure-authoring`" prose (line ~71) to present tense.
- `craft-ops/CHANGELOG.md` — `0.6.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.5.1` → `0.6.0`.
- `.claude-plugin/marketplace.json` — craft-ops entry version `0.5.1` → `0.6.0`.

Independence: **Task 1 (skill) lands first** (Task 2's references are cited by it). After Task 1, **Task 2 (references)** is independent. **Task 3 (docs/version)** lands after the skill exists. Task 4 is controller verification.

---

### Task 1: The `infrastructure-authoring` skill

**Files:**
- Create: `craft-ops/skills/infrastructure-authoring/SKILL.md`

**Interfaces:**
- Consumes: the `infrastructure-design` note as input; reference filenames from Task 2 (`iac-authoring-hygiene.md`, `testing-and-verifying-infrastructure.md`).
- Produces: a skill named `infrastructure-authoring`.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/infrastructure-authoring/SKILL.md`. Read `craft-ops/skills/pipeline-authoring/SKILL.md` first and mirror its section shape exactly (Why this exists → Seams → The production-discipline split → Domain rules → Guardrails → Exit condition). Use this frontmatter (name fixed; description states the write-vs-design boundary and the deferral):

```yaml
---
name: infrastructure-authoring
description: "Use when turning an infrastructure design note (from infrastructure-design) into the actual infrastructure-as-code — writing the real IaC (Terraform/Pulumi/CloudFormation/CDK/etc.) and any policy or module logic. Applies opinionated authoring rules: prefer small composable modules over duplicated resource blocks; NEVER co-locate a durable resource inside a compute unit (compute references durable resources by input, never creates them); protect durable resources with lifecycle guards; review the plan before every apply; remote/locked state with no secrets in code or state; pinned providers; idempotent and drift-free. It WRITES the IaC (unlike infrastructure-design, which only designs it), but defers the production loop to craft: policy/module logic is built under strict-tdd, and the declarative resources are proven by verification — validate/plan and apply against a sandbox. Not for deciding the infrastructure's shape (that is infrastructure-design), nor for pipeline, deployment, or observability authoring."
---
```

Body sections:
- `# Infrastructure Authoring — write the infrastructure the design already decided`
- `## Why this exists` — a design note is not applied infrastructure; this turns it into real, reviewed IaC without re-deciding the design or hand-waving the discipline. Unlike `-design` skills it writes code, so it leans on craft.
- `## Seams` — consumes the `infrastructure-design` note (resource tiers, module boundaries, state strategy already decided — do not re-decide); defers the production loop to craft (`strict-tdd`, `verification`, `code-style`, `self-review`), named generically so it degrades without craft; review/verify go to `craft-reviewer`/`craft-verifier`.
- `## The production-discipline split` — policy/module logic (policy-as-code, modules with computed values, generators, scripting) → craft `strict-tdd` (failing test first); the declarative resources → craft `verification` (validate + plan/diff reviewed, then apply against a throwaway/sandbox env). Add the minimum-verification rule: **`validate` + `plan` is always runnable even without an apply target — it catches broken references, type errors, and unexpected destroy/replace offline; the plan is a diff you must READ.**
- `## Domain rules` — lead with **prefer small composable modules over duplicated resource blocks** (see `references/iac-authoring-hygiene.md`) and **never co-locate a durable resource inside a compute unit** (durable in its own unit; compute references it by input; why: compute is disposable and would tear a co-located durable resource down with it). Then: protect durable resources (lifecycle guards, migrate-not-teardown); review the plan before every apply (catches durable destroy/replace or a durable caught in a compute unit's lifecycle); remote/locked/sensitive state, no secrets in code or state; pinned providers; idempotent/convergent, no manual drift. Testing/verifying depth in `references/testing-and-verifying-infrastructure.md`.
- `## Guardrails` — do not re-decide the design (defer to `infrastructure-design`); do not reimplement TDD/verification (defer to craft); never co-locate a durable resource in a compute unit; no secrets in code or state, ever; review the plan before every apply.
- `## Exit condition` — the IaC and any policy/module logic exist; the logic is covered by strict-tdd tests; the declarative resources are verified by `validate`/`plan` (minimum) and apply against a sandbox with the plan read before apply; durable and compute resources are in separate units; committed the craft way — reviewed, no secrets, pinned.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `grep -m1 '^name:' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: `name: infrastructure-authoring`. Confirm a `description:` line exists.

- [ ] **Step 3: Verify the signature rules, the split, and the deferral are present**

Run: `grep -iE 'composable module|duplicat' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: modules-over-duplication rule present.
Run: `grep -iE 'co-locate|durable' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: the never-co-locate-durable-in-compute rule present.
Run: `grep -iE 'validate|plan' craft-ops/skills/infrastructure-authoring/SKILL.md && grep -iE 'strict-tdd' craft-ops/skills/infrastructure-authoring/SKILL.md && grep -iE 'verif' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: the split + validate/plan minimum present.
Run: `grep -iE 'infrastructure-design' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: upstream design deferral stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/infrastructure-authoring/SKILL.md
git commit -m "feat(craft-ops): add infrastructure-authoring skill"
```

---

### Task 2: `infrastructure-authoring` references

**Files:**
- Create: `craft-ops/skills/infrastructure-authoring/references/iac-authoring-hygiene.md`
- Create: `craft-ops/skills/infrastructure-authoring/references/testing-and-verifying-infrastructure.md`

**Interfaces:**
- Produces: the two files cited by Task 1's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write iac-authoring-hygiene.md**

Read `craft-ops/skills/pipeline-authoring/references/pipeline-as-code-hygiene.md` first to match style. Cover the domain rules, each with its *why*, LEADING with **prefer small composable modules over duplicated resource blocks** (extract and parameterize; duplication is how environments drift) and **never co-locate a durable resource inside a compute unit** (durable resources in their own unit with their own lifecycle; compute receives references — IDs/ARNs/endpoints — as inputs and never creates them; because compute is disposable and would tear a co-located durable resource down with it; this is the structural companion to protect-durable and review-before-apply). Then: protect durable resources (lifecycle guards, migrate-not-teardown); remote/locked/sensitive state (never local; no secrets in code or state — inject via a secret manager); pinned provider/module versions; idempotent/convergent (apply-twice is a no-op); no manual drift (import, don't console-tweak).

- [ ] **Step 2: Write testing-and-verifying-infrastructure.md**

Read `craft-ops/skills/pipeline-authoring/references/testing-and-verifying-pipelines.md` first (it has the analogous split + the entrypoint-smoke-invoke minimum-verification section — mirror that shape). Cover: what to unit-test under `strict-tdd` (policy-as-code checks, modules with computed values, generators, scripting — real logic with edge cases); how to verify the declarative resources under `verification` (validate + plan/diff read, then apply against a throwaway/sandbox env observed for convergence — evidence not inspection); the always-runnable minimum: **`validate` + `plan` catches broken references/types/unexpected destroy-replace offline before any apply — the plan is a diff you must READ, the IaC analog of smoke-invoking a script through its real entrypoint**; and review-before-apply as the gate whose first job is catching a durable-resource destroy/replace (or a durable caught inside a compute unit). Each rule with its *why*.

- [ ] **Step 3: Verify files exist, non-empty, and are cited**

Run: `for f in iac-authoring-hygiene testing-and-verifying-infrastructure; do p="craft-ops/skills/infrastructure-authoring/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/infrastructure-authoring/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for both.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/infrastructure-authoring/references/
git commit -m "feat(craft-ops): add infrastructure-authoring reference conventions"
```

---

### Task 3: README, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name (Task 1).

- [ ] **Step 1: Update the README**

In `craft-ops/README.md` "Domains and skills" table, change the row `| Infrastructure as Code | `infrastructure-authoring` (writes the config) | Planned |` to `| Infrastructure as Code | `infrastructure-authoring` | Built |`. Then retarget the stale prose (around line 71) that calls it "the future `infrastructure-authoring` skill" to present tense — refer to it as the now-built sibling that authors the config, consistent with the table (mirror how the `pipeline-authoring` prose was retargeted).

- [ ] **Step 2: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.6.0] — 2026-08-09` section above `## [0.5.1]`, under `### Added`: the `infrastructure-authoring` skill + 2 references (call out modules-over-duplication, the never-co-locate-durable-in-compute rule, protect-durable + review-before-apply, and validate/plan as the always-runnable minimum verification; deferring the production loop to craft and the design to infrastructure-design). Match the format of existing entries.

- [ ] **Step 3: Bump both manifest versions**

Set `version` to `0.6.0` in `craft-ops/.claude-plugin/plugin.json`, and set the `craft-ops` plugin entry's `version` to `0.6.0` in `.claude-plugin/marketplace.json` (they track together). Keep both valid JSON.

- [ ] **Step 4: Verify docs and versions**

Run: `grep -q 'infrastructure-authoring' craft-ops/README.md && grep -q '0.6.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.6.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK` — expected: `DOCS_OK`.
Run: `grep -rn -i 'future' craft-ops/README.md | grep -i 'infrastructure-authoring' || echo "NO_STALE_FUTURE_REF"` — expected: `NO_STALE_FUTURE_REF`.
Confirm the marketplace craft-ops entry reads `0.6.0` and both JSON files are valid.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark infrastructure-authoring built; bump to 0.6.0"
```

---

### Task 4: Final slice verification (controller-run)

**Files:** none — verifies the slice against the spec's success criteria.

- [ ] **Step 1: Verify the tree**

Run: `find craft-ops/skills/infrastructure-authoring -type f | sort` — expected: 1 SKILL.md + 2 references.

- [ ] **Step 2: Verify frontmatter name**

Run: `grep -m1 '^name:' craft-ops/skills/infrastructure-authoring/SKILL.md` — expected: `name: infrastructure-authoring`.

- [ ] **Step 3: Verify signature rules and seams hold**

Confirm the SKILL.md and references state: modules-over-duplication; never-co-locate-durable-in-compute; protect-durable + review-before-apply; the strict-tdd/verification split with `validate`/`plan` as the minimum; the `infrastructure-design` upstream deferral; both references cited.

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec "Success criteria" and confirm each holds. Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## After the plan: behavioral validation (not a plan task)

Validate behaviorally like pipeline-authoring: dispatch `craft-ops-author` on a sample `infrastructure-design` note for a small stack (a durable datastore + a compute service), and confirm the produced IaC honored the rules — durable and compute in *separate* composable units with compute referencing the durable by input, protect-durable lifecycle guards, pinned providers, remote/locked state, no secrets in code or state, and verification via `validate`/`plan` (with the plan read). Interactive; runs after the plan completes.

## Notes for the executor

- Skill/prose deliverables; "tests" are structural checks (frontmatter parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author the `SKILL.md` under **superpowers:writing-skills**; mirror `craft-ops/skills/pipeline-authoring/` throughout (it is the proven template).
- Match the suite's voice: strict rules each with their *why*; no *what*-comments; concise; cite craft / craft-ops roots. Tool-agnostic — IaC tools named only as examples.
- Do not build `deployment-authoring` or `observability-authoring` — this slice is IaC only.
