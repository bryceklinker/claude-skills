# craft-ops behavioral eval sets

Curated eval sets for the `craft-ops` design skills, run through the
`skill-creator` behavioral-eval loop (draft prompts → run with-skill vs.
baseline → grade assertions → benchmark). Unlike the transient
`craft-ops-workspace/` scratch (gitignored), these prompt sets are committed
so a skill's discriminating tests survive between iterations and can gate a
regression after any edit.

## The one rule: assertions must be able to fail on a strong baseline

These are *thinking/decision* skills, and a capable model already produces a
lot of correct deployment/CI/CD/IaC content unprompted. An assertion that a
good baseline passes anyway measures general competence, not the skill's
lift. Every prompt here records the **dimension it discriminates on** and why
a baseline plausibly fails it. Three dimensions have held up as real
discriminators for `deployment-design`:

- **Completeness** — a whole-rollout ask has every checklist area in play;
  baselines quietly drop the low-salience ones (roll-forward criteria,
  in-flight state, an explicit ownership model, a synthesized
  evidence-of-done, a new dependency's capacity/failure-mode).
- **Scope-down** — a narrow ask tempts a baseline to over-deliver (tooling
  surveys, a full rollout redesign, pseudocode). The skill's harder half is
  going deep only where asked and one-lining the rest.
- **Discipline on a deceptively-simple change** — a change that *looks*
  trivial (a config/timeout/flag flip) tempts "just ship it." The skill
  should force a real release plan — risk, gate, rollback, evidence-of-done —
  without over-building for a one-liner.

A prompt where with-skill and baseline both score 100% (as an
expand-contract schema-migration prompt did — textbook knowledge a strong
model emits unprompted) is **not** a useful eval; it was replaced here by the
timeout-bump prompt, which exercises the discipline dimension instead.

## Running a set

Use `skill-creator` (see its SKILL.md). For each prompt, spawn a with-skill
run and a baseline run (no-skill, or a snapshot of the prior skill version
when measuring a specific edit), grade each output against the prompt's
assertions, then aggregate. Keep the eval set updated as the skill's edges
move — a passing grade on a non-discriminating assertion is false
confidence.

## Sets

| File | Skill | Prompts | Discriminates on |
|------|-------|---------|------------------|
| `deployment-design.json` | `craft-ops/skills/deployment-design` | 3 | completeness, scope-down, discipline-on-simple-change |
| `observability-design.json` | `craft-ops/skills/observability-design` | 3 | completeness, runtime levers, health-signals-for-deployment |
| `incident-response.json` | `craft-ops/skills/incident-response` | 3 | mitigate-before-diagnose, the ratchet, doctrine |

Measured lift (iteration-1, with-skill vs no-skill baseline, sonnet): deployment-design +0.23,
observability-design +0.21, incident-response +0.39. incident-response shows the largest lift in
the suite because its two core moves — mitigate before you diagnose, and a postmortem that mandates
a new test/alert — genuinely run counter to a capable baseline's instinct (investigate first; write
a narrative with optional follow-ups).
