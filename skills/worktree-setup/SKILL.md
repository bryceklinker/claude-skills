---
name: worktree-setup
description: "Set up an isolated git worktree and branch for a work item before implementation begins. Use whenever someone wants a dedicated workspace, sandbox, or separate branch to build a feature or bugfix in — especially phrased as \"off main,\" \"so I don't dirty/mess up my current tree,\" \"isolate this work,\" \"spin up a workspace for this,\" or \"get a worktree going.\" Also triggers when about to enter strict-TDD or write implementation code that would otherwise land on a main/shared branch, and gives parallel subagents room to work without colliding. Do NOT use for merging or tearing down worktrees, general questions about how worktrees/detached HEAD work, planning/breaking work into increments, or writing the actual tests and code. Invoked by dev-workflow as phase 3."
---

# Worktree Setup — isolate the work before you build

## Why this exists

Implementation should never happen directly on the main tree. A worktree gives the work item its own checkout and branch, which buys three things: main stays clean and releasable; abandoned experiments are `rm -rf`, not a messy `git reset`; and parallel implementer subagents have somewhere to work without stepping on each other. This is the boundary that makes the rest of the pipeline safe to run fast.

## The model

- **One worktree per work item.** The feature or bugfix gets a single worktree on its own branch. This is where the strict-TDD phase runs.
- **Sibling worktrees for parallel increments.** When `planning` marked increments as independent and the orchestrator dispatches them concurrently, each implementer subagent gets its own sibling worktree branched off the work-item branch, then merged back. `subagent-execution` owns that choreography; this skill establishes the parent work-item worktree it branches from.

## Steps

1. **Confirm the base is clean and current.** Make sure the base branch is up to date so the worktree starts from a known-good point. Use `git.main_branch` and `git.worktree_dir` from `.craft.yml` (see `project-conventions`) for the base branch and where sibling worktrees live, rather than assuming `main` and `../`.

2. **Create the worktree and branch.** Prefer the native worktree tooling if your environment provides it; otherwise use git directly:

   ```bash
   git worktree add ../<repo>-<slug> -b <branch-name> <base-branch>
   ```

   Name the branch for the work item (e.g. `feat/promo-codes`, `fix/empty-email-accepted`) and the branch name for the slug. Keep worktrees as siblings of the repo, not nested inside it.

3. **Move into the worktree** and confirm you're on the new branch with a clean status before any code is written.

4. **Carry the plan in.** Ensure the plan document from `planning` is available inside the worktree (commit it, or it already lives in-repo) so the implementation phase and any subagents can read it.

## Guardrails

- If a worktree for this work item already exists, reuse it — don't spawn duplicates.
- Never start `strict-tdd` while sitting on the base branch. If you catch yourself about to edit source on `main`, stop and create the worktree first.
- Keep the worktree focused on one work item. A second unrelated change gets its own worktree.

## Exit condition

You are inside a clean worktree on a dedicated branch for this work item, with the plan available. Hand off to `strict-tdd` (directly, or via `subagent-execution` for parallel increments).
