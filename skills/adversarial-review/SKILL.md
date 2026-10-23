---
name: adversarial-review
description: "Use after implementing increments and before verification or merge — to review the full diff adversarially: assume it is wrong and try to prove it. Challenges the assumptions the change rests on (including how the criteria were read), hunts implementation gaps (unmet criteria, untried edge cases, unhandled failure paths, detached work nobody owns), hunts test gaps (plausible bugs no test would catch, tests that can't fail), and flags complexity that could be deleted with every criterion still met. Trigger whenever work is about to be called done — a feature, a bugfix, and just as much a small in-session adjustment or feedback change, which skip review most often. Best run by a fresh, read-only agent that did NOT write the code. Invoked by dev-workflow. Not for writing the fixes, nor for running the app to gather evidence (that is verification)."
---

# Adversarial Review

The author sees what they meant to write. This review assumes the diff is wrong and sets out to show how: the assumption nobody checked, the input nobody tried, the test that would still pass with the bug in place, the code that didn't need to exist. Its output is evidence of failure, or a credible account of the attacks that failed. A clean result on a non-trivial diff with nothing tried is a review that wasn't done.

Run it as a fresh, read-only agent (`craft-code-reviewer`) that didn't write the code — never a fork, which inherits the author's view and can edit. The reviewer reports; it doesn't patch. Inputs: the diff (`git diff <base>...<head>`), the acceptance criteria, and the plan.

## The passes

**1. Challenge the assumptions.** List what the change takes for granted: input shape, size, encoding, and emptiness; ordering and timing; concurrency; configuration and environment; what each dependency actually does; and how the criteria were interpreted. For each one correctness depends on, find what supports it — a test, the dependency's source, a guard. An unsupported load-bearing assumption is a finding. Also ask whether the change solves the problem the criterion states, or a nearby easier one.

**2. Hunt implementation gaps.** Map each criterion to its code and test, then try to break it: boundary values, empty or missing input, duplicates, very large or malformed input, concurrent callers, failure partway through, retries and re-entrancy, the error path of every I/O call, cleanup on failure. For each call site that starts work without awaiting it, ask *if this throws, who finds out?* (`code-style/references/failure-modes.md`). Behavior with no criterion is scope creep or an unwritten criterion; say which. Then check durability: a guard, retry, or delay around a mechanism nobody explained; a third patch to the same lines; a guarantee quietly weakened to get a green; a lock or disable that could block the operation it protects; a change that makes failures harder to see.

**3. Hunt test gaps.** For each behavior, name a plausible bug — an off-by-one, an inverted condition, a dropped `await`, the wrong field — and check whether any test would fail. If none would, that's a gap; state the bug. Also flag tests that can't fail (no real assertion, asserting a mock, a tautology), tests that assert implementation instead of outcome, doubles of things that could run for real, missing failure-path tests, and tests committed after the code they cover.

**4. Challenge the complexity.** What could be deleted with every criterion still met? Interfaces with one implementation, layers that only forward, options and parameters nobody uses, defensive checks for impossible states, single-use helpers, redundant tests, dead code, a new dependency where the platform already suffices. Fewer moving parts with the same guarantees is a finding, not a matter of taste (`PRINCIPLES.md` principle 1).

**5. Check the style.** Against `code-style` and its `references/smells.md`; for each smell, name the resolving technique from `refactoring`.

## Reporting

Rank findings most severe first. Each one has:

- the `file:line` anchor and which pass found it;
- severity — **must-fix** (unmet criterion, real gap, violated rule) or **suggestion**;
- a concrete failure scenario — *given X, when Y, it does Z instead of W* — or, for complexity, what to delete and why nothing breaks;
- whether it is **confirmed** (traced or run) or **plausible**;
- a suggested direction, not an implementation.

Close with the attacks that held up: the assumptions you checked and the edge cases you tried that the code survived. That's what makes "no findings" credible.

## What happens to findings

A behavior finding goes back through `strict-tdd`: a failing test first, then the fix. A test gap on correct code gets its missing test, proven able to fail by breaking the code the way the finding describes, watching it go red, and reverting. Complexity and style findings covered by tests are fixed in a refactor step, staying green. Nothing is hand-patched.

## Exit condition

Every must-fix finding is resolved through the loop, and a re-review of the changed areas finds no new ones. Hand off to `verification`.
