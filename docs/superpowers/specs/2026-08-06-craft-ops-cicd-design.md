# craft-ops — an opinionated DevOps skill suite (CI/CD first)

*Design spec — 2026-08-06*

## Purpose

`craft` encodes one opinionated methodology for writing application code, anchored by a
`PRINCIPLES.md` where every strict rule is stated with its *why*. This spec designs a **sibling
plugin, `craft-ops`**, that extends the same worldview into DevOps work: CI/CD, infrastructure as
code, deployment & release, and observability & incident response.

DevOps work is not a single linear pipeline the way feature development is, so `craft-ops` is a
**library of opinionated domain skills you reach for when that concern is in front of you** — not an
orchestrator. This spec takes the **CI/CD pipelines** domain all the way through; the other three
domains are named and stubbed now and built later.

## Non-goals

- No orchestrator skill (there is no single `dev-workflow`-style march for ops work).
- This build does **not** implement the IaC, deployment, or observability/incident skills — they are
  named stubs only.
- The `cicd-pipeline-design` skill does **not** write pipeline code or configurations. Authoring the
  pipeline definition is a separate, later skill (`pipeline-authoring`), name-stubbed here.
- No behavioral evals for these skills in this build (added when a domain has enough surface to guard).

## Overall shape

A new plugin that mirrors `craft`'s structure so the two read as one worldview, two plugins.

```
craft-ops/
  .claude-plugin/plugin.json        # name: craft-ops
  PRINCIPLES.md                     # the DevOps "why" — derives from & cites craft's principles
  README.md                         # suite overview + domain table (built vs. planned)
  CHANGELOG.md
  skills/
    cicd-pipeline-design/
      SKILL.md                      # the one skill built fully in this spec
      references/
        stage-ordering.md
        promotion.md
        reproducible-builds.md
```

The plugin registers in this repo's existing `.claude-plugin/marketplace.json` alongside `craft`, so
both install from one marketplace. `craft-ops` is **installable independently** — its principles
*cite* craft where they share a root, but it never hard-requires craft to be installed.

### Structural decisions (each with its *why*)

- **No orchestrator.** Ops concerns are reached for individually; forcing a linear pipeline would
  misrepresent the work. The suite is a library, not a march.
- **Independent installability drives independent config.** Because `craft-ops` can be installed
  without `craft`, it uses its **own** conventions file, `.craft-ops.yml`, rather than extending
  `craft`'s `.craft.yml`. `.craft-ops.yml` is self-contained (its own `git.main_branch`, `stack`,
  etc.). If a `.craft.yml` happens to exist, ops skills *may* read shared keys from it as a
  convenience, but never depend on it.
- **Philosophy derives from craft and cites it.** One coherent worldview; each ops principle names
  the craft root it extends.
- **Naming mirrors craft's design skills.** The skill is `cicd-pipeline-design`, matching
  `architecture-design` and `frontend-design`, so the name itself signals it *designs* the pipeline
  rather than implementing it.

## `craft-ops/PRINCIPLES.md`

The philosophy layer. Each CI/CD principle extends a craft root into ops and cites it. Final wording
is refined during implementation; the intent is fixed here.

1. **Build once, promote the same artifact.** Never rebuild per environment; a single immutable
   artifact, identified by a content/commit digest, moves across environments unchanged.
   *(craft: immutability by default → immutable artifacts.)*
2. **The pipeline is code, versioned with what it ships.** No clicked-together jobs; the pipeline is
   reviewed like any other code and lives with the app it builds.
3. **Fast feedback, fail early.** Cheapest and most-likely-to-fail stages run first; a broken main is
   a stop-the-line event. *(craft: tests come first, and they are a ratchet.)*
4. **Reproducible, hermetic builds.** Same input → same artifact; pinned toolchains, isolated and
   ephemeral build environments, no network-dependent build steps.
5. **Deploy is not release.** Decouple shipping the bits from exposing the behavior; roll forward and
   back cheaply. *(previews the deployment & release domain.)*
6. **Config and secrets enter from the environment, never the artifact or repo.** One artifact, many
   environments. *(craft: the domain is independent of how data enters or leaves.)*
7. **Done rests on evidence from the real target.** A deploy is "done" when observed healthy in the
   environment, not when the job turns green. *(craft: judgment is independent, and "done" rests on
   evidence.)*
8. **State the why; keep the escape hatch.** Inherited verbatim from craft — every strict rule is
   legible because it comes with its reason, and a conscious, recorded note is the sanctioned way to
   depart from one.

The IaC, deployment & release, and observability & incident-response domains appear here now as
**honest one-line stub headers** ("expanded when that domain is built"), so the document is coherent
about the full suite while being truthful about current scope.

## The `cicd-pipeline-design` skill

Mirrors craft's `architecture-design`: a **thinking / decision** skill, not a doer. It designs or
reviews a CI/CD pipeline against the opinionated conventions and produces a short design note. It does
**not** write pipeline code or configurations — that is the future `pipeline-authoring` skill, which
would itself run through craft's TDD-gated pipeline because it produces real code.

### Triggers

Setting up CI/CD for a repo; adding or reordering pipeline stages; reviewing an existing pipeline
against the conventions; deciding how an artifact is built, gated, and promoted across environments.

### What it decides (the opinionated checklist)

- **Artifact strategy.** What the single immutable artifact is (image, package, bundle), where it is
  stored, and how it is identified (content/commit digest). *Build once.*
- **Stage ordering for fast feedback.** Cheapest, most-likely-to-fail stages first
  (lint/format → unit → build artifact → integration/acceptance → deploy). Fail early.
- **The gate map.** Which stages are hard automated gates vs. human promotion gates, and where the
  "green main is sacred" stop-the-line rule applies.
- **Promotion flow.** How the *same* artifact moves dev → staging → prod without rebuild; what changes
  between environments (config and secrets from the environment only).
- **Reproducibility seams.** Pinned toolchain, hermetic and ephemeral build environment, no
  network-dependent build steps.
- **Secrets & config boundary.** Confirms nothing secret lives in the pipeline definition or the
  artifact; injected at deploy.
- **Evidence of done.** What signal proves a deploy is healthy in the target (smoke check / health
  probe), not merely a green job.

### Output

A short pipeline design note saved where the work lives (e.g.
`docs/craft-ops/pipelines/YYYY-MM-DD-<name>.md`): the artifact / stage / gate / promotion decisions
with their *why*, enough to then implement the actual pipeline through the future authoring skill.

### Guardrails (mirrors craft's design skills)

- Design only what the situation demands — YAGNI on stages and environments.
- Do not write the pipeline code or configurations here.
- Prefer the existing shape — if a pipeline already fits the conventions, the note is short.

### references/

The SKILL.md cites deeper convention docs rather than restating them, matching how `code-style`
splits into reference files:

- `stage-ordering.md` — fast-feedback ordering and the fail-early rationale.
- `promotion.md` — build-once/promote-the-same-artifact flow across environments.
- `reproducible-builds.md` — hermetic, pinned, ephemeral build environments.

## Scope of this build

**Delivered:**
- `craft-ops` plugin scaffolding: `plugin.json`, `README.md`, `CHANGELOG.md`, and a marketplace entry
  alongside `craft`.
- `PRINCIPLES.md` — the CI/CD-anchored principles fully written; the other three domains as honest
  one-line stubs.
- The `cicd-pipeline-design` skill: `SKILL.md` plus its three `references/` convention docs.
- README domain table listing all four domains and the future `pipeline-authoring` skill, marking
  what is built vs. planned.

**Deferred (named, not built):** the IaC, deployment/release, and observability/incident skills; the
`pipeline-authoring` skill; a `project-conventions`-equivalent skill that formalizes `.craft-ops.yml`
(for now `.craft-ops.yml` is documented within the `cicd-pipeline-design` references); behavioral
evals for these skills.

## Success criteria

- The `craft-ops` plugin installs from this repo's marketplace independently of `craft`.
- `PRINCIPLES.md` states the CI/CD principles, each citing the craft root it extends, with the other
  three domains present as truthful stubs.
- The `cicd-pipeline-design` skill triggers on the described situations and, run against a repo,
  produces a design note covering artifact / stage-ordering / gates / promotion / reproducibility /
  secrets / evidence — and never writes pipeline code or configurations.
- README accurately marks built vs. planned across all four domains and the authoring skill.
