# craft-ops

A sibling to [`craft`](../README.md): a library of opinionated DevOps skills, not a
pipeline. There is no orchestrator here — reach for the skill whose domain concern
is in front of you (CI/CD today; infrastructure, deployment, and observability as
the suite grows) and it produces a short, principled design note for that concern.

## Installation (Claude Code)

`craft-ops` is distributed as a Claude Code plugin via the same marketplace as
`craft`, but it installs and runs **independently of `craft`** — you don't need
`craft` to use it.

```
/plugin marketplace add bryceklinker/claude-skills
/plugin install craft-ops@craft-marketplace
```

- The first command registers this repo's marketplace (`.claude-plugin/marketplace.json`) — skip it if you've already added it for `craft`.
- The second installs the `craft-ops` plugin on its own.

Verify the skill loaded with `/plugin` (it appears under the `craft-ops` plugin).

**Updating** to the latest version later:

```
/plugin marketplace update craft-marketplace
/plugin install craft-ops@craft-marketplace
```

See [`CHANGELOG.md`](CHANGELOG.md) for what changed between versions.

To install from a local checkout instead (for development), point the marketplace
at the repo path:

```
/plugin marketplace add /path/to/claude-skills
/plugin install craft-ops@craft-marketplace
```

## Domains and skills

| Domain | Skill | Status |
|--------|-------|--------|
| CI/CD pipelines | `cicd-pipeline-design` | Built |
| CI/CD pipelines | `pipeline-authoring` (writes the definition) | Planned |
| Infrastructure as Code | — | Planned |
| Deployment & release | — | Planned |
| Observability & incident response | — | Planned |

`cicd-pipeline-design` decides the shape of a pipeline before anything is wired:
artifact strategy, stage ordering for fast feedback, the gate map, promotion flow,
reproducibility seams, the secrets/config boundary, and the evidence that proves a
deploy is actually done — each decision tied back to a principle. It is deliberately
a *thinking* skill: it produces a design note, never the pipeline code or
configuration itself. That authoring step is left to the future
`pipeline-authoring` skill, behind its own review.

## Design philosophy

The suite's rationale lives in [`PRINCIPLES.md`](PRINCIPLES.md) — the canonical
statement of the principles each skill cites instead of restating. It derives from
and cites `craft`'s own `PRINCIPLES.md`, extending that methodology (immutability,
evidence over inspection, fast feedback, the stated *why* with its escape hatch)
from application code into the systems that build, ship, and run it — while
standing on its own, so `craft-ops` never requires `craft` to be installed.

## Conventions

`craft-ops` reads its own `.craft-ops.yml` — never `craft`'s `.craft.yml`. This
keeps the plugin installable and usable on its own, without any dependency on
`craft`'s conventions file or its schema. `cicd-pipeline-design` reads
`.craft-ops.yml`, when present, for a repo's build/test commands and target
environments.
