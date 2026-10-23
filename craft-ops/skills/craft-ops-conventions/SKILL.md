---
name: craft-ops-conventions
description: "Use to record and read a project's concrete DevOps conventions in a .craft-ops.yml file — the commands and settings the generic craft-ops skills need but can't guess: the environments and promotion order, the cloud and IaC tool plus its plan/apply commands, the CI system and artifact registry, the deploy/rollout tool and rollback command, the observability stack, the secret manager, the base branch, and where each domain's design notes live. Trigger when setting up craft-ops in a new repo, when a skill or agent needs a project-specific ops command it doesn't know, or when the conventions change. Reads .craft-ops.yml at the repo root (self-contained — never craft-code's .craft-code.yml) and bootstraps one by discovering the project's tooling when it's absent. Not for designing or authoring pipelines, infrastructure, rollouts, or observability — those are the other craft-ops skills."
---

# Craft-Ops Conventions

The craft-ops skills are cloud- and tool-agnostic, so they can't know how this project provisions, deploys, or instruments itself. A committed `.craft-ops.yml` at the repo root states it once, and every skill and agent reads it instead of guessing. It's self-contained — its own `git.main_branch` and `stack` — and separate from craft-code's `.craft-code.yml`, which craft-ops never reads or writes.

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

Every field and per-stack starters are in `references/schema.md`. Include only the keys the project uses.

## Reading it

Before running or generating anything project-specific — a plan or apply, a deploy, rollout, or rollback, alert generation, choosing the registry or the environments — read `.craft-ops.yml` and use its value. If the key is missing, extend the file rather than guessing.

## Bootstrapping

When it's absent: discover the tooling from CI config, IaC sources, compose files and Kubernetes manifests, and existing dashboard or alert configs; draft the file; ask only about what discovery couldn't settle (usually the observability stack and rollout tool); write and commit it.

## Keeping it true

When a tool or command changes, update the file in the same change. A stale conventions file is worse than none, because skills trust it.
