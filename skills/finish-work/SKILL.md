---
name: finish-work
description: "Use once a work item is implemented, adversarially reviewed, and verified — to integrate it and clean up: settle the commit history, open a PR or merge the work-item branch, and remove the worktree. Trigger whenever development work is done and needs to land. Presents the integration options rather than assuming one. Invoked by dev-workflow as phase 9."
---

# Finish Work

Only finish work that went through `strict-tdd`, `adversarial-review`, and `verification` with real evidence. If any is missing, go back.

## Settle the history

The branch already holds small behavior and refactor commits. Confirm they read coherently and the working tree is clean — nothing stray, no leftover scaffolding, notes, or probes. Reshape history only if the user wants it; don't silently squash away how the work was built.

## Integrate

Offer the options; the right one depends on the repo:

- **Open a pull request** — the default for anything others review or CI governs. The body says what changed and how it was verified, drawn from the verification evidence.
- **Merge directly** — when the workflow is trunk-based or solo and the user asked to merge.
- **Leave it on the branch** — when the user wants to take it from here.

## Clean up

Once integrated, remove the work-item worktree and any sibling increment worktrees (`git worktree remove ../<repo>-<slug>`), delete merged increment branches, and confirm with `git worktree list` that nothing stray remains.

## Exit condition

Integrated the way the user chose, history clean, worktrees removed.
