---
name: frontend-design
description: "Use after intake and before planning for any user-facing change — to design the interface before building it: the screens and components, every state (empty, loading, error, success, partial), the interactions, accessibility, and how the UI talks to its data. Trigger whenever a feature or bugfix touches what a user sees or does — a new screen, a form, a flow, a component — anything with a visual or interaction surface. Produces a short design note (component breakdown + state inventory) that planning decomposes into increments. Skip it for backend-only or headless changes with no UI. Not for requirements (intake), sequencing (planning), API/contract structure (architecture-design), or writing the components."
---

# Frontend Design — design the interface before you build it

## Why this exists

The most common frontend defect isn't a bug in code — it's a state nobody designed for. The happy path gets built, ships, and then falls over on an empty list, a slow network, or a rejected input, because those states were never named. This phase names them up front, so planning can slice a UI that's complete by construction and strict-TDD has every state to drive a test toward.

It is a **thinking** phase. The output is a design note — a component breakdown and a state inventory — not components. No production code is written here; that waits for strict-TDD behind the pipeline's gate.

## What to decide

Work from the agreed acceptance criteria (from `intake`). Design only the surface this change actually introduces.

- **Component breakdown.** Decompose the UI into components with single responsibilities. What's a container (owns data/state) vs. a presentational component (renders props)? Keep them small and composable — the same "small units, one responsibility" discipline as the rest of the code.
- **State inventory — the load-bearing part.** For every view, enumerate every state and how it looks and behaves:
  - **Empty** — no data yet, or legitimately nothing to show (a real designed state, not a blank).
  - **Loading** — first load and subsequent refreshes; skeletons vs. spinners.
  - **Error** — the request failed, input was rejected, something went wrong; the message names what and what to do next.
  - **Partial / optimistic** — some data present, some pending; optimistic updates and their rollback.
  - **Success / populated** — the happy path, including its edge shapes (one item, many, very long text).
- **Interactions.** What the user can do, what each action triggers, what feedback confirms it. Validation timing (on blur, on submit), disabled/enabled affordances, destructive-action confirmation.
- **Accessibility.** Semantic structure, keyboard navigation and focus order, labels and roles, contrast, and that state changes are announced — designed in, not retrofitted.
- **Data binding.** Which components read which data, where fetching happens, and how UI states map to the underlying request states. Note the contract shapes the UI depends on (these tie to `architecture-design`'s ports/types for the same feature).

## Write it down

Produce a short design note. Save it where the work lives (e.g. `docs/craft/design/YYYY-MM-DD-<topic>-ui.md`) so `planning`, `strict-tdd`, and any subagent can read it. Include:

- The component tree (a simple nested list is enough).
- The state inventory per view — every state above, with its appearance and behavior.
- Key interactions and their feedback.
- Accessibility notes that aren't obvious from the structure.

Low-fidelity is the point — a labeled sketch or ASCII wireframe beats a polished mockup here. You're deciding *what states and pieces exist*, not pixel-perfecting them.

## Guardrails

- **Design every state, not just the happy one.** An undesigned error or empty state is a defect waiting for planning to miss it. If you named a data fetch, you owe it a loading and an error state.
- **Don't write components.** If you're reaching for JSX, stop — that's the strict-TDD phase.
- **Match the design to the criteria.** No screens the acceptance criteria don't call for; no speculative configurability.

## Exit condition

A written UI design note: component breakdown plus a complete state inventory per view, interactions, and accessibility notes — enough for `planning` to slice into thin, testable increments. Hand off to `planning`.
