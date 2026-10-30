---
name: craft-code-conventions
description: "Use to record and read a project's concrete conventions in a .craft-code.yml file — the commands and settings the generic craft-code skills need but can't guess: how to run the unit and acceptance suites, start the app, build, lint, and format; which database and external fakes back the acceptance environment; the base branch and where plans/design notes live. Trigger when setting up craft-code in a new repo, when a skill or agent needs to run the suite/app/DB and the exact command isn't known, or when project conventions change. Reads .craft-code.yml at the repo root, and bootstraps one by discovering the project's tooling when it's absent. Not for writing tests, implementing features, or general how-to questions."
---

# Project Conventions

The craft-code skills are language- and framework-agnostic, so they can't know how this project runs its tests or starts its app. A committed `.craft-code.yml` at the repo root states those commands once, and every skill and agent reads it instead of guessing.

```yaml
stack: [typescript]
package_manager: pnpm
commands:
  install:      pnpm install
  build:        pnpm build
  test:         pnpm test          # fast inner-loop unit suite
  acceptance:   pnpm test:e2e      # outer-loop acceptance suite
  run:          pnpm dev
  lint:         pnpm lint
  format_check: pnpm format --check
acceptance_env:
  up:       docker compose -f docker-compose.acceptance.yml up -d
  down:     docker compose -f docker-compose.acceptance.yml down -v
  database: postgres:16
git:
  main_branch: main
paths:
  plans:  docs/craft-code/plans
  design: docs/craft-code/design
```

Every field, the `diagnostics` block, and per-language starters are in `references/schema.md`. Include only the keys the project uses.

## Reading it

Before running the unit or acceptance suite, the app, the build, the linter, or the acceptance environment, read `.craft-code.yml` and use the command it gives. If the key you need is missing, extend the file rather than guessing.

## Bootstrapping

When the file is absent: detect the stack and commands from `package.json` scripts, `*.csproj`/`*.sln`, `Cargo.toml`, `go.mod`, `Makefile`, `docker-compose*.yml`, and CI config; draft the file; ask the user only about what discovery couldn't settle (usually the acceptance command and environment); write and commit it.

## Keeping it true

When a command changes, update the file in the same change. A stale conventions file is worse than none, because skills trust it.
