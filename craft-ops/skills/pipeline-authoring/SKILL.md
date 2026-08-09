---
name: pipeline-authoring
description: "Use when turning a CI/CD pipeline design note (from cicd-pipeline-design) into the actual pipeline definition — writing the real pipeline-as-code and its step scripts. Applies opinionated authoring rules: prefer script files over inline scripts, build once and promote the same artifact, pinned/hermetic/idempotent steps, no secrets in the definition, DRY across stages, fail-fast ordering. It WRITES the pipeline (unlike cicd-pipeline-design, which only designs it), but defers the production loop to craft: extracted logic (scripts/generators) is built under strict-tdd, and the declarative pipeline glue is proven by verification — running the real pipeline against a test artifact. Not for deciding the pipeline's shape (that is cicd-pipeline-design), nor for infrastructure, deployment, or observability authoring."
---

# Pipeline Authoring — write the pipeline the design already decided

## Why this exists

A design note is not a running pipeline. Left to guesswork, the gap between the two fills in with inline shell scripts nobody can unit test, stages that quietly diverge from what was decided, and a definition that's never actually reviewed like code. This skill turns a `cicd-pipeline-design` note into real, reviewed pipeline-as-code — without re-litigating the design and without hand-waving the discipline that makes the result trustworthy.

Unlike the `-design` skills, it *does* write code — so it leans on craft to write it well.

## Seams

- **Consumes** the `cicd-pipeline-design` note as input. That note already made the shape decisions — artifact strategy, stage ordering, gate map, promotion flow, reproducibility seams, secrets boundary, evidence of done. This skill does not re-decide them.
- **Defers the production loop to craft** — named generically so this skill degrades gracefully without craft installed: `strict-tdd` for the extracted logic, `verification` for the pipeline glue, `code-style` and `self-review` for how it's written and checked.
- **Review and verification** go to `craft-reviewer` / `craft-verifier` where those agents exist.

## The production-discipline split

State it plainly, because the two halves are proven differently:

- **Extracted real logic** — scripts, generators, policy code, anything with a decision or a computation in it — is production code. It goes through craft `strict-tdd`: a failing test first, then the minimal code to pass it.
- **The declarative pipeline glue** — the stage/job wiring itself — isn't unit-testable in the same sense. It's proven by craft `verification`: run the real pipeline against a test artifact and observe the outcome, not by reasoning about the YAML.

This skill's job is to maximize how much lands on the testable side of that split. Every non-trivial decision pushed out of the glue and into a script is more of the pipeline covered by strict-tdd instead of resting on "it looked right."

## Domain rules

**Prefer script files over inline scripts.** Non-trivial step bodies live in version-controlled script files that the pipeline calls — never as inline shell/YAML blocks buried in the step definition. Inline scripts can't be unit tested, can't be linted with the rest of the codebase, and hide logic from `git diff` and code review. If a step body branches, loops, parses output, or makes more than a one-line decision, it belongs in a script. See `references/pipeline-as-code-hygiene.md`.

Beyond that:

- **Build once, promote the same artifact.** The pipeline produces one immutable artifact and moves it unchanged across environments; it never rebuilds per environment.
- **Pinned, hermetic, idempotent.** Toolchain and dependency versions are pinned, builds run in isolated environments, and re-running a step is always safe and yields the same result.
- **No secrets in the definition.** Nothing secret is ever written into the pipeline file or baked into the artifact — secrets and environment config are injected at run time.
- **DRY across stages.** Repeated step logic is factored into a shared script or template, not copy-pasted per stage — copy-paste drift is how one stage silently diverges from the others.
- **Fail-fast ordering matching the design.** Stages run in the order the design note settled on — cheapest and most-likely-to-fail first. If the pipeline being authored doesn't match that order, the design note is wrong or stale, not the authoring.
- **Reviewed like code.** The pipeline definition and its scripts go through the same review the application code does — no clicked-together jobs, no changes that bypass PR review.

Testing and verifying depth — what counts as adequate coverage for extracted logic, and how to structure a verification run for the glue — is in `references/testing-and-verifying-pipelines.md`.

## Guardrails

- **Do not re-decide the design.** If the design note is missing, ambiguous, or looks wrong, stop and send it back to `cicd-pipeline-design` rather than deciding the shape here.
- **Do not reimplement TDD or verification.** Defer to craft's `strict-tdd` and `verification`; this skill supplies the domain rules, not a competing test methodology.
- **Don't inline non-trivial step logic.** If a step body is growing past a couple of straight-line commands, extract it to a script before it grows further.
- **No secrets in the definition, ever** — not as a placeholder, not "just for now."

## Exit condition

The pipeline definition and its extracted step scripts exist in the repo. The extracted logic is covered by tests written under strict-tdd; the declarative glue has been verified by running the real pipeline against a test artifact and observing the result. Both are committed the craft way — reviewed, no secrets, no dead scaffolding left behind.
