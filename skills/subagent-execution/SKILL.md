---
name: subagent-execution
description: "Use when executing the implementation, review, and verification phases of dev-workflow and you want to go faster without losing discipline — by dispatching work to subagents. Trigger whenever the plan has independent increments that could run in parallel, or when you want a fresh-eyes adversarial reviewer or verifier that didn't write the code. Covers what context each subagent needs, how to keep parallel work from colliding, and how to reconcile results."
---

# Subagent Execution

Subagents make the pipeline faster (independent increments at once) and better (a reviewer who didn't write the code). The orchestrator stays thin: it holds the plan, dispatches, checks what came back, and reconciles.

## The team

| Agent | Role | Follows | Access | Model |
|-------|------|---------|--------|-------|
| `craft-code-planner` | Criteria + independence-marked plan | `intake` + `planning` | read/write/bash | opus |
| `craft-code-architect` | Structure: boundaries, ports, operations, types | `architecture-design` | read-only | opus |
| `craft-code-designer` | UI: components + state inventory | `frontend-design` | read-only | opus |
| `craft-code-acceptance-tester` | Outer-loop tests + prod-like env | `acceptance-testing` | read/write/bash | opus |
| `craft-code-implementer` | One increment, own worktree | `strict-tdd` + `code-style` | read/write/bash | opus |
| `craft-code-reconciler` | Merges increment branches | git integration | read + bash | sonnet |
| `craft-code-reviewer` | Adversarial review of the diff | `adversarial-review` | read-only | opus |
| `craft-code-verifier` | Runs the change, gathers evidence | `verification` | read + bash | haiku |
| `craft-code-debugger` | Root cause of a defect | `systematic-debugging` | read/write/bash | opus |

The design, review, and verify agents lack write tools on purpose: they must report rather than quietly patch what they were sent to judge.

## Dispatch patterns

- **Design:** architect and designer touch disjoint concerns; run them in parallel and feed both notes to the planner.
- **Acceptance alongside implementation:** the acceptance tester writes the outer tests and environment (never production source) while implementers build increments; its suite is the shared red target.
- **Parallel implementers:** only for increments marked `[independent]` (disjoint files), each in its own sibling worktree — `git worktree add ../<repo>-<slug>-inc<N> -b <branch>-inc<N> <work-item-branch>`. Dependent increments run in order on the work-item branch. When in doubt, run sequentially.
- **Review and verification:** fresh agents, in parallel with each other, after increments are merged. Never dispatch review to a `fork`: it inherits your context — the bias the review exists to escape — and keeps write access. A fork asked for a "read-only survey" has been seen implementing and committing its own findings.

For one small increment, inline is cheaper than dispatch — but still send review and verification to fresh agents.

## What each prompt needs

A subagent starts cold. Give it: the skill(s) to follow; the exact increment or diff, with its criteria and the files it may touch; the worktree, branch, and the commit it's working against; its deliverable; and the blast radius it must stay inside — the named ephemeral stack it may tear down, targeted explicitly.

## Check what came back

- **A prompted constraint isn't a guarantee.** After any read-only dispatch, run `git -C <worktree> status --porcelain` and `git -C <worktree> log --oneline <base>..HEAD`. If it wrote or committed, discard that work and re-dispatch to a genuinely read-only agent; never fold unrequested edits in as if reviewed.
- **Stale checkouts produce confident wrong answers.** Confirm the worktree is at the commit you think before believing a diagnosis.
- **"Running" is not progress.** Look for new commits, files, or output; a delegate well past its normal duration gets checked, not waited on.
- **The orchestrator owns the evidence.** A subagent saying the suite is green is an input to verification, not a substitute for it.

## Reconcile

A `craft-code-reconciler` merges increment branches into the work-item branch; a conflict means the independence marking was wrong — re-mark those increments dependent and re-sequence. Review findings and verification defects go back to `strict-tdd` with a failing test; an unclear cause goes to `craft-code-debugger` first. Advance to `finish-work` only when review is clean and verification produced real evidence.
