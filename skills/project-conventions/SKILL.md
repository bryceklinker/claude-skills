---
name: project-conventions
description: "Use to record and read a project's concrete conventions in a .craft.yml file — the commands and settings the generic craft skills need but can't guess: how to run the unit and acceptance suites, start the app, build, lint, and format; which database and external fakes back the acceptance environment; the base branch and where plans/design notes live. Trigger when setting up craft in a new repo, when a skill or agent needs to run the suite/app/DB and the exact command isn't known, or when project conventions change. Reads .craft.yml at the repo root, and bootstraps one by discovering the project's tooling when it's absent. Not for writing tests, implementing features, or general how-to questions."
---

# Project Conventions — teach the pipeline this project's commands

## Why this exists

The craft skills are deliberately framework- and language-agnostic — that's what lets the same discipline run on a TypeScript app, a .NET service, and a Rust CLI. The tradeoff is that a generic skill can't know *how this project* runs its tests, starts its app, or stands up its database. Left to guess, every skill improvises ("maybe `npm test`?") and gets it wrong on half your repos.

`.craft.yml` closes that gap. A project states its concrete commands and conventions **once**, at the repo root, and every skill and agent reads them instead of guessing. This is what makes the suite portable: the discipline is universal; the commands are per-project, and they live in one file.

## The file

A single `.craft.yml` at the repository root, **committed** so the whole team and every agent share it:

```yaml
stack: [typescript]
package_manager: pnpm
commands:
  install:      pnpm install
  build:        pnpm build
  test:         pnpm test          # the fast inner-loop unit suite
  acceptance:   pnpm test:e2e      # the outer-loop acceptance suite
  run:          pnpm dev           # start the app
  lint:         pnpm lint
  format_check: pnpm format --check
acceptance_env:
  up:       docker compose -f docker-compose.acceptance.yml up -d
  down:     docker compose -f docker-compose.acceptance.yml down -v
  database: postgres:16
git:
  main_branch: main
paths:
  plans:  docs/craft/plans
  design: docs/craft/design
```

The full annotated schema, every field, and per-language starter files (TS/JS, C#/.NET, Rust, Go) are in `references/schema.md`.

## Reading it — the rule for every skill and agent

<HARD-GATE>
Before running the test suite, the acceptance suite, the app, the build, the linter, or standing up the acceptance database, **read `.craft.yml` and use the command it specifies.** Do not guess a command when the file answers it, and do not invent your own when the project has stated one. If the file is missing the key you need, bootstrap or extend it (below) rather than guessing silently.
</HARD-GATE>

This is what turns "run the suite" in a dozen skills from a hopeful guess into a correct, project-specific action.

## Bootstrapping a new repo

When craft first runs in a project and there's no `.craft.yml`, create one by **discovering** the tooling, then confirming with the user:

1. **Detect the stack and commands.** Read `package.json` scripts, `*.csproj`/`*.sln`, `Cargo.toml`, `go.mod`, `Makefile`, `docker-compose*.yml`, and CI config. These usually reveal the test, build, lint, and run commands directly.
2. **Draft `.craft.yml`** from what you found, filling the schema in `references/schema.md`.
3. **Confirm the gaps.** Ask the user only about what discovery couldn't settle — most often the acceptance command and environment (which DB, which external fakes), since those are the newest concept. Don't interrogate what the repo already told you.
4. **Write and commit it.** Now every subsequent phase reads it.

## Keeping it honest

`.craft.yml` is only useful while it's true. When a command changes — the test runner moves, the acceptance env gains a fake, the app's start command changes — update the file in the same change. A stale convention file is worse than none, because skills will trust it. Treat it like any other project contract: it changes with the project.

## How the rest of the suite uses it

| Skill / agent | Reads |
|---------------|-------|
| `strict-tdd` / `craft-implementer` | `commands.test` to run the inner-loop suite |
| `acceptance-testing` / `craft-acceptance-tester` | `commands.acceptance`, `acceptance_env.*` for the prod-like deployment |
| `verification` / `craft-verifier` | `commands.test` + `commands.acceptance` + `commands.run` for evidence |
| `dependency-maintenance` | `commands.test` + `commands.acceptance` after each update; `commands.lint`/`build` |
| `code-style` | `commands.lint` + `commands.format_check` as the pre-commit gate |
| `worktree-setup` / `craft-reconciler` | `git.main_branch`, `git.worktree_dir` |
| `planning` / `architecture-design` / `frontend-design` | `paths.plans`, `paths.design` for where to write |

## Exit condition

A `.craft.yml` exists at the repo root, is committed, and accurately states the commands and conventions the pipeline needs. Any skill or agent that must run something reads it first.
