# craft-ops DevOps Suite (CI/CD first) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring any `SKILL.md`, also use **superpowers:writing-skills** to get frontmatter, trigger-description, and structure right.

**Goal:** Ship a new `craft-ops` sibling plugin — a library of opinionated DevOps skills — with its philosophy layer and its first skill, `cicd-pipeline-design`, fully built and installable independently of `craft`.

**Architecture:** A separate plugin directory `craft-ops/` mirroring `craft`'s layout (its own `plugin.json`, `PRINCIPLES.md`, `README.md`, `CHANGELOG.md`, and `skills/`). It registers as a second plugin in this repo's existing `.claude-plugin/marketplace.json`. `craft-ops` derives its philosophy from `craft`'s `PRINCIPLES.md` and cites it, but hard-requires nothing from craft; its own conventions file is `.craft-ops.yml`.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin/marketplace manifests. No application code. Validation is structural: JSON parse, YAML-frontmatter parse, required-section presence, and cross-reference resolution.

## Global Constraints

- Plugin name is exactly `craft-ops`; first skill is exactly `cicd-pipeline-design` (mirrors `architecture-design` — the name signals it *designs*, not implements).
- `craft-ops` must be **installable independently of `craft`** — no hard dependency on craft files at runtime; principles only *cite* craft.
- `craft-ops` uses its own conventions file `.craft-ops.yml` — never `.craft.yml`.
- The `cicd-pipeline-design` skill **never writes pipeline code or configurations** (generic wording — never say "YAML"). Authoring the definition is a future `pipeline-authoring` skill, name-stubbed only.
- Every strict rule is stated with its *why* (house style from `PRINCIPLES.md`).
- IaC, deployment & release, and observability & incident response are **named one-line stubs** in this build, not implemented.
- Follow the spec at `docs/superpowers/specs/2026-08-06-craft-ops-cicd-design.md` verbatim for principle text and the skill checklist.
- Commit after every task. New files live under `craft-ops/` at the repo root.

---

## File structure

Created in this build:

- `craft-ops/.claude-plugin/plugin.json` — plugin manifest.
- `craft-ops/PRINCIPLES.md` — 8 CI/CD principles (each citing a craft root) + 3 stub domain headers.
- `craft-ops/skills/cicd-pipeline-design/SKILL.md` — the skill (frontmatter + body).
- `craft-ops/skills/cicd-pipeline-design/references/stage-ordering.md`
- `craft-ops/skills/cicd-pipeline-design/references/promotion.md`
- `craft-ops/skills/cicd-pipeline-design/references/reproducible-builds.md`
- `craft-ops/README.md` — suite overview + domain table (built vs. planned).
- `craft-ops/CHANGELOG.md` — `0.1.0` entry.

Modified:

- `.claude-plugin/marketplace.json` — add `craft-ops` as a second plugin entry.

Independence for parallel execution: **Task 1 must land first** (it defines the plugin and registration). After Task 1, **Tasks 2, 3+4, and 5 are independent** and may run in parallel — Task 3 (skill) cites Task 2 (principles) and Task 4 (references) by *filename* only, and those names are fixed in this plan, so no runtime coupling blocks parallel authoring. Reconcile before final verify.

---

### Task 1: Plugin scaffolding + marketplace registration

**Files:**
- Create: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json` (add second entry to `plugins` array)

**Interfaces:**
- Produces: plugin `name: "craft-ops"`; marketplace entry with `source: "./craft-ops"`. Later tasks place files under `craft-ops/`.

- [ ] **Step 1: Write the plugin manifest**

Create `craft-ops/.claude-plugin/plugin.json`:

```json
{
  "name": "craft-ops",
  "description": "An opinionated DevOps skill suite — a library of domain skills (CI/CD, infrastructure as code, deployment & release, observability & incident response) that extends craft's disciplined worldview into operations. Reach for a skill when that concern is in front of you; no single pipeline.",
  "version": "0.1.0",
  "author": {
    "name": "Bryce Klinker"
  },
  "keywords": [
    "devops",
    "cicd",
    "continuous-delivery",
    "infrastructure-as-code",
    "deployment",
    "observability"
  ]
}
```

- [ ] **Step 2: Register the plugin in the marketplace**

In `.claude-plugin/marketplace.json`, add a second object to the `plugins` array (after the existing `craft` entry):

```json
    {
      "name": "craft-ops",
      "source": "./craft-ops",
      "description": "An opinionated DevOps skill suite: a library of domain skills (CI/CD, infrastructure as code, deployment & release, observability & incident response) extending craft's disciplined worldview into operations.",
      "version": "0.1.0",
      "author": { "name": "Bryce Klinker" },
      "keywords": ["devops", "cicd", "continuous-delivery", "infrastructure-as-code", "deployment", "observability"]
    }
```

- [ ] **Step 3: Verify both manifests are valid JSON**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 4: Verify the marketplace lists both plugins**

Run: `python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([p['name'] for p in d['plugins']])"`
Expected: `['craft', 'craft-ops']`

- [ ] **Step 5: Commit**

```bash
git add craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(craft-ops): scaffold plugin and register in marketplace"
```

---

### Task 2: PRINCIPLES.md — the DevOps philosophy layer

**Files:**
- Create: `craft-ops/PRINCIPLES.md`

**Interfaces:**
- Produces: the eight numbered CI/CD principles that `cicd-pipeline-design/SKILL.md` will cite by name; three stub domain headers.

- [ ] **Step 1: Write PRINCIPLES.md**

Create `craft-ops/PRINCIPLES.md`. Open with a short preamble mirroring craft's: this is the canonical *why* for DevOps work; it derives from and cites craft's `PRINCIPLES.md`; every rule is strict on purpose and comes with its reason and an escape hatch. Then the eight CI/CD principles below (copy the intent verbatim from the spec), each as `## N. <title>` with a paragraph and an *(craft: …)* citation where noted:

1. **Build once, promote the same artifact** — never rebuild per environment; one immutable artifact identified by a content/commit digest moves across environments unchanged. *(craft: immutability by default → immutable artifacts.)*
2. **The pipeline is code, versioned with what it ships** — no clicked-together jobs; reviewed like any code and living with the app it builds.
3. **Fast feedback, fail early** — cheapest and most-likely-to-fail stages first; a broken main is a stop-the-line event. *(craft: tests come first, and they are a ratchet.)*
4. **Reproducible, hermetic builds** — same input → same artifact; pinned toolchains, isolated and ephemeral build environments, no network-dependent build steps.
5. **Deploy is not release** — decouple shipping the bits from exposing the behavior; roll forward and back cheaply. *(previews the deployment & release domain.)*
6. **Config and secrets enter from the environment, never the artifact or repo** — one artifact, many environments. *(craft: the domain is independent of how data enters or leaves.)*
7. **Done rests on evidence from the real target** — a deploy is "done" when observed healthy in the environment, not when the job turns green. *(craft: judgment is independent, and "done" rests on evidence.)*
8. **State the why; keep the escape hatch** — inherited verbatim from craft.

Then a `## Coming domains` section (or similar) with three one-line stub headers, each explicitly marked *expanded when that domain is built*:
- **Infrastructure as Code** — declarative, idempotent, immutable infra with review-before-apply. *(stub)*
- **Deployment & release** — progressive delivery, rollback-first, deploy decoupled from release. *(stub)*
- **Observability & incident response** — symptoms over causes, SLOs, blameless and reproducible incident handling. *(stub)*

Close with a *Lineage* line noting it extends craft's methodology into operations.

- [ ] **Step 2: Verify all eight principles and three stubs are present**

Run: `grep -c '^## ' craft-ops/PRINCIPLES.md`
Expected: a count of at least `9` (8 principles + coming-domains header; more if stubs are their own headers).

Run: `grep -ci 'craft:' craft-ops/PRINCIPLES.md`
Expected: `4` or more (the explicit craft citations).

- [ ] **Step 3: Verify the three deferred domains are named as stubs**

Run: `grep -i -E 'infrastructure as code|deployment & release|observability' craft-ops/PRINCIPLES.md`
Expected: all three domains appear.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/PRINCIPLES.md
git commit -m "feat(craft-ops): add PRINCIPLES.md deriving DevOps philosophy from craft"
```

---

### Task 3: The `cicd-pipeline-design` skill

**Files:**
- Create: `craft-ops/skills/cicd-pipeline-design/SKILL.md`

**Interfaces:**
- Consumes: principle titles from `craft-ops/PRINCIPLES.md` (Task 2); reference filenames from Task 4 (`references/stage-ordering.md`, `references/promotion.md`, `references/reproducible-builds.md`).
- Produces: a skill named `cicd-pipeline-design` that emits a pipeline design note.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/cicd-pipeline-design/SKILL.md` with YAML frontmatter. Use this frontmatter (name fixed; description mirrors `architecture-design`'s trigger style — states when to use and the hard boundary):

```yaml
---
name: cicd-pipeline-design
description: "Use when setting up CI/CD for a repo, adding or reordering pipeline stages, reviewing an existing pipeline against conventions, or deciding how an artifact is built, gated, and promoted across environments. Produces a short pipeline design note — the artifact strategy, stage ordering, gate map, promotion flow, reproducibility seams, secrets boundary, and evidence-of-done — with each decision's why. It DESIGNS the pipeline; it never writes the pipeline code or configurations (that is a separate authoring skill). Not for provisioning infrastructure, deployment/release strategy, or observability — those are other craft-ops domains."
---
```

Then a body mirroring `architecture-design/SKILL.md`'s shape:
- `# CI/CD Pipeline Design — decide the shape before you wire it`
- `## Why this exists` — a pipeline wired by guesswork rebuilds per environment, leaks secrets, and orders stages so feedback is slow; deciding the shape once, against the conventions, makes the authoring mechanical. A thinking phase; output is a design note, not pipeline code.
- `## What it decides` — the opinionated checklist, each item one bullet, each tied to its principle:
  - **Artifact strategy** — the single immutable artifact, where stored, how identified (digest). *Build once.*
  - **Stage ordering for fast feedback** — cheapest/most-likely-to-fail first (lint/format → unit → build artifact → integration/acceptance → deploy). *Fail early.* (see `references/stage-ordering.md`)
  - **The gate map** — hard automated gates vs. human promotion gates; where "green main is sacred" stop-the-line applies.
  - **Promotion flow** — the same artifact dev → staging → prod without rebuild; only config/secrets differ. (see `references/promotion.md`)
  - **Reproducibility seams** — pinned toolchain, hermetic/ephemeral env, no network-dependent build steps. (see `references/reproducible-builds.md`)
  - **Secrets & config boundary** — nothing secret in the pipeline definition or artifact; injected at deploy.
  - **Evidence of done** — the health signal proving the deploy is good in the target, not a green job.
- `## Write it down` — save a short design note (e.g. `docs/craft-ops/pipelines/YYYY-MM-DD-<name>.md`): the artifact/stage/gate/promotion decisions with their *why*. Mention it reads `.craft-ops.yml` for project commands/environments if present (documented here until a dedicated conventions skill exists).
- `## Guardrails` — YAGNI on stages/environments; **do not write the pipeline code or configurations here**; prefer the existing shape if a pipeline already fits.
- `## Exit condition` — a written pipeline design note covering all seven checklist items; hand off to the (future) `pipeline-authoring` skill to implement it.

- [ ] **Step 2: Verify the frontmatter parses and the name is exact**

Run: `python3 -c "import sys,yaml; t=open('craft-ops/skills/cicd-pipeline-design/SKILL.md').read().split('---')[1]; d=yaml.safe_load(t); assert d['name']=='cicd-pipeline-design', d['name']; assert 'description' in d; print('OK', d['name'])"`
Expected: `OK cicd-pipeline-design`
(If PyYAML is unavailable, run `head -5 craft-ops/skills/cicd-pipeline-design/SKILL.md` and confirm valid frontmatter by eye.)

- [ ] **Step 3: Verify the boundary wording and all seven checklist items are present**

Run: `grep -i 'never write' craft-ops/skills/cicd-pipeline-design/SKILL.md && ! grep -qi 'yaml' craft-ops/skills/cicd-pipeline-design/SKILL.md && echo BOUNDARY_OK`
Expected: prints a "never write…" line and `BOUNDARY_OK` (confirms the boundary is stated and the word "yaml" is absent).

Run: `grep -ci -E 'artifact strategy|stage ordering|gate map|promotion flow|reproducibility|secrets|evidence of done' craft-ops/skills/cicd-pipeline-design/SKILL.md`
Expected: `7` or more.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/cicd-pipeline-design/SKILL.md
git commit -m "feat(craft-ops): add cicd-pipeline-design skill"
```

---

### Task 4: The three `references/` convention docs

**Files:**
- Create: `craft-ops/skills/cicd-pipeline-design/references/stage-ordering.md`
- Create: `craft-ops/skills/cicd-pipeline-design/references/promotion.md`
- Create: `craft-ops/skills/cicd-pipeline-design/references/reproducible-builds.md`

**Interfaces:**
- Consumes: nothing (standalone reference prose).
- Produces: the three files cited by `SKILL.md` (Task 3) — filenames must match exactly.

- [ ] **Step 1: Write stage-ordering.md**

Create `references/stage-ordering.md`: the fast-feedback ordering rule and its rationale. Cover: order stages cheapest and most-likely-to-fail first (format/lint → unit → build artifact → integration/acceptance → deploy); why fail-early shortens the feedback loop and saves compute; parallelize independent stages but keep the earliest failing signal first; "green main is sacred" stop-the-line. State each rule with its *why*.

- [ ] **Step 2: Write promotion.md**

Create `references/promotion.md`: the build-once/promote-the-same-artifact flow. Cover: build the immutable artifact exactly once, identify it by digest, and promote *that same artifact* dev → staging → prod; only config and secrets differ per environment (injected from the environment); never rebuild for prod; how promotion gates (automated vs. human) fit. State each rule with its *why*.

- [ ] **Step 3: Write reproducible-builds.md**

Create `references/reproducible-builds.md`: hermetic, pinned, ephemeral builds. Cover: same input → same artifact; pin the toolchain and dependencies; isolated ephemeral build environments (fresh each run); no network-dependent or wall-clock-dependent build steps; why reproducibility makes promotion and rollback trustworthy. State each rule with its *why*.

- [ ] **Step 4: Verify all three files exist and are non-empty**

Run: `for f in stage-ordering promotion reproducible-builds; do p="craft-ops/skills/cicd-pipeline-design/references/$f.md"; test -s "$p" && echo "OK $f" || echo "MISSING $f"; done`
Expected: `OK stage-ordering`, `OK promotion`, `OK reproducible-builds`.

- [ ] **Step 5: Verify SKILL.md's citations resolve to these files**

Run: `for f in stage-ordering promotion reproducible-builds; do grep -q "references/$f.md" craft-ops/skills/cicd-pipeline-design/SKILL.md && echo "cited $f" || echo "NOT CITED $f"; done`
Expected: `cited stage-ordering`, `cited promotion`, `cited reproducible-builds`.

- [ ] **Step 6: Commit**

```bash
git add craft-ops/skills/cicd-pipeline-design/references/
git commit -m "feat(craft-ops): add cicd-pipeline-design reference conventions"
```

---

### Task 5: README.md + CHANGELOG.md for craft-ops

**Files:**
- Create: `craft-ops/README.md`
- Create: `craft-ops/CHANGELOG.md`

**Interfaces:**
- Consumes: plugin name and install steps (Task 1); domain names (spec).
- Produces: user-facing entry documentation.

- [ ] **Step 1: Write README.md**

Create `craft-ops/README.md` mirroring `craft`'s README shape:
- Title + one-paragraph description: a sibling to `craft`, a library of opinionated DevOps skills; reach for one when that concern is in front of you; no orchestrator.
- **Installation** section: `/plugin marketplace add bryceklinker/claude-skills` then `/plugin install craft-ops@craft-marketplace`; note it installs independently of `craft`.
- A **domain / skill table** marking built vs. planned:

```markdown
| Domain | Skill | Status |
|--------|-------|--------|
| CI/CD pipelines | `cicd-pipeline-design` | Built |
| CI/CD pipelines | `pipeline-authoring` (writes the definition) | Planned |
| Infrastructure as Code | — | Planned |
| Deployment & release | — | Planned |
| Observability & incident response | — | Planned |
```

- A short **Design philosophy** section pointing at `PRINCIPLES.md` and noting it derives from and cites `craft`'s principles.
- A **Conventions** note: `craft-ops` reads its own `.craft-ops.yml` (never `.craft.yml`), keeping it installable without craft.

- [ ] **Step 2: Write CHANGELOG.md**

Create `craft-ops/CHANGELOG.md` with a Keep-a-Changelog header and a `## [0.1.0] — 2026-08-06` entry under `### Added`: the `craft-ops` plugin; `PRINCIPLES.md` (CI/CD principles + stubbed domains); the `cicd-pipeline-design` skill and its references; marketplace registration.

- [ ] **Step 3: Verify README marks built vs. planned and CHANGELOG has the release**

Run: `grep -q 'cicd-pipeline-design' craft-ops/README.md && grep -qi 'planned' craft-ops/README.md && grep -q '0.1.0' craft-ops/CHANGELOG.md && echo DOCS_OK`
Expected: `DOCS_OK`

- [ ] **Step 4: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md
git commit -m "docs(craft-ops): add README and CHANGELOG"
```

---

### Task 6: Final suite verification

**Files:** none created — this task verifies the whole build against the spec's success criteria.

- [ ] **Step 1: Verify the plugin tree is complete**

Run: `find craft-ops -type f | sort`
Expected: exactly these files —
```
craft-ops/.claude-plugin/plugin.json
craft-ops/CHANGELOG.md
craft-ops/PRINCIPLES.md
craft-ops/README.md
craft-ops/skills/cicd-pipeline-design/SKILL.md
craft-ops/skills/cicd-pipeline-design/references/promotion.md
craft-ops/skills/cicd-pipeline-design/references/reproducible-builds.md
craft-ops/skills/cicd-pipeline-design/references/stage-ordering.md
```

- [ ] **Step 2: Verify independent installability — no hard dependency on craft**

Run: `grep -rin -E '\.craft\.yml|require.*craft\b' craft-ops/ || echo "NO_HARD_DEP"`
Expected: only *citation*-style mentions of craft (in PRINCIPLES/README) — no reference to `.craft.yml` and no "requires craft" language. Confirm by eye that every craft mention is a citation, then the intent of `NO_HARD_DEP` holds.

- [ ] **Step 3: Verify both manifests still parse and list both plugins**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -c "import json; print([p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']])"`
Expected: `['craft', 'craft-ops']`

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read `docs/superpowers/specs/2026-08-06-craft-ops-cicd-design.md` "Success criteria" and confirm each holds: independent install; PRINCIPLES with craft-citing CI/CD principles + truthful stubs; the skill triggers/decides the seven items and never writes pipeline code; README marks built vs. planned. Note any gap and open a follow-up task rather than papering over it.

- [ ] **Step 5: No commit** (verification only — nothing new to record).

---

## Notes for the executor

- These are skill/prose deliverables, so "tests" are structural checks (JSON/YAML parse, section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm regardless.
- Author every `SKILL.md` under **superpowers:writing-skills** — it owns frontmatter, trigger-description quality, and the progressive-disclosure split into `references/`.
- Match `craft`'s existing voice: strict rules, each stated with its *why*; no *what*-comments; concise.
- Do not build the deferred domains or the `pipeline-authoring` skill — they are named stubs only in this build.
