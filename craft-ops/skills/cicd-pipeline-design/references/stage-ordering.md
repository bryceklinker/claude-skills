# Stage Ordering — cheapest, most-likely-to-fail first

A pipeline is a queue of checks between a commit and a deployable artifact. Every check that runs before the one that actually catches the problem is wasted time on every single commit — multiplied across every commit anyone ever pushes. Ordering stages by cost and failure likelihood isn't a style preference; it's the difference between a feedback loop measured in seconds and one measured in "go get coffee."

## Table of contents
- The default order and its rationale
- Fail-early: why the order matters more than the stages
- Parallelizing without losing the earliest signal
- Green main is sacred — stop the line

## The default order and its rationale

The convention is: **format/lint → unit tests → build the artifact → integration/acceptance tests → deploy.** Each step earns its position:

- **Format/lint first** — it's near-instant, needs no compiled code and no dependencies resolved, and catches the class of mistake (typos, style drift, obviously malformed syntax) a human should never wait on a build to hear about.
- **Unit tests second** — still fast (no I/O, no external services), and they cover the largest share of logic errors per second of compute spent. If the domain logic is wrong, this is the cheapest place to find out.
- **Build the artifact third** — only worth doing once the code is known to be syntactically sound and behaviorally correct at the unit level. Building broken code and then discovering it in a slower stage wastes the build.
- **Integration/acceptance fourth** — these need the real artifact, real dependencies, or a real environment, so they're inherently slower and pricier. Run them once you already trust the parts they're testing don't have unit-level bugs to shake out.
- **Deploy last** — the actual environment change happens only after every earlier check has already vouched for the artifact.

The ordering principle generalizes past this specific list: whatever your repo's actual checks are, put the ones that are cheap *and* most likely to catch a real problem before the ones that are expensive *or* rarely the source of the failure. Don't keep this five-stage list if the repo's actual checks don't map onto it — reorder around what's actually cheap and what actually fails often here.

## Fail-early: why the order matters more than the stages

The value of ordering isn't in having the right stages — it's in *stopping* as soon as one of them fails. A pipeline that runs every stage to completion regardless of earlier failures throws away the entire point of ordering: the commit author still waits for the slow stages to finish before learning what unit tests would have told them in seconds. Fail-early means the pipeline halts at the first red stage and reports it immediately, not after every remaining stage limps to a finish.

This also protects the shared resource the later stages consume. Integration environments, deploy targets, and paid third-party sandboxes are typically scarcer and more contended than a lint pass. Every commit that fails lint but still proceeds to occupy an integration environment is compute and contention some other commit didn't get.

## Parallelizing without losing the earliest signal

Independent stages — ones that don't depend on each other's output — can run concurrently to shorten wall-clock time. Parallelism and fail-early aren't in tension, but they can look like it if applied carelessly: running lint and a slow acceptance suite side by side means a lint failure has to wait for the acceptance suite to notice the whole run should stop, if the runner doesn't cancel siblings on first failure.

The rule: parallelize freely, but configure the runner to **cancel outstanding stages the moment any stage fails**, and make sure the *report* surfaces the earliest, cheapest failing signal first even if a later stage's failure message arrives sooner in wall-clock time (a flaky, slow integration test failing at second 40 shouldn't bury a lint error that was known at second 2). The goal of ordering was never strict serial execution — it was making sure the reader learns about the cheap, likely failure without paying for the expensive, unlikely one. Parallel execution that preserves that priority is fully compatible with fail-early; parallel execution that lets a slow stage's failure eclipse a fast stage's failure is not.

## Green main is sacred — stop the line

Everything above governs a single commit's pipeline run. "Green main is sacred" governs what happens when main itself goes red: **stop new work landing on top of the break and fix or revert immediately**, rather than letting subsequent commits queue up on a known-broken base.

The reason is compounding cost, not politeness. Every commit that lands on top of a broken main either inherits the break silently (their pipeline can't tell their change apart from the pre-existing failure) or has to fight through noise to find their own real regression. The longer a break sits, the more commits pile up behind it, and the harder it becomes to bisect which one actually caused the problem versus which ones just landed on a broken foundation. Treat a red main as an incident, not a queued ticket: the fastest fix is usually the smallest — revert the breaking commit, restore green, then re-land the fix (see craft-ops `PRINCIPLES.md`, "Fast feedback, fail early") — rather than debugging forward under pressure while everyone else is blocked.
