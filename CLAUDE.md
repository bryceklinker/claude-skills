# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **content repository**, not an application: it holds two independently-versioned Claude Code plugins made of Markdown skills and agents. There is no build step, no package manager, and no compiled artifact — the deliverable *is* the prose, and its quality bar is behavioral (does the skill fire on the right requests, and does an agent following it actually behave?).

- **`craft-code`** (repo root) — a disciplined software-development suite. One enforced pipeline: `intake → design → planning → worktree-setup → [acceptance-testing wrapping strict-tdd + code-style] → self-review → verification → finish-work`. `dev-workflow` is the orchestrator.
- **`craft-ops/`** (subdirectory) — a sibling DevOps suite. A *library*, not a pipeline: no orchestrator, reach for the skill whose domain is in front of you.

Both ship from one marketplace (`.claude-plugin/marketplace.json`) but install and version separately.

## Layout

```
skills/<name>/SKILL.md          craft-code skills; references/*.md for depth
agents/craft-code-*.md          craft-code subagents
craft-ops/skills/, agents/      the same two shapes, for the ops plugin
PRINCIPLES.md                   craft-code's canonical "why" (craft-ops has its own)
tools/behavioral-evals/         discipline regression guard
tools/hook-tests/               tests for .githooks/commit-msg
docs/superpowers/specs|plans/   design docs and implementation plans, dated
```

Gitignored working areas: `*-workspace/` (trigger-description optimizer, benchmark iterations) and `evals/`.

## Commands

```sh
git config core.hooksPath .githooks          # once per clone: enable the commit-msg hook
tools/hook-tests/commit-msg-test.sh          # test the commit-msg hook

# behavioral evals: grade a produced repo against a scenario's assertions
PY=/opt/homebrew/bin/python3.14 tools/behavioral-evals/run.sh <runs-dir>
/opt/homebrew/bin/python3.14 tools/behavioral-evals/grade.py \
  --repo <path> --scenario tools/behavioral-evals/scenarios/<id>.json --test-cmd "node --test"

# preview generated release notes (CI pins git cliff 2.13.1)
git-cliff --config cliff.toml --tag-pattern 'craft-code-v.*' --exclude-path 'craft-ops/**' --unreleased --tag craft-code-v0.5.0
```

Test a skill change live by installing from the local checkout: `/plugin marketplace add /path/to/claude-skills` then `/plugin install craft-code@craft-marketplace`.

Producing repos for behavioral evals is the expensive, non-deterministic half and is deliberately manual — drive the pipeline over a scenario's `prompt` in a throwaway repo, place the result at `<runs-dir>/<scenario-id>/repo`, then grade.

## Authoring conventions

**Frontmatter is the interface.** A `SKILL.md` carries `name` + `description`; an agent adds `tools` and `model`. The `description` is a *trigger specification*, not a summary — it states when to use the skill, and explicitly when NOT to (the negative clauses are what stop overlapping skills from stealing each other's requests). Descriptions are tuned against eval sets by the trigger optimizer in `craft-code-workspace/`; treat rewrites as a behavioral change, not cosmetics.

**Progressive disclosure.** SKILL.md bodies stay short (most under ~80 lines; `dev-workflow` at ~150 is the outlier). Depth goes in `references/*.md` and is linked, not inlined.

**Cite the principles; don't restate them.** `PRINCIPLES.md` is the single source of the *why*. Skills restate only the slice they need to stand alone and point at "the craft-code principles (`PRINCIPLES.md` at the plugin root)." When you change a rule, change it there first.

**Portability is a hard rule.** Skills never hardcode project commands. A repo's concrete commands live in a committed `.craft-code.yml` (schema: `skills/craft-code-conventions/references/schema.md`) or `.craft-ops.yml`, and skills read them. If you find yourself writing `npm test` into a skill, put it in the conventions layer instead.

**`craft-ops` must not depend on `craft-code`.** It has its own `PRINCIPLES.md` (which cites craft-code's) and its own conventions file, and never reads `.craft-code.yml`. Ops skills that defer the production loop to craft-code must degrade gracefully when it isn't installed — fall back to running the discipline directly rather than failing.

**Read-only agents stay read-only.** Design, review, and verify agents (`craft-code-architect`, `craft-code-designer`, `craft-code-reviewer`) produce notes or reports and deliberately lack write tools, so they can't quietly patch what they were meant to critique.

## Commits and releases

Conventional commits: `<type>(<scope>)<!>: <description>`, types `feat|fix|docs|refactor|perf|test|chore|build|ci|revert`. Scope is conventionally `craft-code` or `craft-ops`, but **release attribution is by file path, not scope**: commits touching `craft-ops/**` go to the craft-ops notes, everything else (including root `README.md`, `docs/`, `tools/`, `.github/`) to craft-code. A subject that doesn't parse is silently dropped from the release notes.

Cutting a release (see `docs/releasing.md` for the full procedure and failure modes):

1. One commit bumping three things in lockstep — the plugin's `.claude-plugin/plugin.json` `version`, its entry in `.claude-plugin/marketplace.json`, and a hand-written `CHANGELOG.md` entry.
2. Merge to `main` with a **merge commit or rebase — never a squash** (notes are generated per commit; a squash collapses the release body to one bullet).
3. Dispatch the **Release** workflow from the Actions tab with the ref left on `main`.

`CHANGELOG.md` files are hand-written editorial prose and are never generated — git cliff's output goes only to the GitHub Release body.

## Working in this repo

Changes here are prose, so `craft-code`'s own pipeline (`dev-workflow`, `strict-tdd`) does not apply — there is no failing test to write for a skill edit. The equivalent discipline is: state the *why* in `PRINCIPLES.md`, keep the trigger description honest about its boundaries, and run the behavioral evals after editing a skill to confirm you didn't quietly loosen the discipline it encodes.
