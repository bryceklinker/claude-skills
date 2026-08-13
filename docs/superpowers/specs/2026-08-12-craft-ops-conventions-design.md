# craft-ops — the `craft-ops-conventions` skill (portability layer)

*Design spec — 2026-08-12*

## Purpose

The craft-ops suite is deliberately framework- and tool-agnostic — that portability is what lets the
same discipline run on any cloud, CI system, or observability stack. The tradeoff is that a generic
skill can't know *how this project* deploys, provisions, or instruments. The four design skills already
say "read `.craft-ops.yml` for the project's environments/commands if present" — but nothing yet
formalizes that file, bootstraps it, or defines its schema.

`craft-ops-conventions` closes that gap. It is the craft-ops analog of craft's `project-conventions`
skill: a project states its concrete ops conventions **once**, at the repo root, in a committed
`.craft-ops.yml`, and every craft-ops skill reads them instead of guessing. This is the suite's
portability layer — the discipline is universal; the commands are per-project.

**This is a separate concern from the future `craft` → `craft-code` rebrand** (a repo-wide rename
queued as its own effort). This spec builds only the new `craft-ops-conventions` skill; the rebrand
will later sweep every "craft" reference (including renaming craft's `project-conventions` →
`craft-code-conventions` and `.craft.yml` → `.craft-code.yml`) across both plugins. `craft-ops` keeps
its name.

## The `.craft-ops.yml` file

A single self-contained `.craft-ops.yml` at the repository root, **committed** so the whole team and
every agent share it. Self-contained per the independently-installable invariant — it carries its own
`git.main_branch` and `stack`, and never depends on craft's `.craft.yml`.

Schema (annotated in full in `references/schema.md`):

```yaml
stack: [kubernetes, aws]          # the tech in play, for the skills to reason about
git:
  main_branch: main
environments: [dev, staging, prod]  # and this is the promotion order
cloud:
  provider: aws
  iac_tool: opentofu               # the IaC tool + how it runs
  iac_commands: { validate: tofu validate, plan: tofu plan, apply: tofu apply }
cicd:
  system: github-actions           # the CI system
  artifact_registry: registry.example.com/checkout
  artifact_identity: digest        # how an artifact is identified/promoted
deployment:
  tool: argo-rollouts              # the progressive-delivery tooling
  rollout_command: kubectl argo rollouts get rollout <name>
  rollback_command: kubectl argo rollouts undo <name>
observability:
  metrics: prometheus
  dashboards: grafana
  alerts: alertmanager
secrets:
  manager: aws-secrets-manager     # where secrets are injected from
paths:                             # where each domain's design notes live
  pipelines:      docs/craft-ops/pipelines
  infrastructure: docs/craft-ops/infrastructure
  deployments:    docs/craft-ops/deployments
  observability:  docs/craft-ops/observability
```

Only the keys a project actually needs are required; a repo with no IaC omits `cloud`, etc. The full
annotated schema and per-stack starter files (AWS/Terraform, GCP/Pulumi, k8s/Argo, etc.) live in
`references/schema.md`.

## The skill

Mirrors the structure of craft's `project-conventions` (its proven analog):

- `craft-ops/skills/craft-ops-conventions/SKILL.md`
- `craft-ops/skills/craft-ops-conventions/references/schema.md`

**SKILL.md** covers:

- **Why it exists** — the portability gap above; the discipline is universal, the commands
  per-project.
- **The file** — a single committed `.craft-ops.yml` at the repo root, self-contained, with the
  schema summarized and `references/schema.md` cited for the full version.
- **The read rule (HARD-GATE)** — before a craft-ops skill or agent runs or generates anything
  project-specific (an IaC plan/apply, a deploy/rollout, an alert-rule generation, choosing an
  artifact registry, picking the environments/promotion order), it **reads `.craft-ops.yml` and uses
  what it specifies**, rather than guessing. If the file is missing the key it needs, bootstrap or
  extend it rather than guessing silently.
- **Bootstrapping a new repo** — when craft-ops first runs and there's no `.craft-ops.yml`: discover
  the tooling (read CI config, `*.tf`/Pulumi, `docker-compose`, k8s manifests, dashboards/alert
  configs), draft the file, confirm the gaps with the user (the newest concepts — the observability
  stack, the rollout tool), then write and commit it.
- **Keeping it honest** — `.craft-ops.yml` is only useful while it's true; when a command or a tool
  changes, update the file in the same change. A stale conventions file is worse than none.
- **How the rest of the suite uses it** — a table mapping each craft-ops skill/agent to the keys it
  reads (e.g. `infrastructure-authoring` → `cloud.iac_commands`; `deployment-authoring` →
  `deployment.*`; `observability-authoring` → `observability.*`; the design skills →
  `environments`, `paths.*`; `craft-ops-author` → whichever domain keys its authoring skill needs).
- **Exit condition** — a committed `.craft-ops.yml` exists at the repo root and accurately states the
  conventions the suite needs; any skill/agent that must run something reads it first.

**references/schema.md** — the full annotated schema (every field, when it's required, examples) plus
per-stack starter `.craft-ops.yml` files.

## Retarget the design skills

The four design skills currently say `.craft-ops.yml` "documents them **until a dedicated conventions
skill exists**." Now it exists, so retarget those clauses to point at `craft-ops-conventions` (e.g.
"read `.craft-ops.yml` — see `craft-ops-conventions`"), mirroring how the "(future) authoring skill"
references were retargeted as each authoring skill shipped. Files: `cicd-pipeline-design`,
`infrastructure-design`, `deployment-design`, `observability-design` SKILL.md.

## Scope of this build

**Delivered:** the `craft-ops-conventions` skill (`SKILL.md` + `references/schema.md`); the four design
skills' "until a dedicated conventions skill exists" clauses retargeted to `craft-ops-conventions`;
README (a Conventions/portability note + any skills listing); CHANGELOG entry + version bump to
`0.10.0`; folded into PR #3. No agent changes (the author agent reads the file via its authoring
skill; no new agent needed).

**Deferred (named):** the full `craft` → `craft-code` rebrand (its own effort).

## Success criteria

- `craft-ops-conventions` triggers when setting up craft-ops in a repo, when a skill/agent needs a
  project-specific command it doesn't know, or when the conventions change; it reads `.craft-ops.yml`
  at the repo root and bootstraps one (by discovery + confirmation) when absent.
- `.craft-ops.yml` is self-contained (own `git.main_branch`/`stack`), never depends on `.craft.yml`,
  and its schema covers the ops conventions the built skills need (environments, cloud/IaC, CI/artifact,
  deployment, observability, secrets, paths).
- The four design skills reference `craft-ops-conventions` rather than "a dedicated conventions skill
  that doesn't exist yet."
- README marks the conventions skill; plugin + marketplace at `0.10.0`; all in PR #3.
