---
name: craft-ops-conventions
description: "Use to record and read a project's concrete DevOps conventions in a .craft-ops.yml file — the commands and settings the generic craft-ops skills need but can't guess: the environments and promotion order, the cloud and IaC tool plus its plan/apply commands, the CI system and artifact registry, the deploy/rollout tool and rollback command, the observability stack, the secret manager, the base branch, and where each domain's design notes live. Trigger when setting up craft-ops in a new repo, when a skill or agent needs a project-specific ops command it doesn't know, or when the conventions change. Reads .craft-ops.yml at the repo root (self-contained — never craft's .craft.yml) and bootstraps one by discovering the project's tooling when it's absent. Not for designing or authoring pipelines, infrastructure, rollouts, or observability — those are the other craft-ops skills."
---

# Craft-Ops Conventions — teach the suite this project's ops commands

## Why this exists

The craft-ops skills are deliberately cloud- and tool-agnostic — that's what lets the same discipline design and author a pipeline whether it runs on GitHub Actions or GitLab CI, provisions AWS or GCP, deploys with a blue/green script or a Kubernetes rollout. The tradeoff is that a generic skill can't know *how this project* actually provisions, deploys, or instruments itself. Left to guess, every skill improvises — "maybe `terraform apply`?", "probably ArgoCD?" — and gets it wrong on half your repos, or worse, silently invents a plausible-sounding command that isn't the one this project uses.

`.craft-ops.yml` closes that gap. A project states its concrete ops commands and conventions **once**, at the repo root, and every craft-ops skill and agent reads them instead of guessing. This is what makes the suite portable: the discipline — small modules, protected durable resources, read-the-plan, mitigate-first — is universal; the commands are per-project, and they live in one file.

## The file

A single `.craft-ops.yml` at the repository root, **committed** so the whole team and every agent share it. It is **self-contained**: it declares its own `git.main_branch` and `stack`, and it is a distinct file from craft's `.craft.yml`. craft-ops stays independently installable — a repo can run craft-ops without craft, or vice versa — so this skill never reads or writes `.craft.yml`, and never assumes one exists.

```yaml
stack: [terraform, kubernetes]
git:
  main_branch: main
environments:
  order: [dev, staging, production]
cloud:
  provider: aws
  iac_tool: terraform
  iac_commands:
    plan:  terraform plan
    apply: terraform apply
cicd:
  system: github-actions
  artifact_registry: ghcr.io/acme/api
  artifact_identity: image-digest
deployment:
  tool: argo-rollouts
  rollout_command:  kubectl argo rollouts set image api api=$IMAGE
  rollback_command: kubectl argo rollouts undo api
observability:
  metrics:    prometheus
  dashboards: grafana
  alerts:     alertmanager
secrets:
  manager: aws-secrets-manager
paths:
  pipelines:      docs/craft-ops/pipelines
  infrastructure: docs/craft-ops/infrastructure
  deployments:    docs/craft-ops/deployments
  observability:  docs/craft-ops/observability
```

The full annotated schema, every field, and per-stack starter files are in `references/schema.md`.

## Reading it — the rule for every skill and agent

<HARD-GATE>
Before running or generating anything project-specific — an IaC plan or apply, a deploy or rollout, alert-rule generation, choosing the artifact registry, deciding the environments or their promotion order — **read `.craft-ops.yml` and use the value it specifies.** Do not guess a command or a tool when the file answers it, and do not invent your own when the project has already stated one. If the file is missing the key you need, bootstrap or extend it (below) rather than guessing silently.
</HARD-GATE>

This is what turns "run the plan," "roll out the release," or "wire up the alert" in a dozen skills from a hopeful guess into a correct, project-specific action.

## Bootstrapping a new repo

When craft-ops first runs in a project and there's no `.craft-ops.yml`, create one by **discovering** the tooling, then confirming with the user:

1. **Detect the stack and commands.** Read CI config (`.github/workflows`, `.gitlab-ci.yml`), IaC sources (`*.tf`, Pulumi programs, CloudFormation/CDK), `docker-compose*.yml` and Kubernetes manifests, and any dashboard or alert-rule configs already in the repo. These usually reveal the cloud provider, IaC tool, CI system, and artifact registry directly.
2. **Draft `.craft-ops.yml`** from what you found, filling the schema in `references/schema.md`.
3. **Confirm the gaps.** Ask the user only about what discovery couldn't settle — most often the observability stack and the rollout/rollback tool, since those are the newest concepts and rarely show up unambiguously in source. Don't interrogate what the repo already told you.
4. **Write and commit it.** Now every subsequent skill or agent reads it first.

## Keeping it honest

`.craft-ops.yml` is only useful while it's true. When a command or tool changes — the IaC provider moves, the rollout tool is swapped, a new environment is added to the promotion order — update the file in the same change. A stale conventions file is worse than none, because skills will trust it. Treat it like any other project contract: it changes with the project.

## How the rest of the suite uses it

| Skill / agent | Reads |
|---------------|-------|
| `infrastructure-authoring` / `infrastructure-design` | `cloud.provider`, `cloud.iac_tool`, `cloud.iac_commands` |
| `pipeline-authoring` / `cicd-pipeline-design` | `cicd.system`, `cicd.artifact_registry`, `cicd.artifact_identity`, `environments.order` |
| `deployment-authoring` / `deployment-design` | `deployment.tool`, `deployment.rollout_command`, `deployment.rollback_command`, `environments.order` |
| `observability-authoring` / `observability-design` | `observability.metrics`, `observability.dashboards`, `observability.alerts` |
| `incident-response` | `deployment.rollback_command`, `observability.*` for mitigation and diagnosis |
| the design skills generally | `environments`, `paths.*` for where to write their design notes |
| `craft-ops-author` / `craft-ops-designer` | whichever domain keys the skill or note it's authoring needs |
| every domain | `secrets.manager` before referencing how a credential is stored or retrieved; `git.main_branch` for branch-relative operations |

## Exit condition

A `.craft-ops.yml` exists at the repo root, is committed, and accurately states the ops conventions the suite needs. It is self-contained — its own `git.main_branch` and `stack`, never craft's `.craft.yml`. Any skill or agent that must plan, apply, deploy, roll back, or generate an alert reads it first.
