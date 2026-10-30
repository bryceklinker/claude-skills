---
name: infrastructure-authoring
description: "Use when turning an infrastructure design note (from infrastructure-design) into the actual infrastructure-as-code — real Terraform/Pulumi/CloudFormation/CDK and any policy or module logic. Opinionated rules: small composable modules over duplicated blocks; NEVER co-locate a durable resource inside a compute unit (compute receives durable resources by input); network foundation first; durable resources in their own segment; lifecycle guards on durable resources; read the plan before every apply; remote/locked state, no secrets in code or state; pinned providers; idempotent and drift-free. It WRITES the IaC and proves it by running it: validate and plan, read the plan, apply to a sandbox, confirm a second plan is empty — no unit-test suite for resource definitions. Not for deciding the infrastructure's shape (infrastructure-design), nor pipeline, deployment, or observability authoring."
---

# Infrastructure Authoring

Turn an `infrastructure-design` note into real IaC without re-deciding the design. Read `cloud.iac_tool` and `cloud.iac_commands` from `.craft-ops.yml` first (`craft-ops-conventions`). If the note is missing, ambiguous, or wrong, send it back to `infrastructure-design`.

## Prove it by running it

Infrastructure is tested by the tool that applies it (`PRINCIPLES.md` core 2):

1. **`validate`, then `plan`** — always runnable, even with nowhere to apply. Then read the plan: the first check is whether it destroys or replaces a durable resource. A green plan is not a reviewed plan.
2. **Apply to a sandbox or throwaway environment** and observe the result: the resources exist with the arguments the definition specified.
3. **Plan again** — it should show no changes. That proves convergence and idempotence.

Don't unit-test resource blocks; a test that mocks the provider only restates the definition. Policy-as-code is proven by running the policy tool against a plan that should pass and one that should fail. A module with genuinely complex computed logic (CIDR derivation, name generation under length limits) can earn a small test with the IaC tool's own test runner where it has one. `references/testing-and-verifying-infrastructure.md` has the detail.

## Domain rules

- **Never co-locate a durable resource in a compute unit.** Databases, object stores, queues, topics, and buses live in their own unit; compute receives their IDs, ARNs, or endpoints as inputs. Compute is replaced routinely, and anything defined alongside it goes down with it.
- **Network foundation first.** The VPC/VNet, subnets, routing, and base security groups are their own unit, applied before anything attaches to them and handed down by reference.
- **Durable resources in their own network segment**, reachable by default only from the compute network; every other path (bastion, migration or backup runner) named and justified.
- **Protect durable resources** with deletion/replacement guards; migrate them, never tear down and recreate.
- **Read the plan before every apply.**
- **Remote, locked state; no secrets in code or state.**
- **Pinned providers and modules.**
- **Small composable modules over duplicated blocks** — but no module for something used once.
- **Idempotent, no drift.**

The rule rationale and examples: `references/iac-authoring-hygiene.md`.

## Writing it well

Apply craft-code's `code-style` where it applies, commit each unit once it has applied and converged, commit refactors separately, and send the finished diff to `adversarial-review` and `verification` (`craft-code-reviewer` / `craft-code-verifier` where available). Without craft-code installed, apply the same discipline directly.

## Exit condition

The IaC is in the repo; it validated, its plan was read, it applied to a sandbox (or, with no target, validated and planned), and a second plan showed no changes. Durable and compute resources live in separate units; reviewed, no secrets, pinned providers, no leftover scaffolding.
