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

## Coming domains

CI/CD is the first domain craft-ops covers in full. The rest of the suite is scaffolded as one-line stubs today; each gets its own full principles when that domain's skills are built.

- **Infrastructure as Code** — declarative, idempotent, immutable infrastructure with review-before-apply. *(stub)*
- **Deployment & release** — progressive delivery, rollback-first, deploy decoupled from release. *(stub)*
- **Observability & incident response** — symptoms over causes, SLOs, blameless and reproducible incident handling. *(stub)*

---

*Lineage:* this methodology extends craft's discipline — immutability, evidence over inspection, tests as a ratchet, the stated *why* with its escape hatch — from application code into the pipelines, infrastructure, and operations that build, ship, and run it.
