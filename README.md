# craft

A disciplined software-development skill suite for Claude Code. Every feature and bugfix flows through one enforced pipeline — no fast lane, because the fast lane is where the bugs live.

## The pipeline

```
intake → design (architecture / frontend, as needed) → planning → worktree-setup → [ acceptance-testing (outer) wrapping strict-tdd + code-style (inner) ] → self-review → verification → finish-work
```

`dev-workflow` is the orchestrator that routes work through these gates and dispatches parallel work via `subagent-execution`.

## Installation (Claude Code)

`craft` is distributed as a Claude Code plugin via a marketplace hosted in this repo. Install it in two steps from the Claude Code prompt:

```
/plugin marketplace add bryceklinker/claude-skills
/plugin install craft@craft-marketplace
```

- The first command registers this repo's marketplace (`.claude-plugin/marketplace.json`).
- The second installs the `craft` plugin, which makes all thirteen skills and seven agents available.

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
| `architecture-design` | Decide the shape before slicing: domain boundary, ports/adapters, CQRS handlers, shared types. As needed. |
| `frontend-design` | Design the UI before building: component breakdown and a complete state inventory. As needed. |
| `planning` | Slice work into small, independently testable increments; mark independence for parallelism. |
| `worktree-setup` | Isolate the work item in its own git worktree before any code. |
| `acceptance-testing` | Outer-loop ATDD: user-level test against a production-like deployment (real UI+API, real DB, external fakes), written up front and left failing. As needed. |
| `strict-tdd` | Classicist TDD: no code before red, one test at a time, red→green, commit at green + after refactor, real collaborators over doubles. |
| `code-style` | Immutability, no *what*-comments, results over exceptions, null objects, small units, clean/hexagonal architecture, CQRS. |
| `self-review` | Fresh-eyes review of the diff against criteria, style, and smells. |
| `verification` | Run it; evidence before any claim of done. |
| `finish-work` | Integrate (PR/merge), settle history, remove worktrees. |
| `subagent-execution` | Dispatch independent increments in parallel and run fresh-eyes review/verify, without breaking discipline. |

## Agent team

The plugin ships seven purpose-built subagents so `dev-workflow` can run the pipeline end to end — and much of it in parallel — without loosening the discipline. The orchestrator (main thread) dispatches to them by name:

| Agent | Role | Follows | Access |
|-------|------|---------|--------|
| `craft-planner` | Criteria + ordered, independence-marked plan | `intake` + `planning` | read / write / bash |
| `craft-architect` | Structure: boundaries, ports, CQRS handlers, types | `architecture-design` | read-only — design note, no code |
| `craft-designer` | UI: component breakdown + full state inventory | `frontend-design` | read-only — design note, no code |
| `craft-acceptance-tester` | Outer-loop user-level tests + production-like env | `acceptance-testing` | read / write / bash |
| `craft-implementer` | Builds one increment in its own sibling worktree | `strict-tdd` + `code-style` | read / write / bash |
| `craft-reviewer` | Fresh-eyes review of a finished diff | `self-review` | read-only — reports, never fixes |
| `craft-verifier` | Runs the change and captures evidence | `verification` | read + bash, no edit |

**Front of the pipeline:** `craft-architect` and `craft-designer` address disjoint concerns, so a full-stack feature dispatches both in parallel; their notes feed `craft-planner`. **Implementation:** a `craft-acceptance-tester` writes the outer, user-level test up front (left failing) and runs it in parallel with the `craft-implementer`s, who each drive one increment's inner unit loop in its own worktree — the outer test is the shared red target that goes green when the increments land. **Back of the pipeline:** a `craft-reviewer` and `craft-verifier` give the merged diff fresh eyes. The design, review, and verify agents are deliberately read-only so they *produce notes or report* rather than quietly write or patch code — the thinking-before-building and fresh-eyes independence the pipeline depends on. See `subagent-execution` for the dispatch and reconciliation choreography.

## Design philosophy

The suite encodes one opinionated methodology: Clean Code, Fowler's *Refactoring*, Meszaros' *xUnit Test Patterns*, ports-and-adapters, CQRS, and classicist (Detroit-school) TDD. The rules are strict on purpose — each removes a recurring source of bugs — but every rule is stated with the *why*, so the discipline is legible rather than dogmatic.

## Central rules worth knowing

- **No production code without a failing test first.** Watch it fail, watch it pass.
- **Two loops, two levels of substitution.** Inner (`strict-tdd`): real in-process code, doubles only at non-deterministic seams *in code*. Outer (`acceptance-testing`): a production-like deployment with a real database and, where a real service can't be used, an *external deployed fake* — never a code-level double inside the running app.
- **Use the real thing wherever it runs deterministically in-process** — including real third-party libraries. Doubles only at genuine external/non-deterministic seams (network, filesystem, clock, randomness).
- **Immutability by default.** The highest-priority style rule.
- **No comments except to explain *why* awkward code exists.**
- **CQRS by default** — commands and queries, never a growing `Service`/`Manager`. Commands may return the data the caller needs; queries never mutate.
- **Every feature/bug goes through the full pipeline** — including the "simple" ones.
