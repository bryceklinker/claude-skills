# craft-ops — authoring skills + agent team (vertical slice 1)

*Design spec — 2026-08-09*

## Purpose

craft-ops has four `-design` skills (thinking skills that produce design notes) but nothing that
turns those notes into real code/config, and no agents to delegate the work to. This spec begins that
work as a **vertical slice**: one authoring skill end-to-end plus the two agents that leverage the
suite, so the whole chain — *design a note → author the code the craft way* — works and is testable
before the pattern is replicated to the other three domains.

**This slice (Spec 1) delivers:**
- `pipeline-authoring` — the first authoring skill (turns a `cicd-pipeline-design` note into the real
  pipeline definition).
- `craft-ops-designer` agent — dispatched to run any craft-ops `-design` skill and produce the note.
- `craft-ops-author` agent — dispatched to turn a design note into real code/config in its own
  worktree, using the authoring skill + craft's production discipline.

**Deferred to later slices (Spec 2+):** `infrastructure-authoring`, `deployment-authoring`,
`observability-authoring`. The `craft-ops-author` agent is written generically so each plugs in with
no agent change.

## Locked-in decisions (from brainstorming)

- **Authoring = domain guidance over craft's pipeline.** An authoring skill is a thin, opinionated
  layer that takes the matching design note as input and adds the domain-specific *how to write it
  well* rules, then **defers the production loop to craft** (`dev-workflow` / `strict-tdd` /
  `verification` / `code-style` / `self-review`). It reuses craft's discipline rather than
  duplicating it.
- **Graceful degradation on installability.** The `-design` skills remain fully standalone. The
  authoring skills *assume* the production discipline is available: they name it generically
  (test-first for logic, verification for glue, review the diff) and point to craft's skills as the
  canonical implementation — best with craft installed, still meaningful without it. This is a
  conscious, recorded softening of the "independently installable" invariant for the authoring layer
  only.
- **Two agents, no responder.** `craft-ops-designer` and `craft-ops-author` are delegatable,
  non-interactive, bounded tasks — the shape agents are good for. `incident-response` stays a
  main-thread, interactive, human-in-the-loop **skill** (a dispatched subagent has no hands on
  production and removes the interactivity an incident needs); the one delegatable slice of an
  incident — root-cause investigation — already belongs to craft's `craft-debugger`
  (`systematic-debugging`), which `incident-response` defers to.
- **No new orchestrator.** craft-ops stays a library; the author agent leans on craft's `dev-workflow`
  loop, and review/verify reuse craft's `craft-reviewer` / `craft-verifier`.
- **Vertical slicing**, folded into **PR #3**.

## The `pipeline-authoring` skill

An authoring skill: it *writes* the real pipeline definition (unlike the `-design` skills). It takes
the `cicd-pipeline-design` note as input, applies the domain rules below, and drives craft's
production discipline to produce the code.

### The production-discipline split (the core insight)

Pipeline definitions are largely *declarative glue that can't be unit-tested*. So the discipline
splits, and the skill's job is to maximize what falls on the testable side:

- **Real logic** it writes (scripts, generators, policy code) → craft **`strict-tdd`**: a failing
  test first, red→green→refactor, commit at green and after refactor.
- **The declarative glue** (the pipeline definition itself) → craft **`verification`**: run the real
  pipeline against a test artifact and observe it — evidence, not inspection.

### Domain rules (the *how to write it well*)

- **Prefer script files over inline scripts.** Any non-trivial step body lives in a
  version-controlled script the pipeline *calls*, never inline in the definition. Inline scripts are
  logic smuggled into glue: they bloat the pipeline file, can't be run or tested locally, and can't be
  reused across stages. Extraction is what turns that logic into the testable side of the split above.
- **Build once, promote the same artifact** — the definition never rebuilds per environment.
- **Pinned, hermetic, idempotent steps** — pinned tool versions, no network-dependent build steps,
  re-runnable without side effects.
- **No secrets in the definition** — injected from the environment at run time.
- **DRY across stages** — shared logic extracted (see the script-files rule), not copy-pasted between
  jobs.
- **Fail-fast ordering matching the design** — cheapest/most-likely-to-fail stages first, mirroring
  the design note's decisions.
- **The pipeline is reviewed like code** — it goes through the same review as any change.

### Boundary

- It *writes* the pipeline definition — that is the point of an authoring skill.
- It does **not** re-decide the design (defers upstream to `cicd-pipeline-design`).
- It does **not** reimplement TDD/verification/review — it defers to craft, naming the discipline
  generically so it degrades without craft.

### Input / output

- **Input:** a `cicd-pipeline-design` design note (artifact strategy, stages, gates, promotion,
  reproducibility, secrets boundary, evidence).
- **Output:** the actual pipeline definition files, the extracted step scripts, and the tests/checks
  that cover the extracted logic — produced under craft's discipline, committed the craft way.

### references/

- `pipeline-as-code-hygiene.md` — the domain rules above with their *why* (script-files-not-inline,
  pinned/hermetic/idempotent, no-secrets, DRY, build-once).
- `testing-and-verifying-pipelines.md` — the TDD-for-logic / verification-for-glue split made
  concrete: what to unit-test (extracted scripts/generators), how to verify the glue (run the real
  pipeline against a test artifact), and how to keep the untestable surface small.

## The agents

Both mirror craft's agent shape: YAML frontmatter (`name`, `description`, `tools`, `model`) plus a
body that invokes specific skills. They live in `craft-ops/agents/` (auto-discovered by the craft-ops
plugin).

### `craft-ops-designer`

- **Role:** given a request and which domain, invoke the matching craft-ops `-design` skill
  (`cicd-pipeline-design`, `infrastructure-design`, `deployment-design`, `observability-design`) and
  produce the design note. Nothing else.
- **Access:** read + write-the-note only — produces a note, never production code (mirrors
  `craft-architect`'s read-only-design stance). **Tools:** Read, Grep, Glob, Write, Skill.
  **Model:** opus (design judgment).
- Works for all four existing design skills today.

### `craft-ops-author`

- **Role:** given a design note, a domain, the exact files it may touch, and a worktree/branch,
  invoke the matching `-authoring` skill and produce the real code/config — driving craft's
  `strict-tdd` for extracted logic and `verification` for the declarative glue, applying `code-style`,
  committing at green and after refactor. Mirrors `craft-implementer`.
- **Access:** Read, Write, Edit, Bash, Grep, Glob, Skill. **Model:** opus.
- For this slice it is wired to `pipeline-authoring`; written generically so future authoring skills
  plug in with no change.
- **Reuses craft's team:** review/verify of its output go to craft's `craft-reviewer` /
  `craft-verifier` when craft is installed; named generically otherwise. Root-cause investigation of a
  defect goes to craft's `craft-debugger`.

## Scope of this build

**Delivered:** the `pipeline-authoring` skill + 2 references; the `craft-ops-designer` and
`craft-ops-author` agents in `craft-ops/agents/`; README updates (a new "Agents" section, the CI/CD
`pipeline-authoring` row flipped Planned→Built); CHANGELOG entry + version bump to `0.5.0`; folded
into PR #3.

**Deferred (named):** `infrastructure-authoring`, `deployment-authoring`, `observability-authoring`
(Spec 2+); a `.craft-ops.yml` conventions skill.

## Success criteria

- `pipeline-authoring` triggers when turning a CI/CD design note into a pipeline definition; it
  produces the pipeline plus extracted step scripts and their tests, applies the domain rules
  (script-files-not-inline, pinned/hermetic, no-secrets-in-definition, build-once), and defers the
  production loop to craft (naming the TDD-for-logic / verification-for-glue split) rather than
  re-deciding the design or reimplementing TDD.
- `craft-ops-designer` runs any of the four `-design` skills and produces a design note, writing no
  production code.
- `craft-ops-author` turns a design note into real code/config in its own worktree under craft's
  strict-tdd/verification/code-style, and is written generically enough to drive a future authoring
  skill without modification.
- README marks `pipeline-authoring` Built and documents the two agents; plugin at `0.5.0`; all folded
  into PR #3.

## Post-build validation (not a build task)

The `-design` skills are validated with the skill-creator behavioral eval loop. `pipeline-authoring`
writes code, so its validation is **behavioral**: dispatch `craft-ops-author` on a sample
`cicd-pipeline-design` note and confirm the produced pipeline honored the domain rules
(script-files-not-inline, no secrets in the definition, pinned versions, extracted logic covered by
tests, glue verified by running it). Treat this as a post-build step, like the eval loops.
