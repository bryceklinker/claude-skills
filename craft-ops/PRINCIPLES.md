# Craft-Ops Principles

The canonical *why* behind craft-ops. Individual skills restate the slice of this they need to stand alone, but this is the source — when a craft-ops skill says "see the principles," it means here. This derives from and cites craft's `PRINCIPLES.md`, extending that methodology from application code into the systems that build, ship, and run it — but craft-ops stands on its own: you can install and use it without craft. Every rule is strict on purpose, each is given with its reason, and each has an escape hatch for the case where it genuinely fights the problem in front of you.

## 1. Build once, promote the same artifact

Never rebuild per environment. One immutable artifact, identified by a content or commit digest, moves across dev, staging, and production unchanged. Rebuilding for each environment means what you tested is not what you shipped — a different compiler run, a different dependency resolution, a different bug. *(craft: immutability by default → immutable artifacts.)*

## 2. The pipeline is code, versioned with what it ships

No clicked-together jobs in a UI that only one person remembers how to reproduce. The pipeline is reviewed like any code, lives in the same repository as the app it builds, and changes travel with the commits they affect. A pipeline you can't diff is a pipeline you can't trust.

## 3. Fast feedback, fail early

Order stages by cost and likelihood of failure: cheapest and most-likely-to-fail first. A broken main is a stop-the-line event, not a background task — the longer a break sits, the more work piles up behind it and the harder the bisection gets. *(craft: tests come first, and they are a ratchet.)*

## 4. Reproducible, hermetic builds

Same input, same artifact, every time. Pin toolchains and dependency versions, build in isolated and ephemeral environments, and cut network-dependent steps out of the build path. A build that depends on what happened to be installed on the runner that day is not a build you can trust to repeat.

## 5. Deploy is not release

Shipping the bits to an environment and exposing the new behavior to traffic are two different actions — decouple them. That's what makes rolling forward or back cheap: a bad release is a flag flip, not a rebuild and redeploy under pressure. *(previews the deployment & release domain.)*

## 6. Config and secrets enter from the environment, never the artifact or repo

One artifact promoted unchanged means environment-specific values can't live inside it. Config and secrets are injected at runtime from the environment — never baked into the build, never committed to the repo. *(craft: the domain is independent of how data enters or leaves.)*

## 7. Done rests on evidence from the real target

A deploy is "done" when it's observed healthy in the actual target environment — a passing health check, real traffic served, a metric that moved — not when the pipeline job turns green. Green is a claim about the pipeline; evidence is a claim about the system. *(craft: judgment is independent, and "done" rests on evidence.)*

## 8. State the why; keep the escape hatch

Every strict rule here is legible rather than dogmatic because it comes with its reason. When a rule genuinely fights the problem in front of you, that tension is worth a conscious, recorded note — not a silent abandonment of the discipline. The rules are strict so that applying them by reflex frees attention for the actual incident, the actual outage, the actual deadline. *(craft: state the why; keep the escape hatch — inherited verbatim.)*

## Infrastructure as Code

### 1. Declarative desired state, not imperative steps

Describe the end state and let the tool converge to it; don't script step-by-step mutations. *(craft: failure/behavior modeled as values → desired-state over imperative.)*

### 2. Idempotent & convergent

Applying the same configuration repeatedly is always safe and yields the same result.

### 3. Immutable where disposable; protected where durable

Split resources into two tiers. Disposable resources — compute, functions, containers, load balancers, most networking — hold no irreplaceable state: treat them as immutable, replace-don't-mutate, rebuilt freely from code. Durable resources — databases, object/blob stores, queues, topics, event buses, anything holding data or messages — hold state that cannot be rebuilt from code and must never be deleted or replaced as a side effect of a change; for them "immutable" means protect and migrate: deletion-protection and no-destroy guards, schema/data migration rather than teardown-and-recreate. Classifying a resource into the wrong tier is how you lose data. *(craft: immutability by default — applied with the realism that state can't be re-derived.)*

### 4. Review before apply — first job: catch a destroy/replace of a durable resource

The plan/diff is the gate, and its first, non-negotiable check is whether the plan destroys or replaces any durable resource. A forced replacement of a database or deletion of a queue is stop-the-line: never applied on a green plan alone, always requiring deliberate, explicit confirmation and usually a migration path. *(craft: judgment is independent, and "done" rests on evidence — the plan is the evidence.)*

### 5. State is shared, locked, and sensitive

Remote, versioned, locked state; never local, never committed to the repo; treated as a secret.

### 6. No manual drift — code is the single source of truth

No console clicking. Drift is detected and reconciled back to code. *(craft: green main is sacred → the code is the truth.)*

### 7. Small, composable modules; environment parity through inputs

Reusable modules with clear inputs and outputs; staging and prod are built from the same modules, differing only in variables. *(craft: small single-purpose units; the domain is independent of how data enters or leaves.)*

### 8. Least privilege; secrets never in code or state

Scoped, apply-time credentials; no secrets baked into configuration or state. *(craft: config and secrets enter from the environment.)*

### 9. Prefer portable, cloud-agnostic tooling; lock-in is a deliberate, recorded cost

Given a choice, prefer tools not bound to one cloud — Terraform, OpenTofu, Pulumi, Kubernetes — over cloud-specific ones — Bicep, CloudFormation, ARM — and apply the same bias to provisioned tech where a portable equivalent exists. Cloud-specific tools sometimes genuinely win, but they create lock-in that's nearly impossible to undo later, so choosing one is a conscious tradeoff recorded with its why — never the default. *(craft: state the why; keep the escape hatch.)*

### 10. State the why; keep the escape hatch

Inherited verbatim from craft: every strict rule here is legible rather than dogmatic because it comes with its reason, and when a rule genuinely fights the problem in front of you, that tension is worth a conscious, recorded note — not a silent abandonment of the discipline.

## Coming domains

CI/CD and Infrastructure as Code are the domains craft-ops covers in full. The rest of the suite is scaffolded as one-line stubs today; each gets its own full principles when that domain's skills are built.

- **Deployment & release** — progressive delivery, rollback-first, deploy decoupled from release. *(stub)*
- **Observability & incident response** — symptoms over causes, SLOs, blameless and reproducible incident handling. *(stub)*

---

*Lineage:* this methodology extends craft's discipline — immutability, evidence over inspection, tests as a ratchet, the stated *why* with its escape hatch — from application code into the pipelines, infrastructure, and operations that build, ship, and run it.
