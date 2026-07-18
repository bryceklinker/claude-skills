---
name: subagent-execution
description: "Use when executing the implementation, review, and verification phases of dev-workflow and you want to go faster without losing discipline — by dispatching work to subagents. Trigger whenever the plan has independent increments that could run in parallel, or when you want a fresh-eyes reviewer/verifier that didn't write the code. Covers what context each subagent needs, how to keep parallel work from colliding, and how to reconcile results."
---

# Subagent Execution — parallelize without breaking discipline

## Why this exists

Phases 4–7 (TDD, style, review, verify) are the slow part of the pipeline, and much of it is parallelizable — but only if you dispatch carefully. Done well, subagents make the pipeline both faster (independent increments run at once) and better (a reviewer who didn't write the code is less biased). Done carelessly, they collide on shared files and produce merge conflicts that quietly corrupt the discipline. This skill is the choreography that keeps the speed and drops the risk.

The core principle: **the orchestrator stays thin and coordinates; subagents do the deep work and report back.** The orchestrator holds the plan, dispatches, and reconciles. It does not itself get lost in the weeds of one increment.

## Two kinds of dispatch

### 1. Parallel implementers (speed)

For increments `planning` marked `[independent]` (disjoint files), dispatch each to its own implementer subagent running the full strict-TDD + code-style loop.

**The independence rule is absolute:** only dispatch increments in parallel if they touch disjoint files. Two subagents editing the same file is not parallelism — it's a merge conflict corrupting the ratchet. When in doubt, run sequentially.

Each implementer subagent gets its own **sibling worktree** off the work-item branch:

```bash
git worktree add ../<repo>-<slug>-inc<N> -b <branch>-inc<N> <work-item-branch>
```

It implements its increment there (red → green → refactor → commit), then the orchestrator merges the increment branch back into the work-item branch. Because the increments touch disjoint files, these merges are clean.

Dependent increments (`[depends: ...]`) run **sequentially** on the work-item branch, in an order where each one's test can be written against slices that already exist.

### 2. Fresh-eyes reviewer and verifier (quality)

After the increments are implemented and merged into the work-item branch, dispatch **separate** subagents for review and verification — agents that did not write the code:

- A `self-review` subagent reviews the full diff against acceptance criteria, `code-style`, and smells.
- A `verification` subagent actually runs the change and gathers evidence.

These can run in parallel with each other. The value here is independence of judgment: the implementer is primed to see what they intended; a fresh agent sees what's actually there.

## What every subagent needs in its prompt

A subagent starts cold. Give it enough to work without re-deriving context, and be explicit that the craft discipline still applies — a subagent does not get to skip TDD or style because it's "just one increment."

Include:
- **The relevant craft skill(s)** it must follow (e.g. `strict-tdd` + `code-style`, or `self-review`).
- **The exact increment or diff** it owns — increment number, behavior, acceptance criteria, and the files it may touch.
- **The worktree/branch** it should operate in.
- **Its precise deliverable** — e.g. "increment green and committed at green + after refactor" for an implementer; "a findings list keyed to file:line" for a reviewer.
- **The reminder that discipline holds:** no code before a red test, doubles only at boundaries, commit at green and after refactor. State it — subagents under a narrow task are the ones most tempted to cut the corner.

## Reconciling results

- **Implementers:** merge each increment branch back into the work-item branch. Because increments were disjoint, conflicts shouldn't occur; if one does, the plan's independence marking was wrong — treat it as a planning defect, not something to paper over with a manual merge.
- **Reviewer / verifier:** collect their findings. Any defect sends you back to `strict-tdd` — write a failing test that reproduces it, then fix. Never hand-patch a finding without a test.
- **Then advance** to `finish-work` only when review is clean and verification produced real evidence.

## When NOT to use subagents

Parallelism has overhead. For a single small increment, or a plan with no independent increments, dispatching costs more than it saves — just run the phases inline. The fresh-eyes review/verify split is still worth it even for small changes, because its payoff is judgment quality, not speed. Use `dispatching-parallel-agents` for the general mechanics of launching agents; this skill is specifically about keeping the craft discipline intact while you do.
