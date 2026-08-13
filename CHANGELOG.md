# Changelog

All notable changes to the `craft` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/). While pre-1.0, minor versions may
introduce new skills and agents; the pipeline's core discipline stays stable.

## Renamed to `craft-code` — 2026-08-13

The plugin was renamed from `craft` to `craft-code` to make the suite naming
self-describing alongside its sibling `craft-ops` — "craft" is really *crafting
code*, "craft-ops" is *crafting ops*. It now installs as
`/plugin install craft-code@craft-marketplace`; the `project-conventions` skill
is `craft-code-conventions`, the nine agents are `craft-code-*` (e.g.
`craft-code-architect`, `craft-code-reviewer`), the skill namespace is
`craft-code:`, and the per-repo config file is `.craft.yml` → `.craft-code.yml`.
This is a pure rename with no behavior change — version continuity is kept at
`0.4.0` (no bump), and the `craft-marketplace` umbrella name is unchanged.

## [0.4.0] — 2026-08-06

Closed discipline gaps surfaced by real retrospectives on branches built with the
pipeline (`haus#18`, `#12`, `#17`): the gates that held only "in spirit" but were
never structurally enforced. No new phases; the existing ones are made harder to
bypass and cheaper to honor.

### Added
- **`refactoring` skill** — a first-class home for behavior-preserving structural change. Encodes Fowler's discipline (small steps, tests green throughout, one technique at a time, refactor commits separately), a curated catalog of ~30 named techniques across the six Fowler/refactoring.guru categories with their safe mechanics (`references/techniques.md`), and a smell → technique map. It defers to `strict-tdd` for the green/commit ratchet and to `code-style` for the target style; it owns the named moves between them. Triggers on "refactor/clean up/restructure/simplify/de-duplicate this code" and on smell-finding — behavior-preserving only (a behavior change is still dev-workflow/strict-tdd).
- **Smell ↔ technique correlation.** Each entry in `code-style/references/smells.md` gained a **Resolve with →** pointer naming the technique that fixes it; `strict-tdd`'s refactor step and `self-review`'s findings now reach for named techniques rather than freehand cleanup. Finding a smell and choosing its fix are one step.
- **Trigger-eval sets** for the feedback/adjustment phrasings: `dev-workflow` and `strict-tdd` eval sets extended with casual "adjust/change/fix X" should-trigger cases and near-miss should-not-trigger cases (docs/config/comment/rename edits); new `refactoring` trigger-eval set. (Description-optimization loop is run out-of-session via `run_loop.py`.)

### Changed
- **`dev-workflow` / `strict-tdd` / `self-review` — feedback and adjustments are change requests.** The most common mid-session leak: a request phrased as feedback or "just adjust/change/fix X" went straight to a production edit with no failing test and no review. Added a `STOP-BEFORE-YOU-EDIT` rule (any edit to production code in direct response to a message needs a red test first, `self-review` after), framed around the insight that the failing test also *proves the adjustment was needed*. Extended `strict-tdd`'s trigger/red-flags and `self-review`'s trigger to catch the casual-adjustment and feedback-driven phrasings that previously slipped past both.
- **`dependency-maintenance` — escalate uncovered work, don't smuggle it.** Rewrote the escalation section to name the three cases a maintenance task pushes into the pipeline (seen in `#12`'s .NET 10 upgrade): an upgrade that forces API-adaptation code (→ `strict-tdd`), replacing a dropped dependency with first-party code (→ full `dev-workflow`, behavior parity as the criterion), and a latent bug the upgrade surfaces (→ `systematic-debugging` then `strict-tdd`, as its own commit — never patched inline in the bump).
- **`dev-workflow` — in-session follow-up lane.** The intake+plan HARD-GATE was binary, so well-scoped follow-ups during a live work item skipped it *every time* rather than take a path that didn't fit. Added an explicit lane, keyed to an observable predicate (active worktree this session + already-agreed criteria + a bounded, unambiguous ask): it collapses intake to one spoken line and the plan to the increment itself, while `strict-tdd`'s red test, worktree isolation, fresh-eyes `self-review`, and `verification` stay hard. A cold start — even "just quickly" — is never eligible and still starts at phase 1. Rationalization table updated so "too small" points to the lane instead of to a silent skip.
- **`subagent-execution` / `self-review` — review dispatches go to a fresh agent, never a `fork`.** A fork inherits the author's context (defeating fresh eyes) and carries write access with no barrier against fixing what it should only report — which happened, and initially read as unattributed external edits. Steered review/verify to the read-only `craft-reviewer`/`craft-verifier` with the reasoning stated.
- **`subagent-execution` — verify a prompted constraint actually held.** A "read-only"/"don't commit" brief is a request, not a boundary. Added a required post-return check (`git status --porcelain` / `git log` on the worktree) before a read-only agent's output is trusted, plus how to recover when it wrote anyway.
- **`strict-tdd` / `project-conventions` — scoped inner loop vs. full aggregate suite.** Running the whole multi-project unit suite on every change is slow enough that the loop stops being run. The inner loop now runs the narrowest command covering the code under change; the full `commands.test` runs before committing a green and before handoff. `schema.md` clarifies `commands.test` as the aggregate suite the inner loop scopes down from.
- **`worktree-setup` — verify `cwd` before destructive/environment commands.** A worktree isolates files, not the shell; a `docker compose down` from the main tree tore down production containers. Added a guardrail to confirm `pwd` (or scope commands with `-C` / `-f`) before any teardown or destructive command.

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

[0.4.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.4.0
[0.3.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.3.0
[0.2.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/bryceklinker/claude-skills/releases/tag/v0.1.0
