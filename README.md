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
- The second installs the `craft` plugin, which makes all sixteen skills and nine agents available.

Verify the skills loaded with `/plugin` (they appear under the `craft` plugin) — `dev-workflow` triggers automatically the moment you start any feature, bugfix, or refactor.

**Updating** to the latest version later:

```
/plugin marketplace update craft-marketplace
/plugin install craft@craft-marketplace
```

See [`CHANGELOG.md`](CHANGELOG.md) for what changed between versions.

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
| `architecture-design` | Decide the shape before slicing: domain boundary, ports/adapters, operations (inputs + handlers), shared types. As needed. |
| `frontend-design` | Design the UI before building: component breakdown and a complete state inventory. As needed. |
| `planning` | Slice work into small, independently testable increments; mark independence for parallelism. |
| `worktree-setup` | Isolate the work item in its own git worktree before any code. |
| `acceptance-testing` | Outer-loop ATDD: user-level test against a production-like deployment (real UI+API, real DB, external fakes), written up front and left failing. As needed. |
| `strict-tdd` | Classicist TDD: no code before red, one test at a time, red→green, commit at green + after refactor, real collaborators over doubles. |
| `code-style` | Immutability, no *what*-comments, results over exceptions, null objects, small units, clean/hexagonal architecture, inputs-as-data separated from handlers. |
| `self-review` | Fresh-eyes review of the diff against criteria, style, and smells. |
| `verification` | Run it; evidence before any claim of done. |
| `finish-work` | Integrate (PR/merge), settle history, remove worktrees. |
| `systematic-debugging` | Find a defect's root cause by disciplined investigation — reproduce, narrow, confirm one hypothesis at a time — before changing anything. The front half of the defect loop. |
| `dependency-maintenance` | The sibling lane for version/tooling updates dev-workflow excludes: one update per commit, read the changelog, run unit + acceptance suites. |
| `subagent-execution` | Dispatch independent increments in parallel and run fresh-eyes review/verify, without breaking discipline. |
| `project-conventions` | Record this project's concrete commands (test, acceptance, run, lint, DB) in a committed `.craft.yml` so the generic skills read them instead of guessing. The portability layer. |

## Agent team

The plugin ships nine purpose-built subagents so `dev-workflow` can run the pipeline end to end — and much of it in parallel — without loosening the discipline. The orchestrator (main thread) dispatches to them by name:

| Agent | Role | Follows | Access | Model |
|-------|------|---------|--------|-------|
| `craft-planner` | Criteria + ordered, independence-marked plan | `intake` + `planning` | read / write / bash | opus |
| `craft-architect` | Structure: boundaries, ports, operations (inputs + handlers), types | `architecture-design` | read-only — design note, no code | opus |
| `craft-designer` | UI: component breakdown + full state inventory | `frontend-design` | read-only — design note, no code | opus |
| `craft-acceptance-tester` | Outer-loop user-level tests + production-like env | `acceptance-testing` | read / write / bash | opus |
| `craft-implementer` | Builds one increment in its own sibling worktree | `strict-tdd` + `code-style` | read / write / bash | opus |
| `craft-reconciler` | Merges parallel increment branches back | *(git integration)* | read + bash, no edit | sonnet |
| `craft-reviewer` | Fresh-eyes review of a finished diff | `self-review` | read-only — reports, never fixes | opus |
| `craft-verifier` | Runs the change and captures evidence | `verification` | read + bash, no edit | haiku |
| `craft-debugger` | Root-cause investigation of a defect | `systematic-debugging` | read / write / bash | opus |

**Front of the pipeline:** `craft-architect` and `craft-designer` address disjoint concerns, so a full-stack feature dispatches both in parallel; their notes feed `craft-planner`. **Implementation:** a `craft-acceptance-tester` writes the outer, user-level test up front (left failing) and runs it in parallel with the `craft-implementer`s, who each drive one increment's inner unit loop in its own worktree — the outer test is the shared red target that goes green when the increments land; a `craft-reconciler` then merges their branches back. **Back of the pipeline:** a `craft-reviewer` and `craft-verifier` give the merged diff fresh eyes, and a `craft-debugger` finds the root cause of any defect whose cause isn't obvious before the fix returns to an implementer. The design, review, and verify agents are deliberately read-only so they *produce notes or report* rather than quietly write or patch code.

**Model tiering is conservative:** every agent that writes code or makes design/decomposition/review judgments runs on `opus`; only the mechanical evidence-gatherer (`craft-verifier`) drops to `haiku`, and the git-integration role (`craft-reconciler`) to `sonnet` — quality is kept where decisions are made, cost trimmed only where the work is mechanical. See `subagent-execution` for the dispatch and reconciliation choreography.

## Design philosophy

The suite encodes one opinionated methodology: Clean Code, Fowler's *Refactoring*, Meszaros' *xUnit Test Patterns*, ports-and-adapters, CQRS, and classicist (Detroit-school) TDD. The rules are strict on purpose — each removes a recurring source of bugs — but every rule is stated with the *why*, so the discipline is legible rather than dogmatic. The full rationale lives in [`PRINCIPLES.md`](PRINCIPLES.md) — the canonical statement of the eleven principles the skills embody.

## Maintaining the suite

- [`PRINCIPLES.md`](PRINCIPLES.md) — the canonical *why* behind every rule; skills cite it instead of restating it.
- [`tools/behavioral-evals/`](tools/behavioral-evals/) — a regression guard that mechanically checks a produced repo actually honored the discipline (test-first, no owned-code doubles, no non-null assertions, separate refactor commits, Given/When/Then names, green suite). Run it after editing a skill to confirm you didn't loosen what it encodes.
- The trigger-description optimizer and its eval sets live under `craft-workspace/` (gitignored) — local tooling used to tune when each skill fires.

## Central rules worth knowing

- **No production code without a failing test first.** Watch it fail, watch it pass.
- **Two loops, two levels of substitution.** Inner (`strict-tdd`): real in-process code, doubles only at non-deterministic seams *in code*. Outer (`acceptance-testing`): a production-like deployment with a real database and, where a real service can't be used, an *external deployed fake* — never a code-level double inside the running app.
- **Use the real thing wherever it runs deterministically in-process** — including real third-party libraries. Doubles only at genuine external/non-deterministic seams (network, filesystem, clock, randomness).
- **Immutability by default.** The highest-priority style rule.
- **No comments except to explain *why* awkward code exists.**
- **Separate *what* from *how*** — a behavior's inputs are an immutable data object; the handling lives in a separate, dedicated unit (one operation, one handler), never a growing `Service`/`Manager`/`Utility`. A message + handler pair (CQRS) is one common shape and a fine default, but the input-data/handler separation is the rule, not the Command/Query names. Where you split reads from writes, a query never mutates and a write handler may return the data the caller needs.
- **Every feature/bug goes through the full pipeline** — including the "simple" ones.
- **Portable by design.** The skills never hardcode commands; a committed `.craft.yml` per repo states the concrete ones (test, acceptance, run, lint, DB, base branch) and every skill/agent reads it. The discipline is universal; the commands are per-project.
