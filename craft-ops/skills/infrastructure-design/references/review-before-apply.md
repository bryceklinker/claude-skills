# Review before apply — the plan is the gate

An apply is irreversible the moment it runs — the tool doesn't ask again once it starts creating, changing, or destroying real infrastructure. The plan (or diff, depending on tool) is the only point where "what's about to happen" can be read, questioned, and stopped before it's real. Skipping review, or reviewing it as a formality, throws away the one chance to catch a mistake before it's a production incident instead of a code comment.

## Table of contents
- Always plan, always review
- The first check: destroy or replace of a durable resource
- Blast-radius thinking
- Idempotent, convergent apply

## Always plan, always review

Every apply is preceded by a plan or diff, and every plan is read by a human (or an automated gate encoding the same checks) before the apply runs — never `apply` run directly against a change no one has seen resolved. The plan is where the tool tells you, concretely, what it's about to create, change, and destroy; treating that output as noise to scroll past defeats the entire reason the tool separates planning from applying in the first place.

The reason this can't be skipped even for "small" or "obviously safe" changes: the plan is generated from the *actual* current state plus the *actual* proposed code, which means it can surface consequences the author of the change never intended and wouldn't have predicted by reading the diff alone — a renamed variable that the tool interprets as delete-and-recreate, a default that changed upstream in a shared module, a resource that some other change already touched. The diff you wrote and the plan the tool produces are answering different questions; only the plan answers "what will actually happen."

## The first check: destroy or replace of a durable resource

Before anything else in the plan gets attention, check one thing: **does it destroy or force-replace any durable resource** — a database, an object store, a queue, a topic, an event bus (see `resource-tiers.md`)? This is the first, non-negotiable check, ahead of cost, ahead of style, ahead of whether the disposable resources in the plan look reasonable — because it's the one category of consequence a later step can't undo.

If the answer is yes, that's a **stop-the-line event**: the apply does not proceed on the strength of a green plan alone. It requires explicit, deliberate confirmation from someone who understands why the destroy/replace is happening, and — if the resource holds data anyone cares about — a named migration path for that data before the apply runs, not written afterward as a postmortem action item.

The reason this check comes first and alone, rather than folded into "review the whole plan carefully": a plan can be long, and a human reading top-to-bottom for general reasonableness is exactly the review style that misses one destructive line buried among forty routine ones. Making the durable-resource check its own explicit first pass — done before the general review, not as part of it — means it doesn't depend on the reviewer's attention holding up for the length of the diff.

## Blast-radius thinking

Before applying, ask how far the change actually reaches: does it touch one resource, one module, one environment — or does a shared module, a shared network boundary, or shared state mean this "small" change plans against staging and prod simultaneously? Isolate risky or exploratory changes to the smallest scope that can validate them (a single environment, a single component's state — see `state-and-modules.md`) rather than letting them run against everything by default.

The reason blast radius is assessed before applying, not discovered by the outcome: a change scoped to touch only what it needs to fails safely — the worst case is bounded and known in advance. A change with unnecessarily wide reach turns every apply, including routine ones, into an event with production-wide stakes, whether or not anything actually goes wrong this time. Matching scope to intent is what keeps "this apply affects one thing" true in practice, not just in the author's mental model of the change.

## Idempotent, convergent apply

An apply should be safe to run again — against the same code, in the same state — and produce the same result: no duplicate resources, no error from something "already existing," no unintended side effect from re-running after a partial failure or a retried pipeline step. The tool converges actual infrastructure toward the desired state described in code; running it twice with nothing changed in between should converge to a no-op plan the second time.

The reason idempotency matters as a design property, not just a nice tool behavior: applies fail partway through — a network blip, a timeout, a rate limit — and the recovery step is almost always "run it again." If re-running isn't safe, every failure turns into manual cleanup before the fix can even be attempted, under exactly the time pressure that makes manual cleanup most error-prone. Idempotent, convergent apply is what makes "just re-run it" a reliable recovery instead of a gamble.
