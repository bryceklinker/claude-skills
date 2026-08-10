# craft-ops

A sibling to [`craft`](../README.md): a library of opinionated DevOps skills, not a
pipeline. There is no orchestrator here — reach for the skill whose domain concern
is in front of you (CI/CD, Infrastructure as Code, and Deployment & release today;
observability as the suite grows) and it produces a short, principled design note
for that concern.

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
| CI/CD pipelines | `pipeline-authoring` | Built |
| Infrastructure as Code | `infrastructure-design` | Built |
| Infrastructure as Code | `infrastructure-authoring` | Built |
| Deployment & release | `deployment-design` | Built |
| Deployment & release | `deployment-authoring` | Built |
| Observability & incident response | `observability-design` | Built |
| Observability & incident response | `incident-response` | Built |
| Observability & incident response | `observability-authoring` (writes the instrumentation/dashboards/alerts) | Planned |

`cicd-pipeline-design` decides the shape of a pipeline before anything is wired:
artifact strategy, stage ordering for fast feedback, the gate map, promotion flow,
reproducibility seams, the secrets/config boundary, and the evidence that proves a
deploy is actually done — each decision tied back to a principle. It is deliberately
a *thinking* skill: it produces a design note, never the pipeline code or
configuration itself. That authoring step is handed off to the
`pipeline-authoring` skill, behind its own review.

`infrastructure-design` decides the shape of infrastructure before anything is
provisioned — or reviews infrastructure code already in place: resource tiering
(disposable versus durable), module boundaries, environment parity through
inputs, the state backend, drift handling, and the least-privilege boundary for
apply-time credentials — each decision tied back to a principle. It is
deliberately a *thinking* skill: it produces a design note, never the
infrastructure code or configuration itself. That authoring step is handed off to
the `infrastructure-authoring` skill, behind its own review.

`observability-design` decides what a service reveals before you need it: SLOs
and error budget, symptom-based alerting, the signals to emit, the runtime
levers that ramp detail up and down without a redeploy, and the health signals
`deployment-design`'s gates and rollback decisions consume — each decision
tied back to a principle. `incident-response` drives the live response itself:
declare and assign roles early, mitigate before you diagnose with the
reversible levers `deployment-design` and `observability-design` already
built, diagnose with method (deferring root-cause mechanics to craft's
`systematic-debugging`), verify resolution on the real signal, and close with
a blameless postmortem that ratchets — a tracked action item and a new test or
alert every time.

## Agents

Two agents dispatch the design and authoring skills above as a team, mirroring
how `craft` splits planning from implementation. Authoring skills are named
generically and defer the production loop to `craft` — they degrade
gracefully when `craft` isn't installed, falling back to running the
discipline directly rather than failing outright.

- **`craft-ops-designer`** — runs the matching `-design` skill
  (`cicd-pipeline-design`, `infrastructure-design`, `deployment-design`, or
  `observability-design`) for a given domain and writes the resulting design
  note. It is read-only over the target system: no pipeline code, IaC,
  rollout automation, or instrumentation comes out of it.
- **`craft-ops-author`** — turns a design note into the real code or config,
  in its own worktree, under `craft`'s production discipline: non-trivial
  step logic is extracted into script files and driven through
  `strict-tdd`, the declarative glue is proven by `verification`, and both
  are reviewed and checked the way `craft`'s reviewer and verifier already do.

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
`craft`'s conventions file or its schema. The craft-ops design skills —
`cicd-pipeline-design` and `infrastructure-design` — read `.craft-ops.yml`, when
present, for a repo's build/test commands and target environments.
