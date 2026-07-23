# .craft.yml — full schema and starter files

`.craft.yml` lives at the repository root and is committed. Every field is optional, but the more the project states, the less any skill has to guess. Unknown keys are ignored, so you can extend it for project-specific needs.

## Table of contents
- The full annotated schema
- Field reference
- Starter: TypeScript / JavaScript
- Starter: C# / .NET
- Starter: Rust
- Starter: Go
- Notes on the acceptance environment

## The full annotated schema

```yaml
# What languages/runtimes the project uses. Informs which conventions apply.
stack: [typescript, csharp]          # any of: typescript, javascript, csharp, rust, go, ...

# The primary package/build tool. Used to phrase commands and pick defaults.
package_manager: pnpm                # pnpm | npm | yarn | bun | dotnet | cargo | go | make

commands:
  install:      pnpm install         # install dependencies
  build:        pnpm build           # produce the build artifact
  test:         pnpm test            # the fast INNER-LOOP unit suite (strict-tdd, verification)
  acceptance:   pnpm test:e2e        # the OUTER-LOOP acceptance suite (acceptance-testing)
  run:          pnpm dev             # start the app for manual/e2e exercise
  lint:         pnpm lint            # static analysis / style enforcement
  format_check: pnpm format --check  # verify formatting without writing (pre-commit gate)
  format_write: pnpm format          # apply formatting
  typecheck:    pnpm typecheck       # optional, when separate from build

acceptance_env:                      # how acceptance-testing stands up a production-like deployment
  up:       docker compose -f docker-compose.acceptance.yml up -d
  down:     docker compose -f docker-compose.acceptance.yml down -v
  database: postgres:16              # the REAL engine used in the acceptance env (never a substitute)
  ui_driver: playwright              # browser automation for UI acceptance: playwright | cypress | selenium
  base_url: http://localhost:8080    # where the deployed app is reachable in the acceptance env
  fakes:                             # EXTERNAL deployed fakes (never code-level doubles)
    - name:  payments
      image: wiremock/wiremock       # a standalone service the app calls over the same protocol
    - name:  email
      image: mailhog/mailhog

git:
  main_branch:   main                # the base branch worktrees branch from
  worktree_dir:  ../                 # where sibling worktrees are created (as repo siblings)
  branch_prefix:
    feature: feat/
    bugfix:  fix/

paths:
  plans:  docs/craft/plans           # where planning writes its increment plans
  design: docs/craft/design          # where architecture-design / frontend-design write notes
```

## Field reference

- **`commands.test` vs `commands.acceptance`** — the single most important distinction. `test` is the fast, in-process unit suite the inner `strict-tdd` loop and `verification` run constantly. `acceptance` is the slow, out-of-process outer suite that boots the real deployment. Keeping them as separate commands is what lets the pipeline run the fast one often and the slow one deliberately.
- **`commands.run`** — how `verification` starts the app to drive a flow by hand when a criterion needs it.
- **`commands.format_check`** — used as a pre-commit gate by `code-style`; the `_check` variant verifies without modifying so it can fail CI.
- **`acceptance_env.database`** — the real engine (e.g. `postgres:16`), matching production. Acceptance tests never substitute this with an in-memory or different database.
- **`acceptance_env.fakes`** — external, deployed fakes only: standalone services the app reaches over the wire exactly as it would the real one. This is where the "never a code-level double in the running app" rule is made concrete.
- **`git.main_branch` / `worktree_dir`** — consumed by `worktree-setup` and `craft-reconciler` so worktrees branch from and merge back to the right place.
- **`paths.*`** — so a resumed session or a subagent finds the plan and design notes where the project keeps them.

## Starter: TypeScript / JavaScript

```yaml
stack: [typescript]
package_manager: pnpm
commands:
  install:      pnpm install
  build:        pnpm build
  test:         pnpm test
  acceptance:   pnpm test:e2e
  run:          pnpm dev
  lint:         pnpm lint
  format_check: pnpm prettier --check .
  typecheck:    pnpm tsc --noEmit
acceptance_env:
  up:        docker compose -f docker-compose.acceptance.yml up -d --wait
  down:      docker compose -f docker-compose.acceptance.yml down -v
  database:  postgres:16
  ui_driver: playwright
  base_url:  http://localhost:3000
git: { main_branch: main }
paths: { plans: docs/craft/plans, design: docs/craft/design }
```

## Starter: C# / .NET

```yaml
stack: [csharp]
package_manager: dotnet
commands:
  install:      dotnet restore
  build:        dotnet build -c Release
  test:         dotnet test --filter Category!=Acceptance
  acceptance:   dotnet test --filter Category=Acceptance
  run:          dotnet run --project src/Api
  format_check: dotnet format --verify-no-changes
  format_write: dotnet format
acceptance_env:
  up:        docker compose -f docker-compose.acceptance.yml up -d --wait
  down:      docker compose -f docker-compose.acceptance.yml down -v
  database:  postgres:16              # or mcr.microsoft.com/mssql/server:2022-latest
  base_url:  http://localhost:8080
git: { main_branch: main }
paths: { plans: docs/craft/plans, design: docs/craft/design }
```

## Starter: Rust

```yaml
stack: [rust]
package_manager: cargo
commands:
  build:        cargo build --release
  test:         cargo test
  acceptance:   cargo test --test acceptance -- --ignored
  run:          cargo run
  lint:         cargo clippy -- -D warnings
  format_check: cargo fmt --check
git: { main_branch: main }
paths: { plans: docs/craft/plans, design: docs/craft/design }
```

## Starter: Go

```yaml
stack: [go]
package_manager: go
commands:
  build:        go build ./...
  test:         go test ./...
  acceptance:   go test -tags=acceptance ./test/acceptance/...
  run:          go run ./cmd/server
  lint:         golangci-lint run
  format_check: gofmt -l .
git: { main_branch: main }
paths: { plans: docs/craft/plans, design: docs/craft/design }
```

## Notes on the acceptance environment

`acceptance_env` is the newest and least-guessable part, so it's the one to confirm with the user during bootstrap. The three questions worth asking when the repo doesn't already answer them:

1. **How is the production-like app brought up?** Usually a `docker compose` file; capture the `up`/`down` commands (prefer `--wait`/healthchecks so tests don't race a booting service).
2. **Which real database?** Name the exact engine and version matching production.
3. **Which external dependencies can't be real, and what fakes stand in?** List each external deployed fake — never a code-level double. If there are none (everything can run for real), say so and omit `fakes`.
