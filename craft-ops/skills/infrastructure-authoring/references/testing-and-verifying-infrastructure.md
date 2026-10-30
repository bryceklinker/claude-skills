# Testing and Verifying Infrastructure

Infrastructure is tested by the tool that applies it, against a target you can throw away. A resource block's only behavior is what it causes the provider to do; a test that mocks the provider restates the definition and passes even when the real apply would fail.

## 1. `validate` and `plan` — always runnable

They need only the tool and the source. `validate` catches broken references, missing arguments, and type errors; `plan` shows exactly what would change against real state. Then read the plan. The first thing to look for is a durable resource marked for destroy or replace — often a sign it ended up inside a compute unit's lifecycle (`iac-authoring-hygiene.md`). An exit code of zero is not a reviewed plan.

## 2. Apply to a sandbox and observe convergence

Apply to a scratch workspace, disposable account, or non-production target shaped enough like production to trust. Record the apply output and confirm the resources exist with the arguments the definition specified. Then **plan again**: no changes means it converged and re-applies are safe. A module never applied anywhere is an assumption.

## 3. Review before every apply

Every plan is read by a person or a reviewing agent before its apply runs, with no exception for changes that look obviously safe. A destroy/replace on stateless compute is routine; the same on a database, store, queue, or bus is the line review exists to catch.

## Policy and computed logic

Policy-as-code is proven by running the policy tool against a plan that should pass and one that should fail. Module logic with real edge cases — a CIDR derived from an index, a name generated under a provider's length limit — can earn a small test with the IaC tool's own test runner (`terraform test`, Pulumi's unit tests) where it has one. Most modules just pass values through and need nothing beyond the plan and the apply.
