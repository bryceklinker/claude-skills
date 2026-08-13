# Rebrand: `craft` → `craft-code`

*Design spec — 2026-08-13*

## Purpose

The code-crafting suite is currently named `craft`; the ops suite is `craft-ops`. To make the naming
symmetric and self-describing — "craft" is really *crafting code*, "craft-ops" is *crafting ops* —
rename the code plugin and everything it exposes from `craft` to `craft-code`. The umbrella that hosts
both suites stays `craft` (the marketplace remains `craft-marketplace`); only the code *plugin* and its
artifacts are renamed.

This is a **repo-wide, cross-plugin rename**: it touches the `craft-code` plugin comprehensively AND
every reference to it inside `craft-ops` (which defers to it, reuses its agents, and cites its
principles). It adds no behavior — it is purely a rename — but it is large and has a real corruption
hazard, so it is executed as small, individually-verified passes.

## What renames (and what does NOT)

**Renames `craft` → `craft-code`:**
- **Plugin identity** — `.claude-plugin/plugin.json` `name: craft` → `craft-code`; the `craft` entry in
  `.claude-plugin/marketplace.json` `name: craft` → `craft-code`. Source stays `"./"` (no dir move).
  Install command becomes `/plugin install craft-code@craft-marketplace`.
- **The 9 agents** — `agents/craft-<role>.md` → `agents/craft-code-<role>.md` (files renamed),
  frontmatter `name:` updated, and every reference across BOTH plugins updated:
  `craft-architect, craft-implementer, craft-planner, craft-reconciler, craft-reviewer, craft-verifier,
  craft-debugger, craft-designer, craft-acceptance-tester` → `craft-code-*`. (~107 references; note
  craft-ops's `craft-ops-author` reuses `craft-reviewer`/`craft-verifier`/`craft-debugger`.)
- **The conventions skill** — `skills/project-conventions/` → `skills/craft-code-conventions/`;
  frontmatter `name: project-conventions` → `craft-code-conventions`; all ~14 references
  (`craft:project-conventions`, prose) updated. craft-ops's mentions of "craft's project-conventions"
  (the analog) update to "craft-code's craft-code-conventions".
- **The config file** — `.craft.yml` → `.craft-code.yml` (18 referencing files); craft-ops-conventions's
  "never craft's `.craft.yml`" note updates to `.craft-code.yml`.
- **The skill namespace** — `craft:<skill>` → `craft-code:<skill>` (~18 refs, e.g.
  `craft:strict-tdd`, `craft:code-style`).
- **Branding/prose** — "craft"/"Craft" as the suite name in `README.md`, `PRINCIPLES.md`
  ("Craft Principles" → "Craft-Code Principles"), `CHANGELOG.md`, and all of craft-ops's
  "defers to craft", "derives from craft's PRINCIPLES", "reuse craft's reviewer" prose → "craft-code".

**Does NOT change (protect these):**
- `craft-marketplace` — the umbrella marketplace name stays.
- `craft-ops` and everything under it that is genuinely named craft-ops: `craft-ops`,
  `craft-ops-conventions`, `craft-ops-author`, `craft-ops-designer`, `.craft-ops.yml`.
- The already-renamed `craft-code-*` tokens (don't double-rename).

## The corruption hazard and the discipline that defuses it

"craft" is a substring of `craft-ops`, `craft-marketplace`, `craft-ops-conventions`,
`craft-ops-author/designer`, and the new `craft-code-*`. A blanket `s/craft/craft-code/g` would corrupt
all of them (e.g. `craft-ops` → `craft-code-ops`, `craft-marketplace` → `craft-code-marketplace`).

Every replacement is therefore **surgical and token-specific**, not a broad substitution:

- **Exact literal tokens** where possible: `.craft.yml` → `.craft-code.yml`; `craft:` → `craft-code:`;
  each of the 9 exact agent names (`craft-architect` → `craft-code-architect`, …); `project-conventions`
  → `craft-code-conventions`. These literals never match `craft-ops`/`craft-marketplace`.
- **Standalone "craft"** in prose (the suite name) is replaced only where it is NOT followed by `-`
  (so `craft-ops`, `craft-marketplace`, `craft-code` are excluded) — e.g. `craft(?![-\w])` /
  "craft" as a whole word not followed by a hyphen, covering "craft", "craft's", "craft.".
- **After every pass, a guard check**: confirm `craft-ops`, `craft-marketplace`, `craft-ops-conventions`,
  and `craft-code-<role>` were not mangled into `craft-code-ops`, `craft-code-marketplace`,
  `craft-code-code-*`, etc. Any such hit fails the pass.

## Versions

- **`craft-code`** — inherits craft's current version **0.4.0** (no bump invented for the rename). The
  `craft-code` marketplace entry, currently stale at `0.1.0`, is synced to `0.4.0`.
- **`craft-ops`** — bumped `0.10.0` → **0.11.0**, since its content (every `craft`/agent/namespace/
  `.craft.yml` reference) changes; its marketplace entry synced to `0.11.0`.
- A CHANGELOG entry in **both** plugins records the rename.

## Scope of this build

**Delivered:** the full `craft` → `craft-code` rename across both plugins — plugin manifests +
marketplace, the 9 agents (files + frontmatter + all refs), the `craft-code-conventions` skill (dir +
frontmatter + refs), `.craft.yml` → `.craft-code.yml`, the `craft:` → `craft-code:` namespace, and all
branding/prose in both plugins — with `craft-marketplace` and everything `craft-ops` protected. Version
+ CHANGELOG updates in both plugins. Folded into PR #3 (which already spans both plugins via the shared
marketplace).

**Non-goals:** no behavior change; no new skills/agents; the `craft-ops` suite's *name* is unchanged.

## Success criteria

- The code plugin installs as `craft-code@craft-marketplace`; `.claude-plugin/plugin.json` and the
  marketplace entry read `craft-code`.
- No `craft-<role>` agent name, `craft:` namespace ref, `project-conventions` ref, `.craft.yml` ref, or
  standalone "craft" suite-name remains anywhere in either plugin (outside gitignored `*-workspace/`
  eval scratch and historical CHANGELOG entries, which may keep their original text).
- **Nothing was corrupted:** no `craft-code-ops`, `craft-code-marketplace`, `craft-code-ops-conventions`,
  or `craft-code-code-*` anywhere; `craft-ops`, `craft-marketplace`, `.craft-ops.yml`, and the
  `craft-ops-*` agents are intact.
- `craft-code` at version 0.4.0 (marketplace synced), `craft-ops` at 0.11.0 (marketplace synced); both
  CHANGELOGs note the rename. The suite still reads coherently end to end.
