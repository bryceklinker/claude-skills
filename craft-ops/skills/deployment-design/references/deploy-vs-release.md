# Deploy vs Release — decoupling shipping the bits from exposing the behavior

A deploy and a release are commonly conflated because the same action often triggers both: push new code, and traffic starts hitting it a moment later. That coupling is what this reference exists to break. Once deploy and release are separated, everything downstream — canary and ring rollouts, health gates, rollback — gets to work at the speed of a config change instead of the speed of a build-and-redeploy cycle.

## Table of contents
- The distinction: running vs. exposed
- The decoupling mechanism: flags, dark launch, traffic routing
- Release is an owned, reversible decision
- Who flips it, and how the flip is itself reversible
- Flag hygiene: cleanup, not permanent forks

## The distinction: running vs. exposed

A **deployed** version is running: processes are up in the target environment, health checks pass, it's consuming its config, it may even be handling background or internal traffic. A **released** version is one whose new behavior is actually exposed to (some slice of) real users. Most deploy tooling defaults to also releasing — the instant new code is running, it's serving requests — which is exactly why the distinction has to be deliberately engineered rather than assumed to already exist.

The reason to insist on the split even when the tooling doesn't force it: every mechanism this skill relies on elsewhere — progressive widening, a health gate that halts a rollout, a fast rollback — only stays cheap if exposure can move independently of the artifact reaching the environment. Once code-reaching-the-environment and code-being-exposed are the same lever, "roll back" necessarily means "redeploy," which is the slow, high-stakes action a rollback plan exists to avoid (see `rollback-and-compatibility.md`).

## The decoupling mechanism: flags, dark launch, traffic routing

Three category-level mechanisms create the seam between deploy and release, and a given change may need one, several, or none of them depending on what actually needs controlling:

- **Feature flags** gate a code path behind a runtime-evaluated condition — a config-driven boolean, a targeting rule evaluated by a flag service. The new code ships fully deployed; the flag decides whether any given request exercises it.
- **Dark launch** runs the new path against real traffic or real data without surfacing its output to users — shadow requests, write-but-don't-serve — so its correctness and performance can be validated under real load before anyone's experience depends on it.
- **Traffic routing** sends a fraction of requests to the new version at the edge — a proxy, gateway, or service-mesh rule — without touching an in-app flag at all.

These answer a different question than progressive delivery's canary/ring/rolling mechanics do. Canary and rings answer "how many users hit the new version"; flags and dark launch answer "does the new version's *behavior* show up to anyone at all." The two axes are independent: a change can be deployed to 100% of instances — every instance running the new binary — while its behavior stays flagged off for everyone, or dark-launched to gather evidence before a single user sees a difference. Conversely, a canary can expose a new version's default (un-flagged) behavior to a traffic slice with no flag involved. Choose the mechanism the change's actual risk needs — not all three by default.

## Release is an owned, reversible decision

Deploy is continuous, automated, and — done well — unremarkable when it happens. Release is a deliberate act someone takes, at a decided time, for a decided reason: a person, or an explicit automated policy standing in for one, chooses to expose the new behavior now. The reason to keep this distinction sharp: automating deploy away is what makes shipping code boring, which is the goal. Automating the exposure decision away too removes the one point in the process where human judgment — is this the right moment, does anything else in flight interact with this, are the right people watching — still adds value that a pipeline can't supply on its own. Collapsing deploy and release back into a single automatic step trades that judgment point for convenience it didn't need to spend.

## Who flips it, and how the flip is itself reversible

Name who owns the release decision explicitly — it is not implied by who merged the PR or who ran the deploy. Depending on the change's blast radius, that owner might be the change's author, an on-call, or a product owner; what matters is that it's decided, not assumed.

The flip itself must be as fast and as safe to reverse as it was to make — a config change, not a redeploy. If turning a release off takes as long as the original deploy did, the decoupling bought nothing: the entire value of a flag or a routing rule is that "off" is instant and cheap, cheaper even than the fastest code rollback path (see `rollback-and-compatibility.md`). A flip that itself requires code review and a deploy pipeline to reverse isn't a release decision anymore — it's a second deploy wearing a release's name.

## Flag hygiene: cleanup, not permanent forks

Every flag introduced to decouple a release has a planned removal from the moment it's created: once the release is fully rolled out and the old path is no longer needed as a rollback rail, delete the flag and the dead branch it guards. A flag that never gets removed becomes a permanent fork in the code — two paths that both have to keep working, both need testing (or, worse, quietly stop getting it), and both get carried in the head of everyone who touches that code afterward. The count of live flags in a codebase either stays roughly flat, each new one balanced by a removed one, or it grows without bound; unbounded growth is complexity debt that compounds silently, because no single flag addition ever looks like the problem on its own. Tie a flag's removal to the same evidence-of-done that closes out the release itself, rather than leaving it as an unowned someday-cleanup task.
