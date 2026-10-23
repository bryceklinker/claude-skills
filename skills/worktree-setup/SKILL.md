---
name: worktree-setup
description: "Set up an isolated git worktree and branch for a work item before implementation begins. Use whenever someone wants a dedicated workspace, sandbox, or separate branch to build a feature or bugfix in — especially phrased as \"off main,\" \"so I don't dirty/mess up my current tree,\" \"isolate this work,\" \"spin up a workspace for this,\" or \"get a worktree going.\" Also triggers when about to enter strict-TDD or write implementation code that would otherwise land on a main/shared branch, and gives parallel subagents room to work without colliding. Do NOT use for merging or tearing down worktrees, general questions about how worktrees/detached HEAD work, planning/breaking work into increments, or writing the actual tests and code. Invoked by dev-workflow as phase 4."
---

# Worktree Setup

Implementation never happens on the main tree. A worktree keeps main releasable, makes an abandoned experiment a directory delete, and gives parallel implementers somewhere to work without colliding.

## Steps

1. Update the base branch (`git.main_branch` in `.craft-code.yml`; worktree location from `git.worktree_dir`).
2. Create the worktree — native tooling if your environment has it, otherwise:
   ```bash
   git worktree add ../<repo>-<slug> -b <branch> <base-branch>
   ```
   Name the branch for the work item (`feat/promo-codes`, `fix/empty-email-accepted`); keep worktrees as siblings of the repo, not nested in it.
3. Move into it and confirm the branch and a clean status.
4. Make sure the plan is available inside it.

One worktree per work item; reuse it if it already exists. Parallel increments get sibling worktrees off the work-item branch (`subagent-execution`).

## Check where you're standing before anything destructive

A worktree isolates files, not your shell. `docker compose down`, `rm -rf`, `git clean -fdx`, or `git reset --hard` run from the wrong directory hit the wrong target — a `docker compose down` from the main repo has taken down running production containers. Before any command that destroys state, confirm `pwd` is this worktree, or scope it explicitly (`git -C <worktree>`, `docker compose -f <this worktree's file>`).

## Exit condition

You're in a clean worktree on the work item's branch, with the plan available. Hand off to `strict-tdd`, directly or via `subagent-execution`.
