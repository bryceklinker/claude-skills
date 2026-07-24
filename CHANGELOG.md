# Changelog

All notable changes to the `craft` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/). While pre-1.0, minor versions may
introduce new skills and agents; the pipeline's core discipline stays stable.

## [0.3.0] — 2026-07-23

Reframed the core structural rule from "CQRS by default" to the underlying
intent it was really enforcing.

### Changed
- **Separate *what* from *how* (was: CQRS by default).** The rule is now the *input-data/handler separation*: a behavior's inputs are an immutable data object, and the handling lives in a separate, dedicated unit (one operation, one handler) — never a growing `Service`/`Manager`/`Utility`. The message + handler pair (Command/Query, CQRS) is presented as **one common shape and a fine default, not the only acceptable one**; other shapes (use-case/interactor with a request object, a pure function taking a parameter object) honor the same separation. Splitting reads from writes is demoted to a worthwhile *additional* discipline "when it fits" — where adopted, a query still must never mutate and a write handler may return what the caller needs. The `Service`/`Manager`/`Utility` grab-bag ban stays firm. Updated across `code-style` (`references/patterns.md`, `naming.md`, `smells.md`), `architecture-design`, `craft-architect`, `self-review`, `dev-workflow`, `PRINCIPLES.md` (principle 7), and `README.md`.

## [0.2.0] — 2026-07-23

A large expansion from the initial process skills into a full, portable suite:
front-of-pipeline design, an acceptance (outer-loop) layer, a debugging lane,
a maintenance lane, a nine-agent team, and a per-project convention layer.

### Added
- **Design phase (conditional).** `architecture-design` (domain boundary, ports/adapters, CQRS handlers, shared types) and `frontend-design` (component breakdown + full state inventory) run after intake, before planning.
- **Acceptance testing (outer loop).** `acceptance-testing` + `references/environment.md` — double-loop ATDD: a user-level test against a production-like deployment (real UI+API, real DB in a container, external deployed fakes — never code-level doubles), written up front and left failing while the inner `strict-tdd` loop drives it green.
- **`systematic-debugging`** + `references/techniques.md` — hypothesis-driven root-cause investigation (reproduce, narrow, confirm one hypothesis at a time); the front half of the pipeline's defect loop.
- **`dependency-maintenance`** — the lighter sibling lane for version/tooling updates `dev-workflow` excludes: one update per commit, changelog review, unit + acceptance suites as the safety net.
- **`project-conventions`** + `references/schema.md` — a committed `.craft.yml` per repo stating concrete commands (test, acceptance, run, build, lint, format), the acceptance environment (database, external fakes), the base branch, and doc paths, so the generic skills read them instead of guessing. Starter files for TS/JS, C#/.NET, Rust, Go.
- **Nine-agent team** — `craft-planner`, `craft-architect`, `craft-designer`, `craft-acceptance-tester`, `craft-implementer`, `craft-reconciler`, `craft-reviewer`, `craft-verifier`, `craft-debugger`. Design/review/verify agents are read-only; the reconciler flags a merge conflict between "independent" increments as a planning defect.
- **`PRINCIPLES.md`** — the canonical statement of the eleven principles the skills embody, referenced by the skills instead of restating the *why* in each.
- **Behavioral eval harness** (`tools/behavioral-evals/`) — a deterministic grader + scenarios that check a produced repo honored the discipline (test-first, no owned-code doubles, no non-null assertions, separate refactor commits, GWT names, green suite), as a regression guard when skills are edited. Validated to pass a disciplined repo and fail an undisciplined one.

### Changed
- **`code-style`** now bans the non-null assertion / null-forgiving operator (`x!` in TS/C#, force-unwraps) as a dedicated smell, and treats project `lint`/`format_check` as a mechanical pre-commit gate.
- **Model tiering** applied to agents: `opus` for code/judgment roles, `haiku` for the mechanical verifier, `sonnet` for the git-integration reconciler.
- **`dev-workflow`** pipeline expanded to nine phases (design + acceptance woven in) with the defect loop routed through `systematic-debugging`, and maintenance work routed out to `dependency-maintenance`.
- **`verification`** now runs the acceptance suite as its strongest done-evidence.
- Skills that run commands (`strict-tdd`, `verification`, `acceptance-testing`, `dependency-maintenance`, `worktree-setup`, `code-style`) and command-running agents now read `.craft.yml` rather than guessing.
- Trigger descriptions for all new skills empirically optimized (5/5 on held-out test splits).

## [0.1.0] — 2026-07-22

Initial release of the craft process suite.

### Added
- Core pipeline skills: `dev-workflow` (orchestrator), `intake`, `planning`, `worktree-setup`, `strict-tdd` (+ `references/testing-doubles.md`, `references/test-utilities.md`), `code-style` (+ naming/architecture/patterns/smells references), `self-review`, `verification`, `finish-work`, `subagent-execution`.
- Classicist TDD, clean/hexagonal architecture, CQRS, and a strict house style, with empirically optimized trigger descriptions.
- Marketplace configuration for installation from the GitHub repo.

[0.3.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.3.0
[0.2.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.1.0
