---
name: finish-work
description: "Use once a work item is implemented, self-reviewed, and verified — to integrate it and clean up: settle the commit history, open a PR or merge the work-item branch, and remove the worktree. Trigger whenever development work is done and needs to land. Presents the integration options rather than assuming one. Invoked by dev-workflow as phase 8."
---

# Finish Work — land it cleanly and clean up

## Why this exists

Work that's verified but not integrated is work that isn't done — and a worktree left behind is clutter that invites confusion later. This final phase gets the change into the main line the way the user wants it and leaves the workspace tidy. It's short, but skipping it is how half-merged branches and orphaned worktrees accumulate.

## Precondition

Only finish work that has passed through the whole pipeline: implemented via `strict-tdd`, reviewed via `self-review`, and verified via `verification` with real evidence. If any of those is missing, go back — don't merge on the strength of "it looks done."

## Settle the history

During `strict-tdd` you committed at green and after each refactor, so the branch already has a clean, honest sequence of small commits. Before integrating:

- Confirm the commits tell a coherent story — behavior and refactor commits in sensible order.
- Make sure the working tree is clean (everything intended is committed; nothing stray is left).
- Only reshape history if the user wants it — some prefer the granular real history, others a tidied series. Ask rather than assume; don't silently squash away the record of how the work was built.

## Choose how to integrate

Don't assume the integration path — present the options and let the user choose, since it depends on their workflow and the repo's conventions:

- **Open a pull request** from the work-item branch — the default for anything reviewed by others or governed by CI. Write a PR body that states what changed and how it was verified (draw on the evidence from `verification`).
- **Merge the branch** into the base directly — when the user's workflow is trunk-based or this is a solo/local repo and they've asked to merge.
- **Leave it on the branch** for the user to integrate themselves — when they want to take it from here.

If you're on the repo's default branch and about to commit new work, that's a signal you skipped `worktree-setup` — branch first.

## Clean up the worktree

Once the work is integrated (or the user has what they need):

- Remove the work-item worktree and any sibling increment worktrees created during parallel dispatch:
  ```bash
  git worktree remove ../<repo>-<slug>
  ```
- Delete merged increment branches; keep the work-item branch until its PR/merge is truly settled.
- Confirm no stray worktrees remain (`git worktree list`).

Leave the repository in the clean state you'd want to start the next work item from.

## Exit condition

The change is integrated the way the user chose (PR opened, merged, or handed off), the history is clean, and the worktrees are removed. The pipeline is complete.
