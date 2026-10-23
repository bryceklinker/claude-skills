---
name: pipeline-authoring
description: "Use when turning a CI/CD pipeline design note (from cicd-pipeline-design) into the actual pipeline definition — writing the real pipeline-as-code and its step scripts. Applies opinionated authoring rules: script files over inline scripts, build once and promote the same artifact, pinned/hermetic/idempotent steps, no secrets in the definition, no duplicated stage logic, fail-fast ordering. It WRITES the pipeline (unlike cicd-pipeline-design, which only designs it) and proves it by running it: each step script executes through the exact entrypoint the pipeline calls and does its job, and the real pipeline runs against a test artifact — no separate unit-test suite for scripts unless one carries substantial decision logic. Not for deciding the pipeline's shape (that is cicd-pipeline-design), nor for infrastructure, deployment, or observability authoring."
---

# Pipeline Authoring

Turn a `cicd-pipeline-design` note into real pipeline-as-code without re-deciding the design. Read `cicd.*` and `environments.order` from `.craft-ops.yml` first (`craft-ops-conventions`). If the note is missing, ambiguous, or wrong, send it back to `cicd-pipeline-design`.

## Prove it by running it

A pipeline and its scripts are tested by executing them and watching them do the job (`PRINCIPLES.md` core 2):

- **Each step script** runs through the exact entrypoint the pipeline uses (`./ci/deploy.sh`, `python -m ci.promote`) against a real or throwaway target, and you observe the outcome — the artifact built and pushed with the expected digest, the version computed, the check failing when it should. Where a script would touch something real, run it against a scratch target or with its own `--dry-run`.
- **The pipeline itself** runs for real against a test artifact on a scratch branch or disposable tag: the stages ran in the designed order, a failing gate actually blocked promotion (make it fail and watch), and the artifact promoted is the one that was built.
- **When no runner is available**, the minimum is linting/validating the pipeline definition plus running every script locally through its entrypoint.

Don't write a unit-test suite for a script by default; it would mostly mock the CI system and registry the script drives. Add one only when a script holds real decision logic with more cases than running it covers cheaply — a version computation, a policy with many branches — and then build it with craft-code's `strict-tdd` where installed. `references/testing-and-verifying-pipelines.md` has the detail.

## Domain rules

- **Script files over inline scripts.** A step body that branches, loops, parses output, or makes more than a one-line decision lives in a version-controlled script the pipeline calls — runnable locally, lintable, and reviewable as a diff. Straight-line one-liners can stay inline. `references/pipeline-as-code-hygiene.md`.
- **Build once, promote the same artifact** — never rebuild per environment.
- **Pinned, hermetic, idempotent** steps; re-running one is safe.
- **No secrets in the definition**; inject them at run time.
- **No duplicated stage logic** — factor it into one script or template; don't build a templating layer for a single use.
- **Stages in the order the design decided.** If they can't be, the design is stale.
- **Only what the design calls for** — no extra stages, environments, or wrapper scripts.

## Writing it well

Apply craft-code's `code-style` to scripts, commit each piece once it's been run and seen working, commit refactors separately, and send the finished diff to `adversarial-review` and `verification` (`craft-code-reviewer` / `craft-code-verifier` where available). Without craft-code installed, apply the same discipline directly.

## Exit condition

The pipeline definition and its scripts are in the repo; every script has run through its real entrypoint and done its job; the pipeline has run against a test artifact (or, without a runner, been validated with every script run locally); reviewed, no secrets, no leftover scaffolding.
