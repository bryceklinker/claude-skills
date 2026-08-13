# craft-ops Infrastructure as Code domain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**.

**Goal:** Add the Infrastructure as Code domain to `craft-ops`: expand `PRINCIPLES.md` with the full IaC principle set and ship the `infrastructure-design` skill (design/review only — never authors config), bumping the plugin to `0.2.0`.

**Architecture:** Extends the existing `craft-ops/` plugin, mirroring the `cicd-pipeline-design` pattern exactly: a thinking/decision skill producing a design note, with `references/` for the mechanics, principles anchored in `PRINCIPLES.md` and citing craft. No new plugin, no orchestrator.

**Tech Stack:** Markdown skill files with YAML frontmatter; JSON plugin/marketplace manifests. No application code. Validation is structural: JSON parse, YAML-frontmatter parse, required-section/keyword presence, cross-reference resolution.

## Global Constraints

- Skill name is exactly `infrastructure-design` (mirrors `cicd-pipeline-design` / craft's `architecture-design` — the name signals it *designs*, not authors).
- The skill **never writes the actual IaC configuration** (Terraform/OpenTofu/Pulumi/CloudFormation/Bicep/etc.). Authoring is a future `infrastructure-authoring` skill, name-stubbed only.
- **Tool-agnostic prose:** name specific tools ONLY as examples of a category (e.g. "a cloud-agnostic tool such as Terraform, OpenTofu, or Pulumi"), never as a required choice, and never hand over authored config in any tool's syntax as the deliverable.
- Three IaC opinions MUST be present and unmistakable: (a) the **disposable-vs-durable** resource tier split — durable resources (databases, object stores, queues, topics, buses) are never deleted/replaced, only protected and migrated; (b) **review-before-apply whose first job is to catch a destroy/replace of a durable resource** (stop-the-line); (c) a **bias toward portable, cloud-agnostic tooling**, with lock-in a deliberate, recorded cost.
- Every strict rule is stated with its *why* (house style from `PRINCIPLES.md`).
- The skill inherits the scope-down house rule from `cicd-pipeline-design`: on a targeted change decide the implicated areas in depth and one-line the rest; on greenfield decide all nine.
- `references/` are exactly `resource-tiers.md`, `state-and-modules.md`, `review-before-apply.md`. Tool-selection guidance lives inline in SKILL.md + PRINCIPLES.md (not a reference).
- Plugin version becomes `0.2.0` in `craft-ops/.claude-plugin/plugin.json`, the `craft-ops` entry of `.claude-plugin/marketplace.json`, and a new `CHANGELOG.md` entry.
- Deployment & release and observability & incident response remain one-line stubs in `PRINCIPLES.md` and Planned in the README.
- Follow the spec at `docs/superpowers/specs/2026-08-08-craft-ops-iac-design.md` verbatim for principle text and the decision checklist.
- Commit after every task. New skill files live under `craft-ops/skills/infrastructure-design/`.

---

## File structure

Created:
- `craft-ops/skills/infrastructure-design/SKILL.md`
- `craft-ops/skills/infrastructure-design/references/resource-tiers.md`
- `craft-ops/skills/infrastructure-design/references/state-and-modules.md`
- `craft-ops/skills/infrastructure-design/references/review-before-apply.md`

Modified:
- `craft-ops/PRINCIPLES.md` — add the IaC principle set; update the "Coming domains" section.
- `craft-ops/README.md` — mark Infrastructure as Code Built; add `infrastructure-authoring` Planned.
- `craft-ops/CHANGELOG.md` — add `0.2.0` entry + link.
- `craft-ops/.claude-plugin/plugin.json` — version `0.2.0`.
- `.claude-plugin/marketplace.json` — `craft-ops` entry version `0.2.0`.

Independence for parallel execution: all four content tasks are logically independent (Task 2 cites Task 1's principles and Task 3's reference filenames by name only, and those names are fixed in this plan). Because they share one working tree, **run implementers sequentially** — concurrent commits to the same branch collide. Suggested order: Task 1 → Task 2 → Task 3 → Task 4, then Task 5 verification.

---

### Task 1: PRINCIPLES.md — Infrastructure as Code principle set

**Files:**
- Modify: `craft-ops/PRINCIPLES.md`

**Interfaces:**
- Produces: the numbered IaC principle titles that `infrastructure-design/SKILL.md` (Task 2) cites.

- [ ] **Step 1: Read the current file**

Read `craft-ops/PRINCIPLES.md`. Current shape: CI/CD principles `## 1.`–`## 8.`, then `## Coming domains` (an intro paragraph + three `*(stub)*` bullets for Infrastructure as Code / Deployment & release / Observability), then a `*Lineage:*` line.

- [ ] **Step 2: Insert the IaC principle section**

Immediately **before** the `## Coming domains` header, insert a new domain section headed `## Infrastructure as Code` followed by these ten principles as `### N. <title>` sub-sections — each a short paragraph stating the rule with its *why*, and the `*(craft: …)*` citation where given. Copy the intent verbatim from the spec:

1. **Declarative desired state, not imperative steps** — describe the end state and let the tool converge; don't script step-by-step mutations. *(craft: failure/behavior modeled as values → desired-state over imperative.)*
2. **Idempotent & convergent** — applying the same configuration repeatedly is always safe and yields the same result.
3. **Immutable where disposable; protected where durable** — split resources into two tiers. Disposable (compute, functions, containers, load balancers, most networking) hold no irreplaceable state: treat as immutable, replace-don't-mutate, rebuilt freely from code. Durable (databases, object/blob stores, queues, topics, event buses — anything holding data or messages) hold state that cannot be rebuilt from code and must **never be deleted or replaced** as a side effect of a change; for them "immutable" means *protect and migrate* — deletion-protection / no-destroy guards, and schema/data migration rather than teardown-and-recreate. Classifying a resource into the wrong tier is how you lose data. *(craft: immutability by default — applied with the realism that state can't be re-derived.)*
4. **Review before apply — first job: catch a destroy/replace of a durable resource** — the plan/diff is the gate; its first, non-negotiable check is whether the plan destroys or replaces any durable resource. A forced replacement of a database or deletion of a queue is stop-the-line: not applied on a green plan, but requiring deliberate, explicit confirmation and usually a migration path. *(craft: judgment is independent, and "done" rests on evidence — the plan is the evidence.)*
5. **State is shared, locked, and sensitive** — remote, versioned, locked state; never local or committed to the repo; treated as a secret.
6. **No manual drift — code is the single source of truth** — no console clicking; drift is detected and reconciled back to code. *(craft: green main is sacred → the code is the truth.)*
7. **Small, composable modules; environment parity through inputs** — reusable modules with clear inputs/outputs; staging and prod built from the same modules, differing only in variables. *(craft: small single-purpose units; the domain is independent of how data enters or leaves.)*
8. **Least privilege; secrets never in code or state** — scoped apply-time credentials; no secrets baked into configuration or state. *(craft: config and secrets enter from the environment.)*
9. **Prefer portable, cloud-agnostic tooling; lock-in is a deliberate, recorded cost** — given a choice, prefer tools not bound to one cloud (Terraform, OpenTofu, Pulumi, Kubernetes) over cloud-specific ones (Bicep, CloudFormation, ARM), and apply the same bias to provisioned tech where a portable equivalent exists. Cloud-specific tools sometimes genuinely win, but create lock-in that's nearly impossible to undo later, so choosing one is a conscious tradeoff recorded with its *why* — never the default. *(craft: state the why; keep the escape hatch.)*
10. **State the why; keep the escape hatch** — inherited verbatim from craft.

- [ ] **Step 3: Update the "Coming domains" section**

Remove the `**Infrastructure as Code** … *(stub)*` bullet (it's now a full section). Update the intro sentence so it reads that CI/CD **and** Infrastructure as Code are covered in full, with the rest scaffolded as stubs. Leave the Deployment & release and Observability & incident-response stub bullets unchanged.

- [ ] **Step 4: Verify**

Run: `grep -c '^### ' craft-ops/PRINCIPLES.md`
Expected: `10` or more (the ten IaC sub-principles).

Run: `grep -iE 'durable|disposable|protect and migrate|destroy or replace|cloud-agnostic|lock-in' craft-ops/PRINCIPLES.md | wc -l`
Expected: `4` or more (the three signature opinions are present).

Run: `grep -iE 'deployment & release|observability' craft-ops/PRINCIPLES.md`
Expected: both still present as stubs.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/PRINCIPLES.md
git commit -m "feat(craft-ops): add Infrastructure as Code principles"
```

---

### Task 2: The `infrastructure-design` skill

**Files:**
- Create: `craft-ops/skills/infrastructure-design/SKILL.md`

**Interfaces:**
- Consumes: IaC principle titles from `craft-ops/PRINCIPLES.md` (Task 1); reference filenames from Task 3 (`references/resource-tiers.md`, `references/state-and-modules.md`, `references/review-before-apply.md`).
- Produces: a skill named `infrastructure-design` that emits an infrastructure design note.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/infrastructure-design/SKILL.md`. Read `craft-ops/skills/cicd-pipeline-design/SKILL.md` first for shape/voice. Use this frontmatter (name fixed; description mirrors `cicd-pipeline-design`'s trigger style — when to use + the design-not-author boundary + the exclusions):

```yaml
---
name: infrastructure-design
description: "Use when deciding the SHAPE of infrastructure or reviewing existing infrastructure-as-code against conventions — what resources a change introduces, how they're grouped into modules, where state lives, how changes are reviewed before apply, and how environments stay in parity. Produces a short infrastructure design note — resource inventory and disposable-vs-durable tiering, tool/tech selection, module composition, state management, change safety, environment parity, identity/least-privilege, drift, and evidence-of-done — each decision with its why. It DESIGNS the infrastructure; it never writes the actual IaC configuration (that is a separate authoring skill). Not for CI/CD pipeline shape, deployment/release strategy, or observability — those are other craft-ops domains."
---
```

Then a body mirroring `cicd-pipeline-design/SKILL.md`'s sections:
- `# Infrastructure Design — decide the shape before you provision it`
- `## Why this exists` — infra wired by guesswork force-replaces a database, leaks state, and locks you into one cloud; deciding the shape once, against the conventions, makes the authoring mechanical. A thinking phase; output is a design note, not IaC configuration.
- `## What it decides` — the nine decision areas, each one bullet tied to its principle:
  - **Resource inventory & tier classification** — enumerate resources; classify each disposable vs. durable; for every durable one, name its deletion-protection / no-destroy guard. (see `references/resource-tiers.md`)
  - **Tool & tech selection** — apply the portability bias; record any lock-in choice with its *why*.
  - **Module boundaries & composition** — modules, inputs/outputs, shared vs. per-environment. (see `references/state-and-modules.md`)
  - **State management** — remote, locked, versioned, isolated, sensitive. (see `references/state-and-modules.md`)
  - **Change safety — review-before-apply & blast radius** — plan/diff gate; whether anything destroys/replaces a durable resource and the migration path if so. (see `references/review-before-apply.md`)
  - **Environment parity** — same modules across environments, differing only in inputs.
  - **Identity, least privilege & secrets** — scoped apply-time credentials; no secrets in code or state.
  - **Drift stance** — how drift is detected and reconciled; nothing changed by hand.
  - **Evidence of done** — plan applied cleanly AND a real post-apply check the infra is in desired state, not "apply exited 0."
- `## Write it down` — save a short design note (e.g. `docs/craft-ops/infrastructure/YYYY-MM-DD-<name>.md`); mention reading `.craft-ops.yml` if present.
- `## Guardrails` — YAGNI on resources/environments; **never write the IaC configuration here**; prefer the existing shape; match the note's length to the change (depth on implicated areas, one line for the rest).
- `## Exit condition` — a written design note accounting for the nine areas (implicated ones in depth, others one-lined); hand off to the future `infrastructure-authoring` skill.

- [ ] **Step 2: Verify frontmatter and name**

Run: `/opt/homebrew/bin/python3.14 -c "import yaml; t=open('craft-ops/skills/infrastructure-design/SKILL.md').read().split('---')[1]; d=yaml.safe_load(t); assert d['name']=='infrastructure-design', d['name']; print('OK', d['name'])"`
Expected: `OK infrastructure-design`
(If PyYAML/py3.14 unavailable, inspect the first 5 lines by eye.)

- [ ] **Step 3: Verify the boundary and the signature opinions are present**

Run: `grep -in 'never write' craft-ops/skills/infrastructure-design/SKILL.md`
Expected: a "never write the IaC configuration" guardrail line.

Run: `grep -icE 'durable|disposable|destroy|replace' craft-ops/skills/infrastructure-design/SKILL.md`
Expected: `1` or more (tiering + destroy/replace safety are in the body).

Run: `for f in resource-tiers state-and-modules review-before-apply; do grep -q "references/$f.md" craft-ops/skills/infrastructure-design/SKILL.md && echo "cited $f" || echo "NOT CITED $f"; done`
Expected: all three cited.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/infrastructure-design/SKILL.md
git commit -m "feat(craft-ops): add infrastructure-design skill"
```

---

### Task 3: The three `references/` convention docs

**Files:**
- Create: `craft-ops/skills/infrastructure-design/references/resource-tiers.md`
- Create: `craft-ops/skills/infrastructure-design/references/state-and-modules.md`
- Create: `craft-ops/skills/infrastructure-design/references/review-before-apply.md`

**Interfaces:**
- Consumes: nothing (standalone reference prose).
- Produces: the three files cited by `SKILL.md` (Task 2) — filenames must match exactly.

- [ ] **Step 1: Write resource-tiers.md**

Read `craft-ops/skills/cicd-pipeline-design/references/promotion.md` for voice. Create `references/resource-tiers.md`: the disposable-vs-durable distinction as the data-safety centerpiece. Cover: how to classify a resource (does it hold state/data/messages that can't be rebuilt from code?); the disposable tier (replace-don't-mutate, rebuilt from code); the durable tier (databases, object/blob stores, queues, topics, buses — never deleted/replaced; deletion-protection and no-destroy lifecycle guards; migrate schema/data rather than teardown-and-recreate); and the failure mode of mis-tiering (data loss from a forced replacement). State each rule with its *why*.

- [ ] **Step 2: Write state-and-modules.md**

Create `references/state-and-modules.md`: state management + module composition + parity. Cover: remote, versioned, locked state, isolated per environment/component, treated as sensitive (never local/committed); small composable modules with clear inputs/outputs; and environment parity — staging and prod built from the same modules, differing only in inputs/variables (env-specific values are inputs, not forks of the code). State each rule with its *why*.

- [ ] **Step 3: Write review-before-apply.md**

Create `references/review-before-apply.md`: the plan/diff gate. Cover: always plan/diff and review before apply; the first, non-negotiable check is whether the plan destroys or replaces a durable resource (stop-the-line, needs explicit confirmation + a migration path); blast-radius thinking (how far a change reaches, isolating risky changes); and idempotent/convergent apply so re-running is safe. State each rule with its *why*.

- [ ] **Step 4: Verify all three exist and are cited**

Run: `for f in resource-tiers state-and-modules review-before-apply; do p="craft-ops/skills/infrastructure-design/references/$f.md"; test -s "$p" && echo "OK $f" || echo "MISSING $f"; done`
Expected: `OK` for all three.

Run: `grep -il -E 'durable|deletion.protection|never.*(delete|destroy|replace)' craft-ops/skills/infrastructure-design/references/resource-tiers.md`
Expected: matches (the durable-protection rule is present).

- [ ] **Step 5: Commit**

```bash
git add craft-ops/skills/infrastructure-design/references/
git commit -m "feat(craft-ops): add infrastructure-design reference conventions"
```

---

### Task 4: README, CHANGELOG, and version bump to 0.2.0

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill name `infrastructure-design` (Task 2).
- Produces: user-facing docs + the `0.2.0` version.

- [ ] **Step 1: Update the README domain table**

In `craft-ops/README.md`, change the row `| Infrastructure as Code | — | Planned |` to `| Infrastructure as Code | \`infrastructure-design\` | Built |`, and add immediately below it a new row: `| Infrastructure as Code | \`infrastructure-authoring\` (writes the config) | Planned |`. Leave the Deployment & release and Observability rows as Planned.

- [ ] **Step 2: Bump plugin.json and marketplace.json to 0.2.0**

In `craft-ops/.claude-plugin/plugin.json`, change `"version": "0.1.0"` to `"version": "0.2.0"`. In `.claude-plugin/marketplace.json`, change the `craft-ops` plugin entry's `"version": "0.1.0"` to `"version": "0.2.0"` (do not touch the `craft` entry).

- [ ] **Step 3: Add the CHANGELOG 0.2.0 entry**

In `craft-ops/CHANGELOG.md`, add a new `## [0.2.0] — 2026-08-08` section above the `0.1.0` entry, under `### Added`: the Infrastructure as Code principle set in `PRINCIPLES.md`; the `infrastructure-design` skill and its three references; the README domain-table update. Add a matching link reference at the bottom mirroring the `0.1.0` link line (`[0.2.0]: https://github.com/bryceklinker/claude-skills/releases/tag/craft-ops-v0.2.0`).

- [ ] **Step 4: Verify**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -c "import json; print([(p['name'],p['version']) for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']])"`
Expected: valid JSON; prints `[('craft', ...), ('craft-ops', '0.2.0')]`.

Run: `grep -q 'infrastructure-design' craft-ops/README.md && grep -qi 'infrastructure-authoring' craft-ops/README.md && grep -q '0.2.0' craft-ops/CHANGELOG.md && grep -q '"version": "0.2.0"' craft-ops/.claude-plugin/plugin.json && echo DOCS_OK`
Expected: `DOCS_OK`

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark Infrastructure as Code built; bump to 0.2.0"
```

---

### Task 5: Final suite verification

**Files:** none created — verifies the whole build against the spec's success criteria.

- [ ] **Step 1: Verify the new skill tree**

Run: `find craft-ops/skills/infrastructure-design -type f | sort`
Expected exactly:
```
craft-ops/skills/infrastructure-design/SKILL.md
craft-ops/skills/infrastructure-design/references/resource-tiers.md
craft-ops/skills/infrastructure-design/references/review-before-apply.md
craft-ops/skills/infrastructure-design/references/state-and-modules.md
```

- [ ] **Step 2: Verify the three signature opinions across the domain**

Run: `grep -rilE 'durable|disposable' craft-ops/PRINCIPLES.md craft-ops/skills/infrastructure-design/`
Expected: PRINCIPLES.md, SKILL.md, and resource-tiers.md all match — the tier distinction is consistent across principles, skill, and reference.

Run: `grep -rilE 'cloud-agnostic|lock-in' craft-ops/PRINCIPLES.md craft-ops/skills/infrastructure-design/SKILL.md`
Expected: the portability bias appears in both principles and the skill.

- [ ] **Step 3: Verify manifests and version**

Run: `python3 -m json.tool craft-ops/.claude-plugin/plugin.json >/dev/null && python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([(p['name'],p['version']) for p in d['plugins']])"`
Expected: valid; `craft-ops` at `0.2.0`, both plugins listed.

- [ ] **Step 4: Confirm against the spec success criteria**

Re-read `docs/superpowers/specs/2026-08-08-craft-ops-iac-design.md` "Success criteria" and confirm each holds: full IaC principle set with tier/destroy-gate/portability opinions; skill triggers and decides the nine areas and never writes config; scope-down behavior available; README marks Built and version is 0.2.0. Note any gap and open a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## Notes for the executor

- Skill/prose deliverables: "tests" are structural checks (JSON/YAML parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author `SKILL.md` under **superpowers:writing-skills**.
- Match `craft-ops`'s established voice: strict rules each with their *why*; no *what*-comments; concise; tools named only as examples, never mandated.
- Do not build `infrastructure-authoring` or the other deferred domains — named stubs only.
- Use `/opt/homebrew/bin/python3.14` for any script needing `str | None` type hints (the default `python3` is 3.9); plain JSON checks work on either.
