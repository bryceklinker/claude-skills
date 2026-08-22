---
name: refactoring
description: "Use when asked to refactor, clean up, restructure, tidy, simplify, de-duplicate, extract, or otherwise improve the internal structure of existing code WITHOUT changing what it does — and when finding code smells and deciding how to resolve them. Trigger on 'refactor this', 'clean up this class', 'this method is too long', 'reduce the duplication here', 'extract this', 'simplify this conditional', 'find the smells and fix them'. Behavior-preserving only: if the change alters observable behavior (a new feature, a bugfix, different output), that is dev-workflow/strict-tdd, not this. Provides the named refactoring techniques, their safe mechanics, and the map from each smell to the technique that resolves it. It supplies the moves, never a licence to skip the pipeline: a restructure spanning several files, or one needing a characterization net built first, still runs inside dev-workflow with its worktree, commits, review and verification — this skill is what you reach for within it."

---

# Refactoring — change the structure, not the behavior

## What this is

Refactoring is **a change to the internal structure of code that does not change its observable behavior** (Fowler). You do it to make code easier to understand and cheaper to change — before adding a feature to make room for it, and after to clarify what you just built. It is not a rewrite, not a cleanup pass that "also fixes a few things," and not an excuse to touch behavior. The instant a change alters what the code *does*, it has stopped being a refactoring and belongs in `strict-tdd` as a new increment with its own failing test.

This skill owns three things: the **discipline** (how to refactor safely), the **catalog** of named techniques and their mechanics (`references/techniques.md`), and the **map from smell to technique** (below and in `code-style/references/smells.md`). It leans on two neighbors and does not duplicate them:

- **`strict-tdd`** owns the green/commit ratchet. Refactoring runs *inside* its REFACTOR step, or as its own behavior-preserving increment — either way, the tests stay green throughout and the refactor commits separately from any behavior change.
- **`code-style`** owns the target: the house style and the smell catalog. Smells are the *triggers* to refactor; the style is the *destination*. This skill supplies the *moves* between them.

**One technique is a move; a restructure is a work item.** Resolving a single smell in front of you — extract this function, hide this delegate — is this skill on its own. But "clean up this class," a decomposition spanning several files, or anything that needs a characterization net built first is *the pipeline's* work: it earns a worktree, increments, fresh-eyes review, and verification like any other change. Enter through `dev-workflow` and let this skill supply the moves inside it. Running a multi-step restructure freehand is how a session ends with beautiful structure, no commits, and no review.


## The discipline

<HARD-GATE>
Refactoring changes structure, never behavior. The test suite is green before you start and green after every step. If a test goes red, your last step changed behavior — revert it; that's not a refactoring.

If the task actually needs new behavior, stop: it is not a refactoring. Give it its own failing test via `strict-tdd`. Never bundle "restructure" and "change what it does" into one move or one commit.
</HARD-GATE>

The safety of refactoring comes entirely from **small, behavior-preserving steps run against green tests**. The rules:

1. **Green before you begin.** Refactoring without tests is just editing and hoping. If the code you're about to restructure has no test covering its behavior, that gap is the first thing to fix — add the characterization test (watch it pass on current behavior) so you have a net, *then* refactor. In the craft-code pipeline this is rarely an issue: strict-tdd already left the behavior covered. **Characterization tests are tests, so they carry the test rules:** named Given/When/Then (`code-style/references/naming.md` — a `describe`/`it` block is fine as surface syntax, but the two titles must still read as Given/When/Then when joined), and real collaborators rather than doubles of owned code. Writing them outside `strict-tdd` doesn't exempt them; it just means nothing else is going to catch it.

2. **One technique at a time.** Pick the single named technique that resolves the smell in front of you (the map below). Apply *its* mechanics — not a freehand rewrite. Named techniques have known-safe steps for a reason.
3. **Small steps, tests after each.** Every mechanical step is small enough that the suite can run between them and prove behavior held. Run the fast scoped suite (see `strict-tdd`) after each step, not just at the end. A refactor that only gets tested at the end is a rewrite wearing a refactor's name.
4. **Commit the refactor on its own — and commit as you go, not at the end.** A refactoring is its own commit — `refactor: extract shippingCost from checkout`, never riding inside a behavior commit. Each technique that lands green is a commit; the characterization net is its own commit before any restructuring starts. This keeps every step independently reviewable and revertible.

<HARD-GATE>
Do not finish a refactoring session with the work uncommitted. Green-and-uncommitted is not a result: it can't be reviewed, can't be reverted step-by-step, and hides whether behavior held at each move or only at the end. If you reach the end and `git status` is dirty, the ratchet never engaged — that's the defect, however good the final structure looks.
</HARD-GATE>

5. **Refactor test code too.** Tests decay like any code; the same techniques apply to them (see `strict-tdd`'s references/test-utilities.md).

## How to use it

When you're asked to refactor, or `self-review` / the strict-tdd refactor step turns up a smell:

1. **Name the smell.** Match what you see to an entry in `code-style/references/smells.md` (long method, duplication, feature envy, sprawling conditional, data class, …).
2. **Look up the resolving technique** in the smell → technique map below, then read its mechanics in `references/techniques.md`.
3. **Apply the technique's mechanics** in small steps, running tests after each.
4. **Commit** the refactor separately, green.

If several smells stack up in one place, resolve them one technique at a time, committing between — not in one big restructuring.

## Smell → technique map

The quick index; each smell's entry in `code-style/references/smells.md` carries the same pointer, and each technique's mechanics live in `references/techniques.md`.

| Smell | Resolve with |
|-------|--------------|
| Long method | Extract Function; if it's tangled around local state, Replace Function with Command / Extract Variable first |
| Large class (`Service`/`Manager`/`Utility` grab-bag) | Extract Class along responsibility lines; split into operations (input object + handler) |
| Duplicate code | Extract Function and call it from both sites; Pull Up Method when the copies sit in siblings |
| Long parameter list | Introduce Parameter Object; Preserve Whole Object; Replace Parameter with Query |
| Data clumps (same fields traveling together) | Introduce Parameter Object; Extract Class for the clump |
| Sprawling / nested conditional | Decompose Conditional; Replace Nested Conditional with Guard Clauses |
| Duplicated switch / type-code branching | Replace Conditional with Polymorphism; Replace Type Code with Subclasses/Strategy |
| Law of Demeter train-wreck | Hide Delegate; Move Function onto the owner of the data (tell, don't ask) |
| Data class (fields + getters, behavior elsewhere) | Move Function onto the data; Encapsulate |
| Feature envy (method uses another object's data more than its own) | Move Function to the envied object; Extract Function then move the piece |
| Comments explaining *what* | Extract Function with an intention-revealing name; Rename |
| Magic literal | Replace Magic Literal with a named constant |
| Long loop body | Extract Function for the per-item work; Replace Loop with Pipeline (map/filter/reduce) |
| Mutable state / reassigned temp | Split Variable; Replace Temp with Query; Extract to a fully-formed immutable value |
| Nulls / non-null assertions | Introduce Null Object (a `code-style` fix); narrow with a guard, or return a Result |

Full mechanics for each technique: `references/techniques.md`.

## Common mistakes

- **Refactoring and changing behavior in one step.** The most common and most dangerous. If the suite goes red, you crossed the line — revert and split the two apart.
- **A freehand "rewrite" called a refactor.** Big restructurings done in one leap, tested only at the end, are how behavior silently changes. Use a named technique's small steps.
- **Refactoring untested code with no net.** Add the characterization test first; otherwise you have no way to know behavior held.
- **Turning a `Manager` into a smaller `Manager`.** Decompose into operations; don't just shrink the grab-bag (see `code-style`).

## Exit condition

The smell is gone, the code moves toward the house style, every step kept the suite green, and the refactor landed as its own commit separate from any behavior change — with a clean `git status`, since uncommitted work means the ratchet never engaged.
 If the work turned out to need new behavior, that part left this skill and went through `strict-tdd` with its own failing test.
