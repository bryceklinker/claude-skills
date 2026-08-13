# craft-ops-conventions skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Ship the `craft-ops-conventions` skill — the craft-ops portability layer that records and reads a self-contained `.craft-ops.yml` so the generic craft-ops skills read project conventions instead of guessing — bumping the plugin to `0.10.0` and folding into PR #3.

**Architecture:** Extends the existing `craft-ops/` plugin, mirroring craft's `project-conventions` skill (`SKILL.md` + `references/schema.md`) with ops-domain content. Also retargets the four design skills' "until a dedicated conventions skill exists" clauses to point at the now-built skill. No agent changes. The separate `craft` → `craft-code` rebrand is NOT part of this plan.

**Tech Stack:** Markdown skill files with YAML frontmatter; a YAML schema doc; JSON plugin manifest. No application code. Validation is structural: YAML-frontmatter parse, required-keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Skill named exactly `craft-ops-conventions`.
- It manages a **self-contained `.craft-ops.yml`** at the repo root (own `git.main_branch`/`stack`) — never craft's `.craft.yml`; craft-ops stays independently installable.
- Mirror the structure and voice of craft's `project-conventions` skill (read `skills/project-conventions/SKILL.md` and `skills/project-conventions/references/schema.md` as the templates), adapted to the ops domains.
- The read rule is a **HARD-GATE**: before a craft-ops skill/agent runs or generates anything project-specific (IaC plan/apply, deploy/rollout, alert-rule generation, artifact registry / environments / promotion order), it reads `.craft-ops.yml` and uses what it specifies; bootstrap or extend rather than guess silently.
- `.craft-ops.yml` schema covers: `stack`, `git.main_branch`, `environments` (+ promotion order), `cloud` (provider, iac_tool, iac_commands), `cicd` (system, artifact_registry, artifact_identity), `deployment` (tool, rollout_command, rollback_command), `observability` (metrics/dashboards/alerts), `secrets.manager`, `paths` (pipelines/infrastructure/deployments/observability). Only keys a project needs are required.
- Do NOT do the `craft` → `craft-code` rebrand here; reference craft's `project-conventions` by its current name where relevant (the rebrand will sweep later).
- Follow the spec verbatim: `docs/superpowers/specs/2026-08-12-craft-ops-conventions-design.md`.
- Every rule stated with its *why*. Bump plugin to `0.10.0`; add a CHANGELOG entry; update README. Keep the marketplace craft-ops entry version in sync with plugin.json. Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/craft-ops-conventions/SKILL.md`
- `craft-ops/skills/craft-ops-conventions/references/schema.md`

Modified:
- `craft-ops/skills/cicd-pipeline-design/SKILL.md` — retarget the "until a dedicated conventions skill exists" clause.
- `craft-ops/skills/infrastructure-design/SKILL.md` — same.
- `craft-ops/skills/deployment-design/SKILL.md` — same.
- `craft-ops/skills/observability-design/SKILL.md` — same.
- `craft-ops/README.md` — a Conventions/portability note (and list the skill).
- `craft-ops/CHANGELOG.md` — `0.10.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.9.0` → `0.10.0`.
- `.claude-plugin/marketplace.json` — craft-ops entry version `0.9.0` → `0.10.0`.

Independence: **Task 1 (SKILL.md) lands first** (Task 2's schema.md is cited by it). After Task 1, **Task 2 (schema.md)** and **Task 3 (design-skill retargets)** are independent. **Task 4 (docs/version)** lands after the skill exists. Task 5 is controller verification.

---

### Task 1: The `craft-ops-conventions` skill

**Files:**
- Create: `craft-ops/skills/craft-ops-conventions/SKILL.md`

**Interfaces:**
- Consumes: `references/schema.md` (Task 2), cited by name.
- Produces: a skill named `craft-ops-conventions`.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**. First read craft's `skills/project-conventions/SKILL.md` as the template. Then create `craft-ops/skills/craft-ops-conventions/SKILL.md` with this frontmatter (name fixed; description mirrors project-conventions' style, adapted to ops):

```yaml
---
name: craft-ops-conventions
description: "Use to record and read a project's concrete DevOps conventions in a .craft-ops.yml file — the commands and settings the generic craft-ops skills need but can't guess: the environments and promotion order, the cloud and IaC tool plus its plan/apply commands, the CI system and artifact registry, the deploy/rollout tool and rollback command, the observability stack, the secret manager, the base branch, and where each domain's design notes live. Trigger when setting up craft-ops in a new repo, when a skill or agent needs a project-specific ops command it doesn't know, or when the conventions change. Reads .craft-ops.yml at the repo root (self-contained — never craft's .craft.yml) and bootstraps one by discovering the project's tooling when it's absent. Not for designing or authoring pipelines, infrastructure, rollouts, or observability — those are the other craft-ops skills."
---
```

Body (mirror `project-conventions`'s sections):
- `# Craft-Ops Conventions — teach the suite this project's ops commands`
- `## Why this exists` — the portability gap: craft-ops is tool/cloud-agnostic on purpose, so a generic skill can't know how THIS project deploys/provisions/instruments; `.craft-ops.yml` states the concrete commands once and every skill reads them. The discipline is universal; the commands are per-project.
- `## The file` — a single committed `.craft-ops.yml` at the repo root, self-contained (own `git.main_branch`/`stack`, never `.craft.yml`); show a compact example (the schema from the spec); cite `references/schema.md` for the full annotated version + per-stack starters.
- `## Reading it — the rule for every skill and agent` — a **HARD-GATE**: before running/generating anything project-specific (an IaC plan/apply, a deploy/rollout, alert-rule generation, choosing the artifact registry, the environments/promotion order), read `.craft-ops.yml` and use the value it specifies; if a needed key is missing, bootstrap or extend rather than guess.
- `## Bootstrapping a new repo` — discover the tooling (CI config, `*.tf`/Pulumi, `docker-compose`, k8s manifests, dashboards/alert configs), draft the file, confirm the gaps with the user (the newest concepts — the observability stack, the rollout tool), write and commit it.
- `## Keeping it honest` — update `.craft-ops.yml` in the same change when a command/tool changes; a stale conventions file is worse than none because skills trust it.
- `## How the rest of the suite uses it` — a table mapping skill/agent → keys read (e.g. `infrastructure-authoring` → `cloud.iac_commands`; `deployment-authoring` → `deployment.*`; `observability-authoring` → `observability.*`; the design skills → `environments`, `paths.*`; `craft-ops-author` → whichever domain keys its authoring skill needs).
- `## Exit condition` — a committed `.craft-ops.yml` exists at the repo root, accurately states the conventions the suite needs; any skill/agent that must run something reads it first.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `grep -m1 '^name:' craft-ops/skills/craft-ops-conventions/SKILL.md` — expected: `name: craft-ops-conventions`. Confirm a `description:` line exists.

- [ ] **Step 3: Verify the read HARD-GATE, the self-contained note, and the schema citation**

Run: `grep -iE 'HARD-GATE|read .*\.craft-ops\.yml|reads? it first' craft-ops/skills/craft-ops-conventions/SKILL.md` — expected: the read rule is present.
Run: `grep -iE 'self-contained|never .*\.craft\.yml' craft-ops/skills/craft-ops-conventions/SKILL.md` — expected: the self-contained / not-.craft.yml note is present.
Run: `grep -q 'references/schema.md' craft-ops/skills/craft-ops-conventions/SKILL.md && echo CITES_SCHEMA` — expected: `CITES_SCHEMA`.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/craft-ops-conventions/SKILL.md
git commit -m "feat(craft-ops): add craft-ops-conventions skill"
```

---

### Task 2: `references/schema.md`

**Files:**
- Create: `craft-ops/skills/craft-ops-conventions/references/schema.md`

**Interfaces:**
- Produces: the file cited by Task 1's SKILL.md — filename must match exactly.

- [ ] **Step 1: Write schema.md**

Read craft's `skills/project-conventions/references/schema.md` first to match style. Write the full annotated `.craft-ops.yml` schema: every field with what it's for and when it's required (only keys a project needs), covering `stack`, `git.main_branch`, `environments` (+ that the list order is the promotion order), `cloud` (provider, iac_tool, iac_commands.{validate,plan,apply}), `cicd` (system, artifact_registry, artifact_identity), `deployment` (tool, rollout_command, rollback_command), `observability` (metrics, dashboards, alerts), `secrets.manager`, `paths` (pipelines, infrastructure, deployments, observability). Then per-stack **starter `.craft-ops.yml` files** for a few common stacks (e.g. AWS + OpenTofu + GitHub Actions + Argo Rollouts + Prometheus; GCP + Pulumi; a minimal one). Note it is self-contained and never references `.craft.yml`.

- [ ] **Step 2: Verify file exists, non-empty, cited, and covers the schema keys**

Run: `test -s craft-ops/skills/craft-ops-conventions/references/schema.md && grep -q 'references/schema.md' craft-ops/skills/craft-ops-conventions/SKILL.md && echo OK` — expected: `OK`.
Run: `grep -ciE 'environments|iac_tool|artifact_registry|rollout_command|observability|secrets|paths' craft-ops/skills/craft-ops-conventions/references/schema.md` — expected: `5` or more (the schema sections are present).

- [ ] **Step 3: Commit**

```bash
git add craft-ops/skills/craft-ops-conventions/references/
git commit -m "feat(craft-ops): add craft-ops-conventions schema reference"
```

---

### Task 3: Retarget the four design skills' conventions clause

**Files:**
- Modify: `craft-ops/skills/cicd-pipeline-design/SKILL.md`
- Modify: `craft-ops/skills/infrastructure-design/SKILL.md`
- Modify: `craft-ops/skills/deployment-design/SKILL.md`
- Modify: `craft-ops/skills/observability-design/SKILL.md`

**Interfaces:**
- Consumes: the skill name `craft-ops-conventions` (Task 1).

- [ ] **Step 1: Retarget each clause**

In each of the four design skills' "Write it down" section, the sentence ends with "…it documents them until a dedicated conventions skill exists." Change the trailing "— it documents them until a dedicated conventions skill exists." to reference the now-built skill, e.g. "— see `craft-ops-conventions`, which records and reads it." Keep the rest of each sentence (each names slightly different keys — build/test commands, environments, tooling, observability stack) intact; only the trailing "until a dedicated conventions skill exists" clause changes.

- [ ] **Step 2: Verify no stale clause remains and the skill is referenced**

Run: `grep -rl 'dedicated conventions skill' craft-ops/skills/*/SKILL.md || echo "NO_STALE_CLAUSE"` — expected: `NO_STALE_CLAUSE`.
Run: `grep -rl 'craft-ops-conventions' craft-ops/skills/cicd-pipeline-design/SKILL.md craft-ops/skills/infrastructure-design/SKILL.md craft-ops/skills/deployment-design/SKILL.md craft-ops/skills/observability-design/SKILL.md | wc -l | tr -d ' '` — expected: `4` (all four now reference it).

- [ ] **Step 3: Commit**

```bash
git add craft-ops/skills/cicd-pipeline-design/SKILL.md craft-ops/skills/infrastructure-design/SKILL.md craft-ops/skills/deployment-design/SKILL.md craft-ops/skills/observability-design/SKILL.md
git commit -m "docs(craft-ops): point design skills at craft-ops-conventions now that it exists"
```

---

### Task 4: README, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name (Task 1).

- [ ] **Step 1: Update the README**

In `craft-ops/README.md`, add a short **Conventions** note (near the Agents/Design-philosophy sections) describing that `craft-ops-conventions` records and reads a self-contained `.craft-ops.yml` so the skills read project conventions instead of guessing (the portability layer), and that it never uses craft's `.craft.yml`. If there is a skills/domain listing that should include it, add it.

- [ ] **Step 2: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.10.0] — 2026-08-12` section above `## [0.9.0]`, under `### Added`: the `craft-ops-conventions` skill + `references/schema.md` (the portability layer; self-contained `.craft-ops.yml`; read-before-you-guess HARD-GATE + bootstrapping); note the four design skills were retargeted to reference it. Match the format of existing entries (name the reference).

- [ ] **Step 3: Bump both manifest versions**

Set `version` to `0.10.0` in `craft-ops/.claude-plugin/plugin.json`, and set the `craft-ops` plugin entry's `version` to `0.10.0` in `.claude-plugin/marketplace.json` (they track together). Keep both valid JSON.

- [ ] **Step 4: Verify docs and versions**

Run: `grep -q 'craft-ops-conventions' craft-ops/README.md && grep -q '0.10.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.10.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK` — expected: `DOCS_OK`.
Confirm the marketplace craft-ops entry reads `0.10.0` and both JSON files are valid.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): add craft-ops-conventions to README; bump to 0.10.0"
```

---

### Task 5: Final verification (controller-run)

**Files:** none — verifies against the spec's success criteria.

- [ ] **Step 1: Verify the tree**

Run: `find craft-ops/skills/craft-ops-conventions -type f | sort` — expected: `SKILL.md` + `references/schema.md`.

- [ ] **Step 2: Verify frontmatter name**

Run: `grep -m1 '^name:' craft-ops/skills/craft-ops-conventions/SKILL.md` — expected: `name: craft-ops-conventions`.

- [ ] **Step 3: Verify the read-gate, self-contained note, schema, and retargets**

Confirm: the SKILL.md states the read HARD-GATE, the self-contained/not-`.craft.yml` note, and cites `references/schema.md`; `schema.md` covers the schema keys; all four design skills reference `craft-ops-conventions` and none still say "dedicated conventions skill exists"; versions at `0.10.0`.

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec "Success criteria" and confirm each holds. Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## Notes for the executor

- Skill/prose deliverables; "tests" are structural checks (frontmatter parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author the `SKILL.md` and `schema.md` under **superpowers:writing-skills**, mirroring craft's `project-conventions` as the proven template.
- Match the suite's voice: strict rules each with their *why*; no *what*-comments; concise.
- Do NOT do the `craft` → `craft-code` rebrand here — that is a separate deferred effort. Reference craft's `project-conventions` by its current name where needed.
