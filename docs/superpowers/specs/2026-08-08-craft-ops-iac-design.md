# craft-ops — Infrastructure as Code domain (infrastructure-design skill)

*Design spec — 2026-08-08*

## Purpose

Add the second domain to the `craft-ops` DevOps suite: **Infrastructure as Code**. This build
delivers one skill, `infrastructure-design`, plus the full IaC principle set — following the exact
pattern established by the CI/CD domain (`cicd-pipeline-design`). It is a **thinking / decision**
skill that decides the *shape* of infrastructure and reviews existing IaC against the conventions,
producing a short design note. It **never writes the actual IaC configuration** — that is a future
`infrastructure-authoring` skill.

## Non-goals

- Does **not** author IaC config (Terraform/OpenTofu/Pulumi/CloudFormation/Bicep/etc.) — that is the
  deferred `infrastructure-authoring` skill.
- Does **not** build the deployment/release or observability/incident domains, or the `.craft-ops.yml`
  conventions skill — all remain named stubs.
- Tool-agnostic: the skill's prose names tools only as examples of a category, never as a required
  choice, and uses no vendor-specific file extensions or syntax.

## Shape

`craft-ops/skills/infrastructure-design/` mirrors `cicd-pipeline-design` and craft's
`architecture-design`: a thinking phase whose output is a design note, not code. Same design-vs-
authoring split, `-design` naming, generic wording, and PRINCIPLES citations. It inherits the
scope-down house rule added to `cicd-pipeline-design` in its iteration-2 refinement: on a **targeted
change**, decide the implicated areas in depth and dispatch the rest in a one-line "not implicated"
note; on **greenfield infrastructure**, decide them all.

## PRINCIPLES.md — IaC expansion

The current one-line IaC stub in `craft-ops/PRINCIPLES.md` is replaced with a full principle set,
each citing the craft root it extends. Final wording is refined during implementation; intent is
fixed here.

1. **Declarative desired state, not imperative steps** — describe the end state and let the tool
   converge; don't script step-by-step mutations. *(craft: failure/behavior modeled as values →
   desired-state over imperative.)*
2. **Idempotent & convergent** — applying the same configuration repeatedly is always safe and yields
   the same result.
3. **Immutable where disposable; protected where durable.** Split every resource into two tiers.
   **Disposable** resources (compute, functions, containers, load balancers, most networking) hold no
   irreplaceable state — treat them as immutable: *replace, don't mutate*, rebuilt freely from code.
   **Durable** resources (databases, object/blob stores, queues, topics, event buses — anything
   holding data or messages) hold state that **cannot be rebuilt from code** and must **never be
   deleted or replaced** as a side effect of a change. For the durable tier, "immutable" means
   *protect and migrate*: deletion-protection and no-destroy lifecycle guards on the resource, and
   schema/data **migration** rather than teardown-and-recreate. Classifying a resource into the wrong
   tier is how you lose data. *(craft: immutability by default — applied with the realism that state
   can't be re-derived.)*
4. **Review before apply — first job: catch a destroy/replace of a durable resource.** The plan/diff
   is the gate, and reviewing it is not merely "does this look right." Its first, non-negotiable
   check: does this plan destroy or replace any durable resource? A forced replacement of a database
   or deletion of a queue is stop-the-line — it is not applied on the strength of a green plan; it
   requires deliberate, explicit confirmation and usually a migration path instead. *(craft: judgment
   is independent, and "done" rests on evidence — the plan is the evidence.)*
5. **State is shared, locked, and sensitive** — remote, versioned, locked state; never local or
   committed to the repo; treated as a secret.
6. **No manual drift — code is the single source of truth** — no console clicking; drift is detected
   and reconciled back to code. *(craft: green main is sacred → the code is the truth.)*
7. **Small, composable modules; environment parity through inputs** — reusable modules with clear
   inputs/outputs; staging and prod are built from the *same* modules, differing only in variables.
   *(craft: small single-purpose units; the domain is independent of how data enters or leaves.)*
8. **Least privilege; secrets never in code or state** — scoped apply-time credentials; no secrets
   baked into configuration or state. *(craft: config and secrets enter from the environment.)*
9. **Prefer portable, cloud-agnostic tooling; lock-in is a deliberate, recorded cost.** Given a
   choice, prefer IaC tools not bound to one cloud (Terraform, OpenTofu, Pulumi, Kubernetes) over
   cloud-specific ones (Bicep, CloudFormation, ARM), and apply the same bias to provisioned tech where
   a portable equivalent exists. Cloud-specific tools sometimes genuinely win (deeper native
   integration, less abstraction), but they create lock-in that is nearly impossible to undo later, so
   choosing one is a conscious tradeoff recorded with its *why* — never the default. *(craft: state
   the why; keep the escape hatch.)*
10. **State the why; keep the escape hatch** — inherited verbatim from craft.

The deployment & release and observability & incident-response domains remain one-line stubs.

## The infrastructure-design skill — what it decides

Nine decision areas (each ties back to a principle above):

1. **Resource inventory & tier classification** — enumerate the resources this change touches and
   classify each **disposable vs. durable**; for every durable resource, name its deletion-protection
   / no-destroy guard.
2. **Tool & tech selection** — which IaC tool and provisioned tech, applying the portability bias; any
   lock-in choice recorded with its *why*.
3. **Module boundaries & composition** — the modules, their inputs/outputs, what is shared vs.
   per-environment.
4. **State management** — where state lives (remote, locked, versioned), how it is isolated, treated
   as sensitive.
5. **Change safety — review-before-apply & blast radius** — how the change is planned, diffed, and
   applied; explicitly whether anything here destroys or replaces a durable resource, and the
   migration path if so.
6. **Environment parity** — the same modules across environments, differing only in inputs.
7. **Identity, least privilege & secrets** — scoped apply-time credentials; no secrets in code or
   state.
8. **Drift stance** — how drift is detected and reconciled; nothing changed by hand.
9. **Evidence of done** — the plan applied cleanly *and* a real post-apply check that the
   infrastructure is in its desired state (resource reachable/healthy), not merely "apply exited 0."

### Output

A short infrastructure design note saved where the work lives (e.g.
`docs/craft-ops/infrastructure/YYYY-MM-DD-<name>.md`): the tier classification, tool choice,
modules, state, change-safety, parity, identity, drift, and evidence decisions — each with its *why*.
Enough for the future `infrastructure-authoring` skill to implement.

### Guardrails (mirror cicd-pipeline-design)

- **YAGNI on resources and environments** — only what the change actually needs.
- **Never write the IaC configuration here** — that belongs to the authoring skill, behind its own
  review.
- **Prefer the existing shape** — if the infrastructure already fits the conventions, the note is
  short.
- **Match the note's length to the change** — depth on implicated areas, one line for the rest.

### references/

Mirrors the 3-file `cicd-pipeline-design` split; the SKILL.md cites rather than restates:

- `resource-tiers.md` — disposable vs. durable classification, deletion-protection guards, and
  migrate-don't-teardown for the durable tier.
- `state-and-modules.md` — remote/locked/versioned state and isolation; small composable modules;
  environment parity through inputs.
- `review-before-apply.md` — the plan/diff gate, catching destroy/replace of durable resources, and
  blast-radius thinking.

Tool-selection guidance lives inline in `SKILL.md` and in `PRINCIPLES.md` (it is an opinion, not a
mechanics reference).

## Scope of this build

**Delivered:**
- `PRINCIPLES.md` — the one-line IaC stub replaced with the full ~10-principle set; deployment and
  observability domains remain one-line stubs.
- `infrastructure-design` skill: `SKILL.md` + the three `references/` docs.
- README domain table: Infrastructure as Code / `infrastructure-design` marked **Built**;
  `infrastructure-authoring` added as **Planned**.
- Version bump to `0.2.0` in `plugin.json`, the marketplace entry, and `CHANGELOG.md`.
- Skill-creator validation (behavioral eval loop + trigger optimization) run after the build, per the
  established workflow.

**Deferred (named, not built):** `infrastructure-authoring`; deployment/release; observability/
incident; the `.craft-ops.yml` conventions skill.

## Success criteria

- `PRINCIPLES.md` states the full IaC principle set, each citing the craft root it extends, including
  the disposable/durable tier distinction, the review-before-apply destroy/replace gate, and the
  cloud-agnostic tooling bias.
- The `infrastructure-design` skill triggers on IaC design/review situations and produces a design
  note covering the nine decision areas — and never writes IaC configuration.
- On a targeted change the note is scoped (depth on implicated areas, one-liners for the rest); on
  greenfield it covers all nine.
- README accurately marks Infrastructure as Code as Built and `infrastructure-authoring` as Planned;
  the plugin version is `0.2.0` across plugin.json, marketplace, and CHANGELOG.
