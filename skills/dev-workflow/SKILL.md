---
name: dev-workflow
description: "Use this to drive any change to application behavior or logic through a disciplined pipeline — features, enhancements, refactors, and bugfixes alike, including subtle runtime defects (race conditions, incorrect state, broken validation, wrong output) and changes that feel \"quick\" or \"simple.\" The moment the user asks you to build, add, implement, fix, correct, adjust, or change how the code behaves, run this BEFORE writing or editing production code; it enforces gates (intake → plan → worktree → TDD → adversarial review → verify → finish) so agreed intent and a plan exist first. Do NOT use it for maintenance that doesn't change product behavior — bumping dependency or tooling versions, editing config/lockfiles, formatting, or resolving config drift — nor for questions, explanations, naming, reviewing, or writing prose/notes about code."
---

# Dev Workflow

Every change to production behavior goes through one pipeline. This skill decides which phase you're in, holds its gate, and hands off to the skill that does the work. The reasons behind every rule are in `PRINCIPLES.md` at the plugin root; principle 1 — use less to achieve more — applies to every phase, including this one: produce only the artifacts a phase actually needs.

| # | Phase | Skill | Enter when | Done when |
|---|-------|-------|------------|-----------|
| 1 | Intake | `intake` | A change is requested | Criteria agreed; a bug is reproduced |
| 2 | Design *(as needed)* | `architecture-design` / `frontend-design` | New structure or a user-facing surface | A short design note exists |
| 3 | Planning | `planning` | Criteria (and design) exist | Ordered increments, independence marked |
| 4 | Worktree | `worktree-setup` | A plan exists | Isolated worktree and branch |
| 5 | Acceptance *(as needed)* | `acceptance-testing` | User-facing feature or flow change | Outer test written and seen failing |
| 6 | Build | `strict-tdd` + `code-style` | Inside the worktree | Every increment green and committed; outer test green |
| 7 | Review | `adversarial-review` | Increments implemented | No open must-fix findings |
| 8 | Verify | `verification` | Review clean | Evidence for each criterion, observed this session |
| 9 | Finish | `finish-work` | Verified | Integrated; worktree removed |

Skip design when the change fits existing structure with no new UI. Skip a new acceptance test for an internal refactor the existing acceptance suite already covers. Review findings and verification defects send you back to phase 6 with a failing test; a defect whose cause isn't known goes to `systematic-debugging` first. Version and tooling bumps belong to `dependency-maintenance`, not this pipeline.

## The gate

Don't write or edit production code until agreed acceptance criteria and a written plan exist. A "just quickly" request with neither starts at phase 1 — the framing is the tell that an unexamined assumption is about to cost rework.

At the start of any development request, say which phase you're in and whether its precondition holds ("New feature, no criteria yet — starting at intake"). On a repo with no `.craft-code.yml`, bootstrap one with `craft-code-conventions` before the phases that run commands. Track progress with one task per phase.

## The in-session follow-up lane

Once a work item is live, a follow-up the user directs is another increment on that plan, not a new work item. Take this lane only when **all three** hold:

1. A work item is active **this session** — you're in its worktree and its criteria were already agreed.
2. The ask is user-directed and well-scoped — a specific, bounded change.
3. It raises no new ambiguity. If it does, that ambiguity is an intake question: take the full pipeline.

Then intake collapses to one spoken sentence stating the change and its done-condition, the plan collapses to the increment itself, and the failing test is the criterion. Nothing else collapses: reuse the work item's worktree, write the failing test first, and run `adversarial-review` and `verification` before calling it done. A cold-start request is never eligible, however small it sounds — the lane continues agreed work; it never starts it.

## Feedback is a change request

"Adjust this," "no, do it this way," "that doesn't handle the empty case" — a request to change how code behaves is a behavior change whatever verb it wears. Before an edit to production code made in direct response to a message, there is a failing test demanding it. The red test also checks the adjustment is needed: more than once, "just adjust this" turns out to already work or to need something different, and the test surfaces that before you touch the code. Then review before calling it done.

## Subagents

Dispatch the front of the pipeline to `craft-code-planner` (with `craft-code-architect` and `craft-code-designer` in parallel when both design kinds are needed), the outer loop to `craft-code-acceptance-tester`, independent increments to parallel `craft-code-implementer`s merged by `craft-code-reconciler`, review to `craft-code-reviewer`, verification to `craft-code-verifier`, and unknown causes to `craft-code-debugger`. For a single small increment, run the phases inline — but review and verification still go to fresh agents, because their value is independent judgment. `subagent-execution` covers prompts, isolation, and reconciliation.

## When a fix is a choice

If a fix can be made at the symptom, the cause, or the structure that allowed it, lay out the options and recommend the most durable one that fits the real constraints (`intake/references/fix-options.md`). A stopgap chosen anyway ships with a *why*-comment naming what would let it be removed. If the failure was hard to see, the missing signal ships with the fix.
