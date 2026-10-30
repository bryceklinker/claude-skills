---
name: frontend-design
description: "Use after intake and before planning for any user-facing change — to design the interface before building it: the screens and components, every state (empty, loading, error, success, partial), the interactions, accessibility, and how the UI talks to its data. Trigger whenever a feature or bugfix touches what a user sees or does — a new screen, a form, a flow, a component — anything with a visual or interaction surface. Produces a short design note (component breakdown + state inventory) that planning decomposes into increments. Skip it for backend-only or headless changes with no UI. Not for requirements (intake), sequencing (planning), API/contract structure (architecture-design), or writing the components."
---

# Frontend Design

The most common UI defect is a state nobody designed: the happy path ships and then falls over on an empty list, a slow network, or a rejected input. Name every state before building, so planning slices a UI that's complete by construction. The output is a note, not components.

## Decide

- **Components** — small, single-responsibility; which own data or state and which only render. Reuse existing components before adding new ones.
- **States, for every view** — empty, loading (first load and refresh), error (what went wrong and what to do next), partial or optimistic (and its rollback), and success including its edge shapes (one item, many, very long text). If a view fetches data, it owes a loading and an error state.
- **Interactions** — what each action triggers, the feedback that confirms it, validation timing, destructive-action confirmation.
- **Accessibility** — semantic structure, keyboard and focus order, labels and roles, contrast, announced state changes.
- **Data binding** — which components read which data, where fetching happens, how UI states map to request states, and the contract shapes the UI depends on (tied to `architecture-design` for the same feature).

Design only the surface the criteria call for — no extra screens, no speculative configurability. Low fidelity is the point: a labeled sketch or ASCII wireframe decides what exists.

## Write it down

Saved under `paths.design` (e.g. `docs/craft-code/design/YYYY-MM-DD-<topic>-ui.md`): the component tree, the state inventory per view, key interactions, and non-obvious accessibility notes.

## Exit condition

A UI design note with a complete state inventory, enough for `planning`. Hand off to `planning`.
