---
name: worktree-setup
description: "Use after planning and before writing any implementation code — to isolate the work item in its own git worktree and branch. Trigger whenever you're about to start the strict-TDD phase, or whenever development work would otherwise happen directly on a main/shared branch. Keeps the main working tree clean and gives parallel subagents room to operate without colliding. Invoked by dev-workflow as phase 3."
---

# Worktree Setup — isolate the work before you build

## Why this exists

Implementation should never happen directly on the main tree. A worktree gives the work item its own checkout and branch, which buys three things: main stays clean and releasable; abandoned experiments are `rm -rf`, not a messy `git reset`; and parallel implementer subagents have somewhere to work without stepping on each other. This is the boundary that makes the rest of the pipeline safe to run fast.

## The model

- **One worktree per work item.** The feature or bugfix gets a single worktree on its own branch. This is where the strict-TDD phase runs.
- **Sibling worktrees for parallel increments.** When `planning` marked increments as independent and the orchestrator dispatches them concurrently, each implementer subagent gets its own sibling worktree branched off the work-item branch, then merged back. `subagent-execution` owns that choreography; this skill establishes the parent work-item worktree it branches from.

## Steps

1. **Confirm the base is clean and current.** Make sure the base branch (e.g. `main`) is up to date so the worktree starts from a known-good point.

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
