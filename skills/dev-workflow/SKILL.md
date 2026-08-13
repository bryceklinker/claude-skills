---
name: dev-workflow
description: "Use this to drive any change to application behavior or logic through a disciplined pipeline — features, enhancements, refactors, and bugfixes alike, including subtle runtime defects (race conditions, incorrect state, broken validation, wrong output) and changes that feel \"quick\" or \"simple.\" The moment the user asks you to build, add, implement, fix, correct, or change how the code behaves, run this BEFORE writing or editing production code; it enforces gates (intake → plan → worktree → TDD → review → verify → finish) so agreed intent and a plan exist first. Do NOT use it for maintenance that doesn't change product behavior — bumping dependency or tooling versions, editing config/lockfiles, formatting, or resolving config drift — nor for questions, explanations, naming, reviewing, or writing prose/notes about code."
---

# Dev Workflow — the disciplined pipeline

## What this is

Every change to production code — a feature, a bugfix, a refactor, a "tiny" tweak — flows through one pipeline. This skill is the conductor. It doesn't do the work itself; it decides which phase you're in, enforces the gate for that phase, and hands off to the specialist skill that does the work.

The reason for a single enforced path is simple: the failures that cost the most — building the wrong thing, untested code, style drift, regressions — all come from skipping a phase because it "felt unnecessary this time." The pipeline removes that decision. There is no lane that skips the failing test or the fresh-eyes review, because that's exactly where the bugs live — not even the in-session follow-up lane below, which collapses the *paperwork* of intake and planning for already-agreed work but keeps every test and review gate hard. The *why* behind this and every rule the phases enforce is stated canonically in the craft principles (`PRINCIPLES.md` at the plugin root).

**What this pipeline is *not* for:** work that changes no product behavior. Updating dependency or tooling versions, lockfiles, and config drift go through `dependency-maintenance`, a lighter sibling lane — not this pipeline. And when a defect's cause is unknown, `systematic-debugging` finds it first, then feeds the fix back into this pipeline. Both are covered below under "When phases send you backward" and the maintenance lane.

## The pipeline

```dot
digraph pipeline {
    rankdir=TB;
    intake      [label="1. intake\n(intent, scope, acceptance criteria)", shape=box];
    design      [label="2. design — as needed\n(architecture-design / frontend-design)", shape=box, style=dashed];
    planning    [label="3. planning\n(decompose into testable increments)", shape=box];
    worktree    [label="4. worktree-setup\n(isolate the work)", shape=box];
    accept      [label="5. acceptance-testing — as needed\n(outer loop: write user-level test, watch it fail)", shape=box, style=dashed];
    tdd         [label="6. strict-tdd + code-style\n(inner loop: drive increments green)", shape=box];
    review      [label="7. self-review\n(fresh eyes vs criteria + style)", shape=box];
    verify      [label="8. verification\n(run it, gather evidence)", shape=box];
    finish      [label="9. finish-work\n(integrate, PR, clean up)", shape=box];

    intake -> design -> planning -> worktree -> accept -> tdd;
    tdd -> accept [label="re-run outer test → green", style=dashed];
    accept -> review [label="feature proven"];
    review -> verify -> finish;
    verify -> tdd [label="defects found", style=dashed];
    review -> tdd [label="issues found", style=dashed];
}
```

Each phase has a dedicated skill: `intake`, `architecture-design` / `frontend-design`, `planning`, `worktree-setup`, `acceptance-testing`, `strict-tdd`, `code-style`, `self-review`, `verification`, `finish-work`. Dispatch and parallelism are handled by `subagent-execution`.

**Design (phase 2) is conditional.** Run it when the change adds new structure or a user-facing surface: `architecture-design` when there are new moving parts (a module, integration, persistence/transport concern, non-trivial structural refactor), `frontend-design` when a user sees or does something new. Both can run — a full-stack feature needs each. Skip design entirely for a change that fits cleanly into existing, well-shaped structure with no UI. When in doubt, a two-line design note ("fits existing checkout feature, one new operation and its handler") is cheap; a wrong structure discovered mid-TDD is not.

**Acceptance testing (phase 5) is the outer loop, and conditional.** For a user-facing feature or a change to a user flow, write a user-level acceptance test up front — against a production-like deployment (real UI + API, real database in a container, external deployed fakes, never code-level doubles) — and watch it fail. It stays red while the inner `strict-tdd` increments (phase 6) are built, and its going green is what proves the feature works end to end. Skip it for a pure internal refactor already covered by the existing acceptance suite. This is double-loop TDD: the outer acceptance test brackets the inner unit cycle.

## The gate you must honor

<HARD-GATE>
Do NOT write or edit production code until BOTH of these exist:
1. Agreed acceptance criteria (from `intake`)
2. A written plan of testable increments (from `planning`)

If you are asked to "just quickly" change code and these do not exist, stop and start at phase 1. "Simple" changes are exactly where unexamined assumptions cause the most rework.
</HARD-GATE>

This is not bureaucracy for its own sake. Intake catches "we built the wrong thing." Planning catches "we painted ourselves into a corner." Skipping them doesn't save time; it moves the cost later, where it's larger.

## The in-session follow-up lane

The gate asks for agreed criteria and a written plan. On the **first** request of a work item — a cold start — neither exists yet, so you build them (phases 1–3). But once a work item is *live* — you're already in its worktree, its criteria were agreed, its plan is being executed — those two conditions already hold. A well-scoped change the user directs mid-session ("also make the health check reflect the real connection state," "convert the simulator to MVC while you're in there") is another increment on that live plan, not a new work item. Forcing a fresh intake document and plan file for each such follow-up is the ceremony that gets skipped anyway — and a gate that's skipped every single time was never really a gate. Give the follow-up an honest, lighter route instead of a rationalization to lie about.

So a follow-up **collapses** the front of the pipeline; it does not skip it.

<FOLLOW-UP-LANE trigger — ALL three must hold>
1. An active work item exists **this session**: you are in its worktree and its acceptance criteria were already agreed.
2. The ask is **user-directed and well-scoped** — a specific, bounded change, not "figure out X" or "clean up the module."
3. It raises **no new ambiguity** — no boundary question, no unclear requirement, nothing you'd need to check back on. If it does, that ambiguity *is* an intake question: take the full pipeline.
</FOLLOW-UP-LANE>

When all three hold, the front of the pipeline collapses to:
- **Intake → one spoken line.** State the change and its done-condition out loud ("the health publisher should report the coordinator's real connection state, not a hardcoded `Healthy`"). That sentence is the criterion.
- **Criterion → the failing test.** You don't write a criteria doc; you write the test that encodes the done-condition, and `strict-tdd`'s iron law makes it real. The red test *is* the acceptance criterion, executable.
- **Plan → the increment itself.** One increment needs no plan file.

Everything downstream stays hard — a follow-up earns no exemption from the parts that actually catch bugs:
- **Reuse the work item's worktree.** Never edit source on the base branch (`worktree-setup`).
- **`strict-tdd`'s iron law holds absolutely.** A failing test first, watched red, or you are not in this lane — you're just writing untested code and calling it a follow-up.
- **Fresh-eyes `self-review` and `verification` still run** before the follow-up is called done. "It was small" is not a reason to skip review; small changes break things too.

Miss any one trigger condition and you are on the full pipeline. A **cold-start** request — even one phrased "just quickly," even one that sounds tiny — has no active work item and no agreed criteria, so it is never eligible: it starts at phase 1, where the "just quickly" framing is exactly the tell that an unexamined assumption is about to cost you. **The lane is for continuing agreed work, never for starting it.**

## Feedback and adjustments are change requests too

The pipeline is easy to honor for a request that *announces itself* as a feature. It gets silently skipped for the request that doesn't: a piece of feedback, a correction, an "adjust this," a "no, do it this way," a "that's not handling the empty case." These feel like conversation, not development — so the reflex is to open the editor and change the production code on the spot. That reflex is the single most common way the discipline is lost mid-session, and it is the thing this section exists to stop.

**A request to adjust, change, correct, tweak, or fix how code behaves is a change to behavior** — whatever verb it wore, however small it sounds, however casually it was phrased. It enters the pipeline like any other change: the in-session follow-up lane if all three of its triggers hold, the full pipeline otherwise. Either way it is **test-first**, and it is **reviewed** before it's called done.

<STOP-BEFORE-YOU-EDIT>
The moment your next action would be an edit to production code *in direct response to a message* — a feature ask, a bug report, a review comment, or a one-line "just change X" — stop and ask: is there a failing test demanding this change? If not, you are about to write untested code. Route the request through `strict-tdd` (capture the adjustment as a red test first), then `self-review` before you call it done. Editing first and testing after is not this pipeline, no matter who asked or how small it is.
</STOP-BEFORE-YOU-EDIT>

Writing the test first here does more than guard against regressions — it *verifies the adjustment was actually needed.* A change you can't first express as a failing test is a change you haven't yet shown the code needs; more than once, "just adjust this" turns out to already work, or to need something different from what was asked, and the red test is what surfaces that **before** you've touched production code. That is the check the straight-to-editor reflex skips.

## How to run it

At the start of any development request, **state the current phase out loud** and confirm its precondition before acting. For example: *"This is a new feature. No acceptance criteria exist yet — starting at phase 1, intake."* This single habit is what makes the gate real instead of decorative.

On a repo craft hasn't run in before, make sure a `.craft.yml` exists first — it tells every downstream phase how *this* project runs its tests, app, and acceptance environment. If it's missing, use `project-conventions` to bootstrap one before the phases that need those commands (TDD, acceptance, verification).

Then, for each phase:

1. Announce which phase you're entering and why.
2. Invoke the phase's skill and follow it.
3. Confirm the phase's exit condition is met before advancing.

Track the work item's progress with a task list — one task per phase — so the state is always visible and a resumed session knows exactly where it left off.

### Phase map

| Phase | Skill | Precondition (gate) | Exit condition |
|-------|-------|---------------------|----------------|
| 1 | `intake` | A change is requested | Acceptance criteria agreed; bugs have a reproduction |
| 2 | `architecture-design` / `frontend-design` *(as needed)* | Criteria exist; change adds structure or UI | Design note: boundaries/ports/handlers and/or components/states |
| 3 | `planning` | Criteria (and design, if any) exist | Ordered increments written, independence marked |
| 4 | `worktree-setup` | Plan exists | Isolated worktree + branch created |
| 5 | `acceptance-testing` *(as needed — outer loop)* | User-facing feature or user-flow change | User-level acceptance test written, watched failing against a production-like deployment |
| 6 | `strict-tdd` + `code-style` | Inside the worktree | Every increment green; committed at green + after refactor; outer acceptance test now green |
| 7 | `self-review` | Increments implemented | Diff reviewed against criteria, style, smells |
| 8 | `verification` | Review passed | The change actually ran (incl. the acceptance suite); evidence captured |
| 9 | `finish-work` | Verified | Integrated (PR/merge), worktree cleaned up |

## Speeding it up with subagents

Phases 5–8 are the slow part, and much of it parallelizes. The orchestrator's job is to dispatch aggressively **without breaking the discipline**:

- **The front of the pipeline runs as focused agents.** Dispatch a `craft-code-planner` for intake + planning; when the change adds structure, a `craft-code-architect` for `architecture-design`; when it's user-facing, a `craft-code-designer` for `frontend-design`. Architecture and UI design touch disjoint concerns, so for a full-stack feature they can run in parallel, then feed the planner.
- **The outer acceptance loop runs alongside the inner work.** For a user-facing feature, dispatch a `craft-code-acceptance-tester` to write the user-level acceptance tests up front (left failing) and stand up the production-like environment. It works in parallel with the implementers — they drive the inner unit loop while its outer test is the shared red target — and it confirms green once the increments land.
- **Independent increments run in parallel.** If `planning` marked two increments as touching disjoint files, dispatch each to its own `craft-code-implementer` (each in a sibling worktree, each running the full strict-TDD + code-style loop). Increments with dependencies run in order. When they finish, a `craft-code-reconciler` merges the increment branches back into the work-item branch — clean by construction, or a flagged planning defect if two collide.
- **Review and verification run as fresh-eyes agents.** Hand the diff to a `craft-code-reviewer` and a `craft-code-verifier` that did *not* write the code. A reviewer without implementation bias catches more — this is a quality win, not only a speed one.
- **Unknown-cause defects go to the debugger first.** When `self-review` or `verification` finds a defect whose cause isn't obvious, dispatch a `craft-code-debugger` to find the root cause (reproduce, narrow, confirm) before the fix returns to a `craft-code-implementer` to capture as a failing test.

The `craft` plugin ships nine agents — `craft-code-planner`, `craft-code-architect`, `craft-code-designer`, `craft-code-acceptance-tester`, `craft-code-implementer`, `craft-code-reconciler`, `craft-code-reviewer`, `craft-code-verifier`, `craft-code-debugger` — covering the pipeline end to end. `subagent-execution` covers exactly what each needs and how to reconcile their output.

See `subagent-execution` for exactly how to parcel the work, what context each subagent needs, and how to reconcile their results. The rule that never bends: parallelism is allowed only where the work is genuinely independent. Two subagents editing the same file is not speed, it's a merge conflict waiting to corrupt the discipline.

## When phases send you backward

The dashed arrows are normal, not failures. If `self-review` or `verification` finds a defect, you return to `strict-tdd`: write a failing test that reproduces the defect, then fix it. You never patch a defect without a test that would have caught it — that's how the pipeline stays a ratchet that only tightens.

When the defect's cause isn't obvious — a failure you can't yet explain, a flaky test, a regression, a race — don't guess your way back through `strict-tdd`. Use `systematic-debugging` first to find the root cause (reproduce, narrow, confirm one hypothesis at a time), then hand the confirmed cause to `strict-tdd` to capture as a failing test and fix. Debugging finds the cause; the pipeline captures and fixes it.

## Rationalizations to reject

| Thought | Reality |
|---------|---------|
| "This change is too small for the pipeline" | Size was never the axis — *cold start vs. follow-up* is. A cold change still earns its gate (criteria + plan); a follow-up on live, agreed work takes the in-session follow-up lane above — lighter, but still test-first and reviewed. "Skip it entirely" is not one of the options. |
| "This is a follow-up, so I can skip the test / the review too" | The follow-up lane collapses only intake and planning. `strict-tdd`'s red test and fresh-eyes `self-review` never collapse — they're the part that catches the bug, not the paperwork. |
| "The user gave feedback / told me to adjust the code — that's not a 'feature,' just do it" | A change to how code behaves is a change, whatever the verb. Adjust / tweak / fix / correct / "do it this way" all enter the pipeline, test-first and reviewed. The casual phrasing is camouflage, not an exemption. |
| "It's a tiny adjustment, there's nothing to test" | Then the test is tiny too. And if you genuinely can't write one that fails without the change, you've just learned the change may not be needed — that's the test doing its job before you edit, not busywork. |
| "I already know what to build, skip intake" | Then intake takes 30 seconds. Writing it down is what surfaces the disagreement you didn't know you had. |
| "Let me just prototype in the main tree" | Exploration is fine — in a worktree, thrown away after. Prototyping in place is how prototypes ship untested. |
| "One worktree is overkill for a one-liner" | The worktree costs seconds and keeps main clean. The one-liner that broke main also looked harmless. |
| "Subagents are slower to set up than just doing it" | For a single increment, maybe. For independent increments or for a fresh-eyes review, they're both faster and better. |
