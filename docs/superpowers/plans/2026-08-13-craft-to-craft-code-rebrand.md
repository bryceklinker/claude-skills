# craft → craft-code Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the code suite `craft` → `craft-code` across both plugins — plugin identity, the 9 agents, the conventions skill, `.craft.yml`, the `craft:` namespace, and all branding — without corrupting `craft-ops` / `craft-marketplace`, folded into PR #3.

**Architecture:** A purely mechanical, cross-plugin rename executed as small, individually-verified **passes**. Each pass runs a surgical, token-specific replacement over the tracked-file set, then a **guard check** confirming no protected token (`craft-ops`, `craft-marketplace`, `craft-ops-conventions`, `.craft-ops.yml`, `craft-ops-*`, already-renamed `craft-code-*`) was mangled. No behavior changes.

**Tech Stack:** Markdown + JSON. `perl -pi` / `git mv` for surgical edits; `grep` for guards. No application code.

## Global Constraints

- Rename `craft` → `craft-code` for: plugin identity; the 9 agents (`craft-architect, craft-implementer, craft-planner, craft-reconciler, craft-reviewer, craft-verifier, craft-debugger, craft-designer, craft-acceptance-tester`); the conventions skill (`project-conventions` → `craft-code-conventions`); the config file (`.craft.yml` → `.craft-code.yml`); the skill namespace (`craft:` → `craft-code:`); and all `craft`/`Craft` branding prose.
- **PROTECT (never change):** `craft-marketplace`; `craft-ops` and everything under it named craft-ops (`craft-ops`, `craft-ops-conventions`, `craft-ops-author`, `craft-ops-designer`, `.craft-ops.yml`); already-renamed `craft-code-*` tokens.
- **The sweep file set** is tracked files only (so gitignored `*-workspace/` scratch is auto-excluded), .md under `skills/`, `agents/`, `craft-ops/`, plus root `README.md`/`PRINCIPLES.md`, and **excluding both `CHANGELOG.md` files** (changelog history is append-only — preserved, with new rename entries added in Task 7). Recompute per task:
  `FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)`
- After EVERY replacement pass, run the **guard**: `grep -rnE 'craft-code-ops|craft-code-marketplace|craft-code-ops-conventions|craft-code-code-' $FILES` must return nothing, and `craft-ops`/`craft-marketplace`/`.craft-ops.yml` must still be present and intact.
- `craft-code` inherits version **0.4.0** (its marketplace entry synced from stale `0.1.0`); `craft-ops` → **0.11.0**. Both CHANGELOGs note the rename.
- Follow the spec: `docs/superpowers/specs/2026-08-13-craft-to-craft-code-rebrand-design.md`. Commit after every task. Build on `feat/craft-ops-cicd` (PR #3).

---

### Task 1: Rename the 9 agents (files + frontmatter + all references)

**Files:** `agents/craft-*.md` (renamed) + every tracked .md referencing an agent name.

- [ ] **Step 1: Rename the agent files**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
for r in architect implementer planner reconciler reviewer verifier debugger designer acceptance-tester; do
  git mv "agents/craft-$r.md" "agents/craft-code-$r.md"
done
ls agents/   # expect craft-code-*.md x9, no craft-<role>.md
```

- [ ] **Step 2: Replace all references to the 9 agent names (frontmatter + prose, both plugins)**

```bash
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
for r in architect implementer planner reconciler reviewer verifier debugger designer acceptance-tester; do
  perl -pi -e "s/\\bcraft-$r\\b/craft-code-$r/g" $FILES
done
```
(Word-boundary `\bcraft-<role>\b` — `craft-ops-designer`/`craft-ops-author` do NOT contain the literal `craft-designer` etc., so they're untouched.)

- [ ] **Step 3: Guard + verify**

```bash
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
grep -rnE 'craft-code-code-|craft-code-ops' $FILES && echo "CORRUPTION" || echo "guard OK"
grep -rhoE '\bcraft-(architect|implementer|planner|reconciler|reviewer|verifier|debugger|designer|acceptance-tester)\b' $FILES | sort -u   # expect EMPTY
grep -rl 'craft-ops-designer\|craft-ops-author' craft-ops/agents/ >/dev/null && echo "craft-ops agents intact"
for r in architect implementer planner reconciler reviewer verifier debugger designer acceptance-tester; do grep -q "^name: craft-code-$r" "agents/craft-code-$r.md" && echo "OK $r" || echo "FAIL $r"; done
```
Expected: `guard OK`, empty old-name list, craft-ops agents intact, `OK` for all 9 frontmatter names.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor(craft-code): rename the 9 craft-* agents to craft-code-*"
```

---

### Task 2: Rename `project-conventions` → `craft-code-conventions`

**Files:** `skills/project-conventions/` (renamed) + every reference.

- [ ] **Step 1: Rename the skill dir + replace references**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
git mv skills/project-conventions skills/craft-code-conventions
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
perl -pi -e 's/project-conventions/craft-code-conventions/g' $FILES
```
(Literal `project-conventions` — does not match `craft-ops-conventions`, so craft-ops's conventions skill is untouched. This also turns `craft:project-conventions` → `craft:craft-code-conventions`; the `craft:` prefix is fixed in Task 4.)

- [ ] **Step 2: Guard + verify**

```bash
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
grep -rn 'project-conventions' $FILES && echo "RESIDUAL" || echo "no residual project-conventions"
grep -q '^name: craft-code-conventions' skills/craft-code-conventions/SKILL.md && echo "frontmatter OK"
grep -rq 'craft-ops-conventions' craft-ops/skills/craft-ops-conventions/SKILL.md && echo "craft-ops-conventions intact"
grep -rnE 'craft-code-ops|craft-code-code-' $FILES && echo "CORRUPTION" || echo "guard OK"
```
Expected: no residual, frontmatter OK, craft-ops-conventions intact, guard OK.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor(craft-code): rename project-conventions skill to craft-code-conventions"
```

---

### Task 3: `.craft.yml` → `.craft-code.yml`

- [ ] **Step 1: Replace + guard**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
perl -pi -e 's/\.craft\.yml/.craft-code.yml/g' $FILES
grep -rn '\.craft\.yml\b' $FILES | grep -v '\.craft-code\.yml' && echo "RESIDUAL" || echo "no residual .craft.yml"
grep -rq '\.craft-ops\.yml' craft-ops/ && echo ".craft-ops.yml intact"
```
Expected: no residual `.craft.yml`, `.craft-ops.yml` intact. (Literal `.craft.yml` never matches `.craft-ops.yml`.)

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "refactor(craft-code): rename .craft.yml -> .craft-code.yml"
```

---

### Task 4: `craft:` namespace → `craft-code:`

- [ ] **Step 1: Replace + guard**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
perl -pi -e 's/\bcraft:/craft-code:/g' $FILES
grep -rnE '\bcraft:[a-z]' $FILES && echo "RESIDUAL" || echo "no residual craft: namespace"
grep -rnE 'craft-code-code:|craft-code:craft-code-conventions' $FILES | head   # craft-code:craft-code-conventions is CORRECT and expected
grep -rnE 'craft-code-ops|craft-code-code-[a-z]' $FILES && echo "CORRUPTION" || echo "guard OK"
```
Expected: no residual `craft:`; `craft-code:strict-tdd` etc. now present; `craft-code:craft-code-conventions` present (correct); guard OK.

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "refactor(craft-code): rename craft: skill namespace to craft-code:"
```

---

### Task 5: Plugin manifests + install command

**Files:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md` (install command).

- [ ] **Step 1: Rename the plugin identity in the manifests**

In `.claude-plugin/plugin.json` (the craft-code plugin manifest at the repo root), change `"name": "craft"` → `"name": "craft-code"` (leave `version: 0.4.0` as-is).
In `.claude-plugin/marketplace.json`, in the plugin entry whose `"source": "./"` (the code plugin), change `"name": "craft"` → `"name": "craft-code"` and its `"version": "0.1.0"` → `"0.4.0"`. Do NOT touch the `craft-marketplace` marketplace `name`, and do NOT touch the `craft-ops` entry here.

- [ ] **Step 2: Update the install command in README**

In `craft-ops/README.md` and the root `README.md`, update any `/plugin install craft@craft-marketplace` to `/plugin install craft-code@craft-marketplace`. (`craft-marketplace` stays.)

- [ ] **Step 3: Verify manifests**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
python3 -m json.tool .claude-plugin/plugin.json >/dev/null && python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo JSON_OK
python3 -c "import json;print('plugin:',json.load(open('.claude-plugin/plugin.json'))['name']);m=json.load(open('.claude-plugin/marketplace.json'));print('marketplace name:',m['name']);print('entries:',[(p['name'],p['version']) for p in m['plugins']])"
grep -rn 'install craft@' README.md craft-ops/README.md && echo "STALE INSTALL CMD" || echo "install cmd updated"
```
Expected: `JSON_OK`; plugin `craft-code`; marketplace name `craft-marketplace`; entries `[('craft-code','0.4.0'), ('craft-ops','0.10.0')]` (craft-ops version bumped in Task 7); no stale install cmd.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json README.md craft-ops/README.md
git commit -m "refactor(craft-code): rename plugin identity craft -> craft-code in manifests + install cmd"
```

---

### Task 6: Branding prose — standalone `craft`/`Craft` → `craft-code`/`Craft-Code`

**Files:** the sweep set (excludes CHANGELOGs). This is the highest-risk pass — the guard and an eyeball of the diff are mandatory.

- [ ] **Step 1: Replace standalone suite-name occurrences**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
# lowercase 'craft' as a whole word NOT followed by '-', ':', or a word char (so craft-ops/craft-marketplace/craft-code/craftsmanship are excluded)
perl -pi -e 's/\bcraft(?![-\w:])/craft-code/g' $FILES
# capitalized 'Craft' as a whole word not followed by '-' or a word char (titles: "Craft Principles", "Craft Architect")
perl -pi -e 's/\bCraft(?![-\w])/Craft-Code/g' $FILES
```

- [ ] **Step 2: Guard — nothing protected was corrupted**

```bash
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md | grep -E '\.md$' | grep -v CHANGELOG)
grep -rnE 'craft-code-ops|craft-code-marketplace|craft-code-ops-conventions|craft-code-code-|Craft-Code-Ops' $FILES && echo "CORRUPTION" || echo "guard OK"
grep -rq 'craft-ops' craft-ops/README.md && echo "craft-ops intact"
grep -rq 'craft-marketplace' README.md craft-ops/README.md && echo "craft-marketplace intact"
# residual standalone suite-name 'craft' (should be none outside craft-ops/craft-code/craft-marketplace):
grep -rnP '\bcraft(?![-\w:])' $FILES && echo "RESIDUAL craft" || echo "no residual standalone craft"
grep -rnP '\bCraft(?![-\w])' $FILES && echo "RESIDUAL Craft" || echo "no residual standalone Craft"
```
Expected: guard OK; craft-ops + craft-marketplace intact; no residual standalone craft/Craft.

- [ ] **Step 3: Eyeball the diff for false positives**

Run `git diff --stat` then scan `git diff` for any place where an English-word "craft" (not the suite) was wrongly changed, or a compound token was mangled. Fix any false positive by hand. (Expected false-positive rate is near zero in these docs, but this pass earns a human look.)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor(craft-code): rebrand craft -> craft-code across prose in both plugins"
```

---

### Task 7: Versions + CHANGELOG entries

**Files:** `craft-ops/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md` (root, craft-code's), `craft-ops/CHANGELOG.md`.

- [ ] **Step 1: Bump craft-ops to 0.11.0 (plugin + marketplace)**

Set `version` `0.10.0` → `0.11.0` in `craft-ops/.claude-plugin/plugin.json`, and the `craft-ops` entry's `version` `0.10.0` → `0.11.0` in `.claude-plugin/marketplace.json`. (craft-code stays 0.4.0; its marketplace entry was set to 0.4.0 in Task 5.) Keep JSON valid.

- [ ] **Step 2: CHANGELOG entries in both plugins**

In `craft-ops/CHANGELOG.md`, add a `## [0.11.0] — 2026-08-13` section under `### Changed`: "Renamed all references to the code suite from `craft` to `craft-code` (plugin, agents `craft-code-*`, `craft-code:` namespace, `craft-code-conventions`, `.craft-code.yml`) following the code-suite rebrand; no behavior change." In the root `CHANGELOG.md` (craft-code's), add a dated top note recording the rename: the plugin is now `craft-code` (installs as `craft-code@craft-marketplace`), `project-conventions` → `craft-code-conventions`, agents `craft-code-*`, `.craft.yml` → `.craft-code.yml`; version continuity kept at 0.4.0. Match each file's existing changelog format. (Do NOT rewrite historical entries.)

- [ ] **Step 3: Verify versions**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
python3 -c "import json;print('craft-code plugin', json.load(open('.claude-plugin/plugin.json'))['version']);print('craft-ops plugin', json.load(open('craft-ops/.claude-plugin/plugin.json'))['version']);m=json.load(open('.claude-plugin/marketplace.json'));print('marketplace', [(p['name'],p['version']) for p in m['plugins']])"
grep -q '0.11.0' craft-ops/CHANGELOG.md && grep -qi 'craft-code' CHANGELOG.md && echo CHANGELOGS_OK
```
Expected: craft-code plugin 0.4.0, craft-ops plugin 0.11.0, marketplace `[('craft-code','0.4.0'),('craft-ops','0.11.0')]`, CHANGELOGS_OK.

- [ ] **Step 4: Commit**

```bash
git add craft-ops/.claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md craft-ops/CHANGELOG.md
git commit -m "chore: bump craft-ops to 0.11.0, sync marketplace, record the craft-code rename in both changelogs"
```

---

### Task 8: Final global verification (controller-run)

**Files:** none — verifies the whole rename against the spec's success criteria.

- [ ] **Step 1: No protected token corrupted (across ALL tracked files)**

```bash
cd /Users/bryce.klinker/code/personal/claude-skills
ALL=$(git ls-files | grep -E '\.(md|json)$' | grep -v -E '/-?workspace|-workspace/')
grep -rnE 'craft-code-ops|craft-code-marketplace|craft-code-ops-conventions|craft-code-code-|Craft-Code-Ops' $ALL && echo "CORRUPTION FOUND" || echo "no corruption"
grep -rl 'craft-ops' $ALL >/dev/null && grep -rl 'craft-marketplace' $ALL >/dev/null && echo "craft-ops + craft-marketplace present"
```

- [ ] **Step 2: No residual old tokens (outside CHANGELOG history + gitignored workspaces)**

```bash
FILES=$(git ls-files skills agents craft-ops README.md PRINCIPLES.md .claude-plugin | grep -E '\.(md|json)$' | grep -v CHANGELOG)
grep -rhoE '\bcraft-(architect|implementer|planner|reconciler|reviewer|verifier|debugger|designer|acceptance-tester)\b' $FILES | sort -u   # empty
grep -rnE '\bcraft:[a-z]' $FILES     # empty
grep -rn 'project-conventions' $FILES   # empty
grep -rn '\.craft\.yml\b' $FILES | grep -v craft-code   # empty
grep -rnP '\bcraft(?![-\w:])' $FILES     # empty (no standalone suite-name craft)
```
All expected EMPTY.

- [ ] **Step 3: Identity + agents present under new names**

```bash
ls agents/ | grep -c '^craft-code-'   # expect 9
python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['name'])"   # craft-code
ls skills/craft-code-conventions/SKILL.md && echo "conventions skill renamed"
```

- [ ] **Step 4: Confirm against the spec's success criteria**

Re-read the spec "Success criteria" and confirm each holds. Note any gap as a follow-up rather than papering over it.

- [ ] **Step 5: No commit** (verification only).

---

## Notes for the executor

- This is a mechanical rename — the value is in the surgical precision and the guards, not judgment. Run the exact commands; do not improvise a broad `s/craft/craft-code/`.
- `git ls-files` is the sweep set precisely because it excludes gitignored `*-workspace/` eval scratch — never sweep those.
- CHANGELOG history is append-only: preserve old entries, add new ones.
- If any guard reports CORRUPTION or a residual, STOP and fix before committing that task.
