# .craft-ops.yml — full schema and starter files

`.craft-ops.yml` lives at the repository root and is committed. It is **self-contained**: it declares its own `stack` and `git.main_branch`, and it never references craft's `.craft.yml` — craft-ops stays independently installable, so a repo can run craft-ops without craft, or vice versa. Every top-level section is optional — a repo with no IaC omits `cloud`, a repo that hasn't wired up alerting omits `observability.alerts`, and so on. State only what the project actually has; unknown keys are ignored, so you can extend it for project-specific needs.

## Table of contents
- The full annotated schema
- Field reference
- Starter: AWS + OpenTofu + GitHub Actions + Argo Rollouts + Prometheus
- Starter: GCP + Pulumi + Cloud Build + Cloud Run
- Starter: minimal (environments + paths only)
- Notes on bootstrapping

## The full annotated schema

```yaml
# What infrastructure/deployment tooling the project uses. Informs which
# craft-ops conventions apply — not the application's language stack.
stack: [terraform, kubernetes]        # e.g. terraform, opentofu, pulumi, cloudformation, kubernetes, ecs, ...

git:
  main_branch: main                   # the base branch pipelines deploy from and rollbacks compare against

# The environments this project promotes through, and the order it promotes
# them in. The LIST ORDER IS THE PROMOTION ORDER — first entry is promoted
# to first, last entry is the final/production target.
environments:
  order: [dev, staging, production]

# Present only when the project provisions infrastructure as code. Omit this
# whole section for a repo with no IaC (e.g. a pure application repo that
# deploys into infrastructure someone else owns).
cloud:
  provider: aws                       # aws | gcp | azure | ...
  iac_tool: terraform                 # terraform | opentofu | pulumi | cloudformation | cdk | ...
  iac_commands:
    validate: terraform validate      # optional — static/config validation, run before plan
    plan:  terraform plan             # required — preview a change against real state
    apply: terraform apply            # required — apply a previously planned change

# How the project builds and ships artifacts. Present whenever there's a
# pipeline producing something deployable.
cicd:
  system: github-actions              # github-actions | gitlab-ci | circleci | jenkins | ...
  artifact_registry: ghcr.io/acme/api # where built artifacts are pushed (image registry, package feed, ...)
  artifact_identity: image-digest     # how an artifact is uniquely referenced downstream: image-digest | image-tag | semver | commit-sha

# How a built artifact gets into an environment, and how that's undone.
# Present whenever the project has an automated or scripted deploy path.
deployment:
  tool: argo-rollouts                 # argo-rollouts | kubectl | ecs-deploy | helm | a custom script, ...
  rollout_command:  kubectl argo rollouts set image api api=$IMAGE   # promote a new artifact into an environment
  rollback_command: kubectl argo rollouts undo api                   # undo the most recent rollout

# The observability stack: where metrics live, where dashboards are viewed,
# and what fires alerts. Present whenever the project has instrumentation to
# read from or alert rules to author against.
observability:
  metrics:    prometheus              # prometheus | cloudwatch | datadog | ...
  dashboards: grafana                 # grafana | datadog | cloudwatch-dashboards | ...
  alerts:     alertmanager            # alertmanager | pagerduty | opsgenie | cloudwatch-alarms | ...

# Where application/deploy-time secrets are stored and retrieved from.
# Present whenever the project has secrets to reference at all (most do).
secrets:
  manager: aws-secrets-manager        # aws-secrets-manager | gcp-secret-manager | vault | doppler | ...

# Where each craft-ops domain writes and reads its design notes, so a
# resumed session or a subagent finds them where the project keeps them.
paths:
  pipelines:      docs/craft-ops/pipelines
  infrastructure: docs/craft-ops/infrastructure
  deployments:    docs/craft-ops/deployments
  observability:  docs/craft-ops/observability
```

## Field reference

- **`stack`** — a list, not a scalar; a project may use more than one IaC/orchestration tool at once (e.g. Terraform for cloud resources, Kubernetes manifests for workloads). This is the *infrastructure/ops* stack, distinct from — and never derived from — an application's language stack in `.craft.yml`.
- **`git.main_branch`** — the branch pipelines build from and the branch rollbacks and promotion diffs are compared against. Consumed anywhere craft-ops needs a branch-relative operation.
- **`environments.order`** — a nested list under `environments`. Its order *is* the promotion order: a change reaches `order[0]` first and `order[-1]` (commonly `production`) last. `pipeline-authoring`, `deployment-authoring`, and the design analogs all read this to know what "promote" means for this project — never assume `dev`/`staging`/`production` if the file says otherwise.
- **`cloud`** — omit the entire section when the project doesn't provision its own infrastructure (e.g. it deploys into a platform or cluster someone else manages). When present, `provider` and `iac_tool` are required; `iac_commands.plan` and `iac_commands.apply` are required since every IaC workflow needs both; `iac_commands.validate` is optional — include it only if the tool has a distinct validate/lint step the project actually runs before planning.
- **`cicd.artifact_identity`** — how a downstream consumer (a rollout command, a deploy manifest) uniquely names the artifact it's promoting. This matters because `rollout_command` templates often need to know whether to substitute a digest, a tag, or a semver string.
- **`deployment.tool` / `rollout_command` / `rollback_command`** — the concrete commands `deployment-authoring` and `incident-response` use instead of guessing. `rollback_command` in particular is read by `incident-response` for mitigate-first response — it must be a command that actually reverts the last rollout, not just a description of one.
- **`observability.metrics` / `dashboards` / `alerts`** — three distinct systems that are often, but not always, the same product. Keep them separate even when one vendor supplies all three (e.g. Datadog for metrics, dashboards, and alerts) — the fields are read independently by different skills.
- **`secrets.manager`** — read by every domain before referencing how a credential is stored or retrieved, so generated pipelines, IaC, or rollout commands reference secrets the way this project actually manages them (env-injected from a manager, mounted, etc.) rather than inventing a plausible-looking placeholder.
- **`paths.*`** — where `pipeline-authoring`, `infrastructure-authoring`, `deployment-authoring`, and `observability-authoring` (and their `-design` counterparts) write and read their design notes. Keep these distinct from craft's `paths.plans` / `paths.design` in `.craft.yml` — the two files are never cross-referenced.

## Starter: AWS + OpenTofu + GitHub Actions + Argo Rollouts + Prometheus

```yaml
stack: [opentofu, kubernetes]
git:
  main_branch: main
environments:
  order: [dev, staging, production]
cloud:
  provider: aws
  iac_tool: opentofu
  iac_commands:
    validate: tofu validate
    plan:  tofu plan
    apply: tofu apply
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

## Starter: GCP + Pulumi + Cloud Build + Cloud Run

```yaml
stack: [pulumi]
git:
  main_branch: main
environments:
  order: [staging, production]
cloud:
  provider: gcp
  iac_tool: pulumi
  iac_commands:
    plan:  pulumi preview
    apply: pulumi up
cicd:
  system: cloud-build
  artifact_registry: us-central1-docker.pkg.dev/acme/api
  artifact_identity: image-digest
deployment:
  tool: gcloud-run-deploy
  rollout_command:  gcloud run deploy api --image=$IMAGE --region=us-central1
  rollback_command: gcloud run services update-traffic api --to-revisions=PREVIOUS=100
observability:
  metrics:    cloudwatch          # swap for your project's real metrics backend, e.g. cloud-monitoring
  dashboards: grafana
  alerts:     opsgenie
secrets:
  manager: gcp-secret-manager
paths:
  pipelines:      docs/craft-ops/pipelines
  infrastructure: docs/craft-ops/infrastructure
  deployments:    docs/craft-ops/deployments
  observability:  docs/craft-ops/observability
```

## Starter: minimal (environments + paths only)

Use this shape for a repo that's only ready to state its promotion order and where notes go — no IaC, deployment tool, or observability stack wired up yet. Add sections as the project grows into them.

```yaml
git:
  main_branch: main
environments:
  order: [staging, production]
paths:
  pipelines:      docs/craft-ops/pipelines
  infrastructure: docs/craft-ops/infrastructure
  deployments:    docs/craft-ops/deployments
  observability:  docs/craft-ops/observability
```

## Notes on bootstrapping

`cloud`, `deployment`, and `observability` are the sections least likely to be guessable from source alone, so they're the ones worth confirming with the user during bootstrap rather than inventing:

1. **Cloud and IaC.** Usually settled by what's in the repo — `*.tf`/`*.tofu` files, a Pulumi program, a CloudFormation/CDK stack. If none exist, the project may have no `cloud` section at all; don't add one speculatively.
2. **Deployment tool and rollback command.** CI workflow files and Kubernetes manifests often reveal the rollout tool, but the exact `rollback_command` is rarely written down anywhere — confirm it explicitly, since `incident-response` depends on it being correct, not just plausible.
3. **Observability stack.** Dashboard and alert-rule configs in the repo are the strongest signal; when nothing is checked in, ask rather than default to a popular tool the project may not actually run.

Keep `.craft-ops.yml` honest: when a command or tool changes — the IaC provider moves, the rollout tool is swapped, a new environment enters the promotion order — update the file in the same change that makes the change true.
