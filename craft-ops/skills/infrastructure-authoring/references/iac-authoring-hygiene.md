# IaC Authoring Hygiene — infrastructure that doesn't drift

Infrastructure-as-code looks like ordinary source until you notice how differently it behaves: the same file that fails a lint check today can still `apply` cleanly, and the resource block nobody dared touch is often the one silently diverging from what's on disk. Hygiene here isn't cosmetic — it's the set of structural habits that keep the applied world matching the committed definition, and keep a durable resource from ever depending on the lifecycle of something meant to be thrown away. This document makes the domain rules from the skill's `SKILL.md` concrete, each with the failure it exists to prevent.

## Table of contents
- Prefer small composable modules over duplicated resource blocks
- Never co-locate a durable resource inside a compute unit
- Protect durable resources with lifecycle guards
- Remote, locked state — no secrets in code or state
- Pin every provider and module version
- Idempotent and convergent: apply-twice is a no-op
- No manual drift — import, don't console-tweak

## Prefer small composable modules over duplicated resource blocks

**When the same shape of resource is needed more than once — across environments, services, or regions — extract it into a small, composable module with explicit inputs and outputs, and parameterize the differences. Never copy-paste a resource block and hand-edit the copy.**

A copy-pasted block looks identical to its sibling at the moment it's created and starts drifting the instant either one is edited without the other. Someone fixes a security-group rule in staging and forgets prod has its own copy; someone adds a tag convention to the new environment's block that never makes it back to the old one. Six months later the environments that were supposed to be "the same infrastructure, different inputs" are quietly different infrastructure, and nobody can say without a diff-by-hand exactly where they've diverged. A module fixed once is fixed everywhere it's instantiated; a duplicated block fixed once is fixed in exactly the one place someone happened to be looking — which is the same failure mode DRY prevents in application code, except here the blast radius is a live environment instead of a function. This is the structural precondition for everything else in this document: hygiene rules applied inconsistently across N copies of a resource are not hygiene, they're a promise that's already been broken in at least one copy.

## Never co-locate a durable resource inside a compute unit

**Durable resources — a database, an object store, a queue, a topic, a message bus, anything holding state or data that must outlive a single deploy — are defined in their own composable unit, with their own lifecycle. A compute unit — an instance, a container, a function, a cluster, an autoscaling group — never creates a durable resource inside its own module or stack. It receives a reference to one instead: an ID, an ARN, an endpoint, passed in as an input.**

Compute is disposable by design — it gets destroyed and replaced on every deploy, rescaled up and down with load, torn down and rebuilt when the underlying image or instance type changes. That churn is normal and desired for compute. It is not survivable for a durable resource: if the database is defined inside the same module as the container that happens to use it, then the routine, expected, entirely-by-design destruction of the compute unit takes the data down with it, because to the tool driving the apply they're the same unit with the same lifecycle. Splitting them is what lets compute churn as aggressively as it needs to while the data sits completely outside the blast radius. This is the structural companion to "protect durable resources" below and to "review the plan before every apply": those two rules are safety nets that catch a durable resource on its way to being destroyed, but this rule is what keeps that resource out of the position where a routine compute change could ever put it there in the first place. A lifecycle guard on a resource that shouldn't be in that module to begin with is a second line of defense standing in for a first line that was never built.

## Protect durable resources with lifecycle guards

**Every durable resource carries an explicit lifecycle guard — deletion protection, replacement protection, `prevent_destroy` or whatever the tool's equivalent is — and a change to a durable resource is migrated in place, never torn down and recreated to get there.**

Most resource changes are safe to resolve by destroy-and-recreate: the tool sees a diff it can't reconcile in place, so it deletes the old one and stands up a new one, and for a stateless compute unit that's invisible. For a durable resource, destroy-and-recreate is data loss dressed up as a routine apply — the replacement resource is empty, and whatever the original held is gone the moment the plan that proposed it gets approved. A lifecycle guard turns that failure mode from "possible if someone isn't paying close enough attention to the plan" into "blocked by the tool itself, regardless of who's reviewing." It's a second, independent check behind the human reading the plan — not a substitute for review, but insurance for the moment review is rushed or the destroy/replace is buried in a large diff.

## Remote, locked state — no secrets in code or state

**State lives in a remote backend with locking, never on a local disk. Nothing secret — credentials, tokens, connection strings — is ever written into the IaC source, and nothing secret is allowed to land unencrypted in the state file either; secrets are injected at apply time from a secret manager, not authored into either place.**

Local state is a single point of failure and a coordination hazard at once: it lives on one machine, it's invisible to everyone else who might need to apply next, and two people applying against their own local copies at the same time will silently clobber each other's view of reality. A remote, locked backend fixes both problems — it's the one shared source of truth, and the lock makes concurrent applies queue instead of race. The secrets half is a separate risk that state makes easy to underestimate: state files routinely contain the *resolved* values of anything passed into a resource, including secrets that never appear in the source at all — a database password set via a variable shows up in plaintext in the state's resource attributes even if the `.tf`/`.yaml`/whatever never mentions it directly. Treating "no secrets in code" as sufficient and ignoring state is how a secret ends up exposed to everyone with read access to the backend anyway. Injection from a secret manager at apply time is what keeps the secret out of both places at once.

## Pin every provider and module version

**Every provider and every module the IaC depends on is pinned to an exact or narrowly-constrained version — never left to float to "whatever's newest" at apply time.**

An unpinned provider or module is a hidden input to the apply that can change between two runs of the exact same source with no corresponding commit, diff, or review to explain it. When a provider ships a breaking change or a module's new minor version alters a default, an unpinned dependency means the infrastructure someone applies today is not the infrastructure the source describes — it's that source plus whatever shifted underneath it since the last apply. Pinning turns every dependency into something a `git blame` and a changelog can actually explain, and turns an unexpected plan into a signal worth investigating rather than background noise.

## Idempotent and convergent: apply-twice is a no-op

**Applying the same IaC twice in a row, with nothing else having changed, produces no changes on the second run. If a re-apply against an unmodified source keeps proposing a diff, the definition itself is broken — it isn't converging on a stable, described state.**

Convergence is what makes an apply trustworthy as a routine operation instead of a one-shot gamble: a definition that converges can be re-applied after a transient failure, a partial run, or just to confirm nothing's drifted, and the worst case is "no-op." A definition that doesn't converge — because a value is computed differently each run, an ordering isn't deterministic, or a resource's provider doesn't faithfully report its own state — turns every re-apply into a coin flip about whether it'll try to change something that shouldn't change. Idempotence is the property that lets "just apply it again" stay a safe answer.

## No manual drift — import, don't console-tweak

**Every change to managed infrastructure goes through the IaC and an apply. A resource is never hand-edited in a provider's console, CLI, or API to "just fix it quickly" — if a resource exists that the IaC doesn't yet manage, it's brought under management with an import, not left as an out-of-band exception.**

A console tweak is invisible to everything that makes the applied state trustworthy: it isn't in source, isn't reviewed, isn't in the history that explains why the infrastructure looks the way it does, and — critically — it's exactly the kind of change the next `plan` will either silently overwrite or flag as drift nobody remembers authorizing. Once one resource has a hand-made exception, every future plan for that resource carries an extra question that pure declarative infrastructure was supposed to eliminate: does this diff represent an intended change, or is it the tool trying to undo someone's manual fix? Importing the resource instead keeps the IaC the single source of truth it's meant to be, and keeps every subsequent plan legible.
