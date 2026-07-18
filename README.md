# craft

A disciplined software-development skill suite for Claude Code. Every feature and bugfix flows through one enforced pipeline — no fast lane, because the fast lane is where the bugs live.

## The pipeline

```
intake → planning → worktree-setup → strict-tdd + code-style → self-review → verification → finish-work
```

`dev-workflow` is the orchestrator that routes work through these gates and dispatches parallel work via `subagent-execution`.

## Installation (Claude Code)

`craft` is distributed as a Claude Code plugin via a marketplace hosted in this repo. Install it in two steps from the Claude Code prompt:

```
/plugin marketplace add bryceklinker/claude-skills
/plugin install craft@craft-marketplace
```

- The first command registers this repo's marketplace (`.claude-plugin/marketplace.json`).
- The second installs the `craft` plugin, which makes all ten skills available.

Verify the skills loaded with `/plugin` (they appear under the `craft` plugin) — `dev-workflow` triggers automatically the moment you start any feature, bugfix, or refactor.

**Updating** to the latest version later:

```
/plugin marketplace update craft-marketplace
/plugin install craft@craft-marketplace
```

To install from a local checkout instead (for development), point the marketplace at the repo path:

```
/plugin marketplace add /path/to/claude-skills
/plugin install craft@craft-marketplace
```

## Skills

| Skill | Role |
|-------|------|
| `dev-workflow` | Orchestrator. Entry point for all dev work; enforces the gates; dispatches subagents. |
| `intake` | Pin down intent, scope, and acceptance criteria. Reproduce bugs first. |
| `planning` | Slice work into small, independently testable increments; mark independence for parallelism. |
| `worktree-setup` | Isolate the work item in its own git worktree before any code. |
| `strict-tdd` | Classicist TDD: no code before red, one test at a time, red→green, commit at green + after refactor, real collaborators over doubles. |
| `code-style` | Immutability, no *what*-comments, results over exceptions, null objects, small units, clean/hexagonal architecture, CQRS. |
| `self-review` | Fresh-eyes review of the diff against criteria, style, and smells. |
| `verification` | Run it; evidence before any claim of done. |
| `finish-work` | Integrate (PR/merge), settle history, remove worktrees. |
| `subagent-execution` | Dispatch independent increments in parallel and run fresh-eyes review/verify, without breaking discipline. |

## Design philosophy

The suite encodes one opinionated methodology: Clean Code, Fowler's *Refactoring*, Meszaros' *xUnit Test Patterns*, ports-and-adapters, CQRS, and classicist (Detroit-school) TDD. The rules are strict on purpose — each removes a recurring source of bugs — but every rule is stated with the *why*, so the discipline is legible rather than dogmatic.

## Central rules worth knowing

- **No production code without a failing test first.** Watch it fail, watch it pass.
- **Use the real thing wherever it runs deterministically in-process** — including real third-party libraries. Doubles only at genuine external/non-deterministic seams (network, filesystem, clock, randomness).
- **Immutability by default.** The highest-priority style rule.
- **No comments except to explain *why* awkward code exists.**
- **CQRS by default** — commands and queries, never a growing `Service`/`Manager`. Commands may return the data the caller needs; queries never mutate.
- **Every feature/bug goes through the full pipeline** — including the "simple" ones.
