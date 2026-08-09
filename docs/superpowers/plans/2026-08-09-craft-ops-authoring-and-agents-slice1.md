# craft-ops authoring + agents (vertical slice 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. When authoring the `SKILL.md`, also use **superpowers:writing-skills**; the agent files follow the shape of the existing `agents/craft-*.md`.

**Goal:** Ship the first authoring vertical for `craft-ops`: the `pipeline-authoring` skill plus the two agents (`craft-ops-designer`, `craft-ops-author`) that leverage the suite, bumping the plugin to `0.5.0` and folding into PR #3.

**Architecture:** Extends the existing `craft-ops/` plugin. `pipeline-authoring` is a thin, opinionated skill that turns a `cicd-pipeline-design` note into the real pipeline definition and **defers the production loop to craft** (`strict-tdd` for extracted logic, `verification` for declarative glue). Two agents mirror craft's agent shape and live in a new `craft-ops/agents/` dir (auto-discovered by the craft-ops plugin): a read-only designer that runs any `-design` skill, and an author that drives an `-authoring` skill under craft's discipline in a worktree.

**Tech Stack:** Markdown skill/agent files with YAML frontmatter; JSON plugin manifest. No application code. Validation is structural: YAML-frontmatter parse, required-keyword presence, cross-reference resolution, JSON parse.

## Global Constraints

- Skill named exactly `pipeline-authoring`; agents named exactly `craft-ops-designer` and `craft-ops-author`.
- `pipeline-authoring` WRITES the pipeline (unlike `cicd-pipeline-design`), but must (a) defer the design decision upstream to `cicd-pipeline-design`, and (b) defer the production loop to craft — naming the discipline generically (test-first for logic, verification for glue, review the diff) and pointing to craft's `strict-tdd` / `verification` / `code-style` / `self-review` as canonical, so it degrades gracefully without craft.
- The core split, stated explicitly: **extracted real logic (scripts/generators/policy) → craft `strict-tdd`; the declarative pipeline glue → craft `verification` (run the real pipeline against a test artifact).**
- FIRST-CLASS domain rule (do not omit): **prefer script files over inline scripts** — non-trivial step bodies live in version-controlled scripts the pipeline calls, never inline; this is what turns step logic into the testable side of the split. Plus: build-once/promote-same-artifact, pinned/hermetic/idempotent steps, no secrets in the definition, DRY across stages, fail-fast ordering matching the design, reviewed like code.
- `craft-ops-designer` produces a design note only — no production code. `craft-ops-author` writes code/config in its own worktree under craft's discipline and is written generically so future authoring skills plug in unchanged.
- `craft-ops-author` reuses craft's `craft-reviewer`/`craft-verifier` for review/verify and `craft-debugger` for root-cause — named generically so it degrades without craft.
- Agents mirror the frontmatter shape of `agents/craft-*.md` (`name`, `description`, `tools`, `model: opus`) and a body that invokes the relevant skills.
- Follow the spec verbatim: `docs/superpowers/specs/2026-08-09-craft-ops-authoring-and-agents-slice1-design.md`.
- Bump plugin to `0.5.0`; add a CHANGELOG entry; update README (mark `pipeline-authoring` Built; add an Agents section). Keep marketplace entry version in sync with plugin.json (they track together). Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

## File structure

Created:
- `craft-ops/skills/pipeline-authoring/SKILL.md`
- `craft-ops/skills/pipeline-authoring/references/pipeline-as-code-hygiene.md`
- `craft-ops/skills/pipeline-authoring/references/testing-and-verifying-pipelines.md`
- `craft-ops/agents/craft-ops-designer.md`
- `craft-ops/agents/craft-ops-author.md`

Modified:
- `craft-ops/README.md` — flip the `pipeline-authoring` row to Built; add an "Agents" section.
- `craft-ops/CHANGELOG.md` — `0.5.0` entry.
- `craft-ops/.claude-plugin/plugin.json` — version `0.4.0` → `0.5.0`.
- `.claude-plugin/marketplace.json` — craft-ops entry version `0.4.0` → `0.5.0`.

Independence for parallel execution: **Task 1 (skill) lands first** (Task 2's references are cited by it; Task 4's author agent references the skill by name). After Task 1, **Task 2 (references), Task 3 (designer agent), and Task 4 (author agent) are independent** (disjoint files; cross-references by fixed name only). **Task 5 (docs/version) lands after skill + agents exist.** Task 6 is controller verification.

---

### Task 1: The `pipeline-authoring` skill

**Files:**
- Create: `craft-ops/skills/pipeline-authoring/SKILL.md`

**Interfaces:**
- Consumes: the `cicd-pipeline-design` note as its input; reference filenames from Task 2 (`pipeline-as-code-hygiene.md`, `testing-and-verifying-pipelines.md`).
- Produces: a skill named `pipeline-authoring` that the `craft-ops-author` agent (Task 4) invokes by name.

- [ ] **Step 1: Author the skill using writing-skills**

Invoke **superpowers:writing-skills**, then create `craft-ops/skills/pipeline-authoring/SKILL.md`. Read `craft-ops/skills/cicd-pipeline-design/SKILL.md` first to match voice. Use this frontmatter (name fixed; description states the write-vs-design boundary and the deferral):

```yaml
---
name: pipeline-authoring
description: "Use when turning a CI/CD pipeline design note (from cicd-pipeline-design) into the actual pipeline definition — writing the real pipeline-as-code and its step scripts. Applies opinionated authoring rules: prefer script files over inline scripts, build once and promote the same artifact, pinned/hermetic/idempotent steps, no secrets in the definition, DRY across stages, fail-fast ordering. It WRITES the pipeline (unlike cicd-pipeline-design, which only designs it), but defers the production loop to craft: extracted logic (scripts/generators) is built under strict-tdd, and the declarative pipeline glue is proven by verification — running the real pipeline against a test artifact. Not for deciding the pipeline's shape (that is cicd-pipeline-design), nor for infrastructure, deployment, or observability authoring."
---
```

Body (mirror the sibling skills' section shape):
- `# Pipeline Authoring — write the pipeline the design already decided`
- `## Why this exists` — a design note is not a running pipeline; this skill turns the note into real, reviewed pipeline-as-code without re-litigating the design or hand-waving the discipline. Unlike the `-design` skills, it *does* write code — so it leans on craft to write it well.
- `## Seams` — consumes the `cicd-pipeline-design` note (upstream design decision — do not re-decide it); defers the production loop to craft (`strict-tdd`, `verification`, `code-style`, `self-review`), named so it degrades without craft; review/verify go to `craft-reviewer`/`craft-verifier`.
- `## The production-discipline split` — state it plainly: extracted real logic (scripts, generators, policy code) → craft `strict-tdd` (failing test first); the declarative pipeline glue → craft `verification` (run the real pipeline against a test artifact and observe it). The skill's job is to maximize the testable side.
- `## Domain rules` — the hygiene rules, each with its *why*, leading with **prefer script files over inline scripts** (see `references/pipeline-as-code-hygiene.md`), then build-once/promote-same-artifact, pinned/hermetic/idempotent, no secrets in the definition, DRY across stages, fail-fast ordering matching the design, reviewed like code. Testing/verifying depth in `references/testing-and-verifying-pipelines.md`.
- `## Guardrails` — do not re-decide the design (defer to `cicd-pipeline-design`); do not reimplement TDD/verification (defer to craft); don't inline non-trivial step logic; no secrets in the definition.
- `## Exit condition` — the pipeline definition plus extracted step scripts exist, the extracted logic is covered by tests (strict-tdd) and the glue verified by running it, committed the craft way.

- [ ] **Step 2: Verify frontmatter parses and name is exact**

Run: `awk '/^---/{c++;next} c==1 && /^name:/{print $2}' craft-ops/skills/pipeline-authoring/SKILL.md` — expected: `pipeline-authoring`. Confirm a `description:` line exists in the frontmatter.

- [ ] **Step 3: Verify the boundary, the split, and the script-files rule are present**

Run: `grep -iE 'script file|inline script' craft-ops/skills/pipeline-authoring/SKILL.md` — expected: the prefer-script-files rule appears.
Run: `grep -iE 'strict-tdd' craft-ops/skills/pipeline-authoring/SKILL.md && grep -iE 'verification|verify' craft-ops/skills/pipeline-authoring/SKILL.md` — expected: both deferrals present (the split).
Run: `grep -iE 'cicd-pipeline-design' craft-ops/skills/pipeline-authoring/SKILL.md` — expected: the upstream design deferral is stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/pipeline-authoring/SKILL.md
git commit -m "feat(craft-ops): add pipeline-authoring skill"
```

---

### Task 2: `pipeline-authoring` references

**Files:**
- Create: `craft-ops/skills/pipeline-authoring/references/pipeline-as-code-hygiene.md`
- Create: `craft-ops/skills/pipeline-authoring/references/testing-and-verifying-pipelines.md`

**Interfaces:**
- Produces: the two files cited by Task 1's SKILL.md — filenames must match exactly.

- [ ] **Step 1: Write pipeline-as-code-hygiene.md**

Read one of `craft-ops/skills/cicd-pipeline-design/references/*.md` first to match style. Cover the domain rules, each with its *why*, leading with **prefer script files over inline scripts** (non-trivial step bodies live in version-controlled scripts the pipeline calls; inline scripts bloat the file, can't be run/tested locally, and can't be reused; extraction is what makes the logic testable). Then: build once and promote the same artifact; pinned tool versions; hermetic and idempotent, re-runnable steps; no secrets in the definition (inject at run time); DRY across stages; fail-fast ordering matching the design; the pipeline is reviewed like code.

- [ ] **Step 2: Write testing-and-verifying-pipelines.md**

Cover the TDD-for-logic / verification-for-glue split made concrete: what to unit-test (the extracted step scripts, generators, policy code) under `strict-tdd`; how to verify the declarative glue (run the real pipeline against a throwaway/test artifact and observe the outcome — evidence, not inspection) under `verification`; and how to keep the untestable surface small (extract logic out of the definition so little glue remains). Each rule with its *why*.

- [ ] **Step 3: Verify files exist, non-empty, and are cited**

Run: `for f in pipeline-as-code-hygiene testing-and-verifying-pipelines; do p="craft-ops/skills/pipeline-authoring/references/$f.md"; test -s "$p" && grep -q "references/$f.md" craft-ops/skills/pipeline-authoring/SKILL.md && echo "OK $f" || echo "FAIL $f"; done` — expected: `OK` for both.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/skills/pipeline-authoring/references/
git commit -m "feat(craft-ops): add pipeline-authoring reference conventions"
```

---

### Task 3: The `craft-ops-designer` agent

**Files:**
- Create: `craft-ops/agents/craft-ops-designer.md`

**Interfaces:**
- Produces: an agent named `craft-ops-designer` that runs any craft-ops `-design` skill.

- [ ] **Step 1: Write the agent**

Read `agents/craft-architect.md` first to match the agent shape (frontmatter + body). Create `craft-ops/agents/craft-ops-designer.md` with this frontmatter:

```yaml
---
name: craft-ops-designer
description: "Dispatch to produce a craft-ops design note for an ops change: run the matching craft-ops -design skill (cicd-pipeline-design, infrastructure-design, deployment-design, or observability-design) and write the note. Give it the request and which domain. It produces a design note only — no production code and no pipeline/infra/rollout/instrumentation configuration. Do NOT use it to author the code that realizes a note (that is craft-ops-author) or to run a live incident (the incident-response skill, in the main thread)."
tools: Read, Grep, Glob, Write, Skill
model: opus
---
```

Body: a short `# Craft-Ops Designer` describing that it starts cold; it picks the `-design` skill matching the named domain, invokes it, and writes the resulting design note where the work lives (`docs/craft-ops/...`); it never writes production code or config; it reports the note's path and key decisions. Mirror the tone of `agents/craft-architect.md`.

- [ ] **Step 2: Verify frontmatter parses, name/model exact, tools include no Edit/Bash-write of code**

Run: `awk '/^---/{c++;next} c==1 && /^name:/{print $2}' craft-ops/agents/craft-ops-designer.md` — expected: `craft-ops-designer`.
Run: `grep -E '^model: opus' craft-ops/agents/craft-ops-designer.md && grep -E '^tools:' craft-ops/agents/craft-ops-designer.md` — expected: both present; the tools line has no `Edit`.

- [ ] **Step 3: Verify it references the four design skills and the no-code boundary**

Run: `grep -c -iE 'cicd-pipeline-design|infrastructure-design|deployment-design|observability-design' craft-ops/agents/craft-ops-designer.md` — expected: ≥ 1 (the four design skills are named).
Run: `grep -iE 'design note only|no production code' craft-ops/agents/craft-ops-designer.md` — expected: the boundary is stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/agents/craft-ops-designer.md
git commit -m "feat(craft-ops): add craft-ops-designer agent"
```

---

### Task 4: The `craft-ops-author` agent

**Files:**
- Create: `craft-ops/agents/craft-ops-author.md`

**Interfaces:**
- Consumes: the `pipeline-authoring` skill name (Task 1); craft's `strict-tdd`/`code-style`/`verification` and `craft-reviewer`/`craft-verifier`/`craft-debugger` by name.
- Produces: an agent named `craft-ops-author`.

- [ ] **Step 1: Write the agent**

Read `agents/craft-implementer.md` first to match the shape (worktree discipline, TDD loop, stay-in-lane, report-back). Create `craft-ops/agents/craft-ops-author.md` with this frontmatter:

```yaml
---
name: craft-ops-author
description: "Dispatch to turn a craft-ops design note into the real code/config for one ops domain, in its own worktree, under craft's production discipline. Give it the design note, the domain, the exact files it may touch, and its worktree/branch. It invokes the matching -authoring skill (e.g. pipeline-authoring), extracts step logic into script files and drives it under strict-tdd, verifies the declarative glue by running it, applies code-style, and commits at green and after refactor. Do NOT use it to decide the design (craft-ops-designer) or to review/verify a finished diff (craft-reviewer / craft-verifier)."
tools: Read, Write, Edit, Bash, Grep, Glob, Skill
model: opus
---
```

Body: a `# Craft-Ops Author` describing that it starts cold and reads its task (the design note, domain, files-it-may-touch, worktree/branch). It invokes the matching `-authoring` skill (for CI/CD, `pipeline-authoring`) plus craft's `strict-tdd` and `code-style`; it extracts non-trivial step logic into script files and drives that logic red→green→refactor, commits at green and after refactor separately, and verifies the declarative glue by running the real pipeline (craft `verification`). It stays in its lane (only assigned files; report if it needs a shared file), does not decide the design, and hands review/verify to `craft-reviewer`/`craft-verifier` and root-cause to `craft-debugger`. Written generically — the only domain-specific choice is which `-authoring` skill to invoke — so future authoring skills plug in unchanged. Reports branch/worktree, criteria covered, and commit SHAs.

- [ ] **Step 2: Verify frontmatter parses, name/model exact, tools include Edit+Bash**

Run: `awk '/^---/{c++;next} c==1 && /^name:/{print $2}' craft-ops/agents/craft-ops-author.md` — expected: `craft-ops-author`.
Run: `grep -E '^model: opus' craft-ops/agents/craft-ops-author.md && grep -E '^tools:.*Edit' craft-ops/agents/craft-ops-author.md` — expected: both present.

- [ ] **Step 3: Verify it invokes the authoring skill + craft discipline and stays generic**

Run: `grep -iE 'pipeline-authoring' craft-ops/agents/craft-ops-author.md` — expected: present.
Run: `grep -iE 'strict-tdd' craft-ops/agents/craft-ops-author.md && grep -iE 'verification|verify' craft-ops/agents/craft-ops-author.md` — expected: both (the split).
Run: `grep -iE 'craft-reviewer|craft-verifier' craft-ops/agents/craft-ops-author.md` — expected: reuse of craft's team is stated.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/agents/craft-ops-author.md
git commit -m "feat(craft-ops): add craft-ops-author agent"
```

---

### Task 5: README, CHANGELOG, and version bump

**Files:**
- Modify: `craft-ops/README.md`
- Modify: `craft-ops/CHANGELOG.md`
- Modify: `craft-ops/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the skill and agent names (Tasks 1, 3, 4).

- [ ] **Step 1: Update the README**

In `craft-ops/README.md` "Domains and skills" table, change the row
`| CI/CD pipelines | `pipeline-authoring` (writes the definition) | Planned |`
to `| CI/CD pipelines | `pipeline-authoring` | Built |`.
Then add a new `## Agents` section after the domain table describing the two agents in 1–2 sentences each: `craft-ops-designer` (runs any `-design` skill → a design note; no production code) and `craft-ops-author` (turns a design note into real code/config in a worktree under craft's strict-tdd/verification, reusing craft's reviewer/verifier). Note authoring skills defer the production loop to craft and degrade gracefully without it.

- [ ] **Step 2: Add the CHANGELOG entry**

In `craft-ops/CHANGELOG.md`, add a `## [0.5.0] — 2026-08-09` section above `## [0.4.0]`, under `### Added`: the `pipeline-authoring` skill + 2 references (call out prefer-script-files-over-inline and the TDD-for-logic / verification-for-glue split, deferring the production loop to craft); the `craft-ops-designer` and `craft-ops-author` agents (a new `craft-ops/agents/` dir); README/version updates. Match the format of existing entries.

- [ ] **Step 3: Bump both manifest versions**

Set `version` to `0.5.0` in `craft-ops/.claude-plugin/plugin.json`, and set the `craft-ops` plugin entry's `version` to `0.5.0` in `.claude-plugin/marketplace.json` (they track together). Keep both valid JSON.

- [ ] **Step 4: Verify docs and versions**

Run: `grep -q 'pipeline-authoring' craft-ops/README.md && grep -qi '## Agents' craft-ops/README.md && grep -q '0.5.0' craft-ops/CHANGELOG.md && python3 -c "import json;assert json.load(open('craft-ops/.claude-plugin/plugin.json'))['version']=='0.5.0'; m=json.load(open('.claude-plugin/marketplace.json')); assert [p for p in m['plugins'] if p['name']=='craft-ops'][0]['version']=='0.5.0'" && echo DOCS_OK` — expected: `DOCS_OK`.

- [ ] **Step 5: Commit**

```bash
git add craft-ops/README.md craft-ops/CHANGELOG.md craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs(craft-ops): mark pipeline-authoring built, add agents; bump to 0.5.0"
```

---

### Task 6: Final slice verification (controller-run)

**Files:** none — verifies the slice against the spec's success criteria.

- [ ] **Step 1: Verify the tree**

Run: `find craft-ops/skills/pipeline-authoring craft-ops/agents -type f | sort` — expected: 1 SKILL.md + 2 references + 2 agent files.

- [ ] **Step 2: Verify all frontmatter names**

Run the three `awk` name checks (Tasks 1, 3, 4) — expected: `pipeline-authoring`, `craft-ops-designer`, `craft-ops-author`.

- [ ] **Step 3: Verify seams/boundaries hold**

Confirm: `pipeline-authoring` cites both references and states the script-files rule, the TDD/verification split, and the `cicd-pipeline-design` deferral; `craft-ops-designer` names the four design skills and the no-code boundary; `craft-ops-author` names `pipeline-authoring`, the split, and craft's reviewer/verifier.

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec "Success criteria" and confirm each holds. Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## After the plan: behavioral validation (not a plan task)

`pipeline-authoring` writes code, so validate it **behaviorally** (not with the design-note eval loop): dispatch `craft-ops-author` on a sample `cicd-pipeline-design` note and confirm the produced pipeline honored the domain rules — script files not inline, no secrets in the definition, pinned versions, extracted logic covered by tests, glue verified by running it. Interactive; runs after the plan completes.

## Notes for the executor

- These are skill/agent/prose deliverables; "tests" are structural checks (frontmatter parse, keyword/section presence, cross-reference resolution), not code test cycles. Keep the frequent-commit rhythm.
- Author the `SKILL.md` under **superpowers:writing-skills**; model the agent files on `agents/craft-architect.md` (designer) and `agents/craft-implementer.md` (author).
- Match the suite's voice: strict rules each with their *why*; no *what*-comments; concise; cite craft / craft-ops roots.
- Do not build the other three authoring skills — this slice is CI/CD only.
