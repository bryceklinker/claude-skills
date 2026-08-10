---
name: infrastructure-authoring
description: "Use when turning an infrastructure design note (from infrastructure-design) into the actual infrastructure-as-code — writing the real IaC (Terraform/Pulumi/CloudFormation/CDK/etc.) and any policy or module logic. Applies opinionated authoring rules: prefer small composable modules over duplicated resource blocks; NEVER co-locate a durable resource inside a compute unit (compute references durable resources by input, never creates them); protect durable resources with lifecycle guards; review the plan before every apply; remote/locked state with no secrets in code or state; pinned providers; idempotent and drift-free. It WRITES the IaC (unlike infrastructure-design, which only designs it), but defers the production loop to craft: policy/module logic is built under strict-tdd, and the declarative resources are proven by verification — validate/plan and apply against a sandbox. Not for deciding the infrastructure's shape (that is infrastructure-design), nor for pipeline, deployment, or observability authoring."
---

# Infrastructure Authoring — write the infrastructure the design already decided

## Why this exists

A design note is not applied infrastructure. Left to guesswork, the gap between the two fills in with duplicated resource blocks copy-pasted across environments, durable resources wired directly into the compute unit that happens to need them, and applies that go out without anyone reading the plan. This skill turns an `infrastructure-design` note into real, reviewed infrastructure-as-code — without re-deciding the design and without hand-waving the discipline that makes the result trustworthy.

Unlike the `-design` skills, it *does* write code — so it leans on craft to write it well.

## Seams

- **Consumes** the `infrastructure-design` note as input. That note already made the shape decisions — resource tiers, module boundaries, state strategy. This skill does not re-decide them.
- **Defers the production loop to craft** — named generically so this skill degrades gracefully without craft installed: `strict-tdd` for policy and module logic, `verification` for the declarative resources, `code-style` and `self-review` for how it's written and checked.
- **Review and verification** go to `craft-reviewer` / `craft-verifier` where those agents exist.

## The production-discipline split

State it plainly, because the two halves are proven differently:

- **Policy/module logic** — policy-as-code, modules with computed values, generators, anything with scripting or a decision in it — is production code. It goes through craft `strict-tdd`: a failing test first, then the minimal code to pass it.
- **The declarative resources** — the resource blocks and their wiring — aren't unit-testable in the same sense. They're proven by craft `verification`: `validate` + `plan`/`diff`, reviewed, then applied against a throwaway or sandbox environment. At minimum, even when no apply target is available, **`validate` + `plan` is the always-runnable minimum verification** — it catches broken references, type errors, and unexpected destroy/replace offline, before any apply. The plan is a diff you must READ, not a step you rubber-stamp.

This skill's job is to maximize how much lands on the testable side of that split. Every computed value or decision pushed out of the declarative resources and into a module or policy script is more of the infrastructure covered by strict-tdd instead of resting on "the plan looked fine."

## Domain rules

**Prefer small composable modules over duplicated resource blocks.** A resource block copy-pasted across environments or services drifts the moment one copy gets an edit the others don't. Small, composable modules with clear inputs/outputs keep the duplication in one reviewable place. See `references/iac-authoring-hygiene.md`.

**Never co-locate a durable resource inside a compute unit.** Durable resources — a database, object store, queue, topic, or bus — live in their own composable unit, never defined inside the module or stack for an instance, container, function, cluster, or ASG. Compute units receive references to durable resources — IDs, ARNs, endpoints — as inputs; they never create them. Compute is disposable: it gets destroyed, replaced, and rescaled routinely, and a durable resource defined alongside it goes down whenever the compute unit does. Splitting them into separate units is what lets compute churn without ever threatening the data.

Beyond those two:

- **Protect durable resources.** Lifecycle guards (deletion/replacement protection, `prevent_destroy` or equivalent) on every durable resource; changes to a durable resource are migrated, never torn down and recreated.
- **Review the plan before every apply.** No apply goes out on trust — the diff is read by a human or reviewer, every time. This is what catches a durable resource marked for destroy/replace, or a durable resource that snuck into a compute unit's lifecycle.
- **Remote, locked state — no secrets in code or state.** State lives in a remote backend with locking; nothing secret is ever committed to the IaC or allowed to land unencrypted in state.
- **Pinned providers.** Provider and module versions are pinned, not left floating, so an apply today produces the same result as an apply next month.
- **Idempotent, no drift.** Re-running an apply with no intervening change is a no-op; manual out-of-band changes are not how this infrastructure gets modified.

Testing/verifying depth is in `references/testing-and-verifying-infrastructure.md`.

## Guardrails

- **Do not re-decide the design.** If the design note is missing, ambiguous, or looks wrong, stop and send it back to `infrastructure-design` rather than deciding the shape here.
- **Do not reimplement TDD or verification.** Defer to craft's `strict-tdd` and `verification`; this skill supplies the domain rules, not a competing test methodology.
- **Never co-locate a durable resource in a compute unit** — not "just this once," not "it's a small instance."
- **No secrets in code or state, ever.**
- **Review the plan before every apply** — no exceptions for "obviously safe" changes.

## Exit condition

The IaC and any policy/module logic exist in the repo. The logic is covered by tests written under strict-tdd; the declarative resources are verified by `validate`/`plan` at minimum, and applied against a sandbox with the plan read before the apply. Durable resources and compute units live in separate composable units. All of it is committed the craft way — reviewed, no secrets, pinned providers, no dead scaffolding left behind.
