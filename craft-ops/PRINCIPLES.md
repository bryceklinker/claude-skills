# Craft-Ops Principles

The canonical *why* behind craft-ops. It extends craft-code's `PRINCIPLES.md` from application code into the systems that build, ship, and run it, but stands on its own: craft-ops never requires craft-code to be installed. Each rule comes with its reason; when one genuinely fights the problem in front of you, depart deliberately and record why.

## Core

### 1. Use less to achieve more

The fewest stages, environments, resources, modules, flags, signals, and scripts that deliver what's needed reliably. Each addition answers to a present requirement, not an imagined one. Reliability that's actually needed — a rollback path, a health gate, an alert on user pain — is part of the minimum; speculative stages, unused environments, wrapper scripts, and dashboards nobody reads are not. *(craft-code: use less to achieve more.)*

### 2. Ops code is proven by running it

A deploy script, pipeline step, IaC module, or alert rule is correct when it executes and does its job against a real or throwaway target — the artifact is pushed, the resource converges, the rollout progresses and halts, the alert fires. That run is its test. A separate unit-test suite for an ops script usually re-states the script with mocks of the very systems it drives, so it adds code to maintain without adding confidence. Write one only when a script carries real decision logic — a gate threshold, a version computation — with more cases than running it can cheaply cover. *(craft-code: done rests on evidence.)*

### 3. Build once, promote the same artifact

One immutable artifact, identified by a digest, moves across environments unchanged. Rebuilding per environment means what you tested isn't what you shipped.

### 4. The pipeline is code, versioned with what it ships

No clicked-together jobs. The pipeline is reviewed like code, lives with the app, and changes travel with the commits they affect.

### 5. Fast feedback, fail early

Cheapest and most-likely-to-fail stages first. A broken main stops the line.

### 6. Reproducible, hermetic builds

Same input, same artifact: pinned toolchains and dependencies, ephemeral build environments, no network-dependent build steps.

### 7. Deploy is not release

Shipping the bits and exposing the behavior are separate actions, so a bad release is a flag flip rather than a rebuild under pressure.

### 8. Config and secrets enter from the environment

Never baked into the artifact, never committed to the repo.

### 9. Done rests on evidence from the real target

Done is observed health in the target environment — a passing health check, real traffic served, a metric that moved — not a green pipeline job.

### 10. Mitigate fast, remediate at the cause

During an incident the fastest safe lever wins: roll back, fail over, scale out, flip the flag. But mitigation isn't a fix, and the failure mode of ops is letting it become one — the nightly restart, the silenced alert, the capacity that hides a leak. Mitigation ends with the cause tracked as work, and when remediation options are laid out, exactly one is recommended: the most durable that fits the constraints. A mitigation kept on purpose records what would let it be removed. *(craft-code: fix the cause at its level.)*

## Infrastructure as Code

1. **Declarative desired state**, not imperative steps.
2. **Idempotent and convergent** — applying the same configuration twice is safe and changes nothing.
3. **Immutable where disposable; protected where durable.** Compute, functions, containers, load balancers, and most networking hold no irreplaceable state: replace, don't mutate. Databases, object stores, queues, topics, and buses hold state that can't be rebuilt from code: deletion protection, no-destroy guards, migrate rather than recreate. Misclassifying a resource is how data is lost.
4. **Review before apply** — and the first check on every plan is whether it destroys or replaces a durable resource. That is never applied on a green plan alone.
5. **State is remote, locked, and treated as a secret** — never local, never committed.
6. **No manual drift** — code is the source of truth; drift is reconciled back to it.
7. **Small, composable modules; environment parity through inputs.**
8. **Least privilege; no secrets in code or state.**
9. **Prefer portable tooling** (Terraform, OpenTofu, Pulumi, Kubernetes) over cloud-specific tools; lock-in is a deliberate, recorded choice, never the default.

## Deployment & release

1. **Deploy is not release** — a version can run in production dark, behind a flag.
2. **Progressive delivery** — expose a small blast radius first and widen on healthy signals.
3. **Rollback-first** — every release has a fast, rehearsed way back, decided before the rollout starts.
4. **Health-gated promotion; automatic halt on regression** — objective signals, not a human eyeballing a dashboard.
5. **Compatibility across the transition** — old and new run at once: expand-contract migrations, N-1 compatible schemas, APIs, and messages.
6. **Control the blast radius** — internal, then canary, then wider.
7. **Release is a decision; deploy is routine.**
8. **You can only progressively deliver what you can observe** — the gating signals exist before the rollout does.

## Observability & incident response

1. **Observability is a design input** and the precondition for safe deployment.
2. **Alert on symptoms, not causes** — page on user-facing pain; noise trains people to ignore pages.
3. **SLOs and error budgets are the contract**, defined from the user's perspective.
4. **Runtime levers** — verbosity, sampling, and trace detail turn up and down without a redeploy, scoped narrowly, with default and incident settings designed in.
5. **Instrument for the questions you'll ask under pressure** — structured, correlatable signals you can slice by tenant, version, and route.
6. **Signals cost** — cardinality and retention are a budget; sample and aggregate deliberately.
7. **Mitigate before you diagnose.**
8. **Blameless** — review the conditions, not the person on call.
9. **Every incident tightens the ratchet** — a tracked action item and a new test or alert that would have caught it.
10. **Find the cause with method** — reproduce, bisect, one hypothesis at a time, with a written timeline.

---

*Lineage:* craft-code's discipline — immutability, evidence over inspection, the ratchet, the least that works — applied to pipelines, infrastructure, and operations.
