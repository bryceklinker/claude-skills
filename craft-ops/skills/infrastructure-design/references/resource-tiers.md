# Resource tiers — disposable vs. durable

The question tiering answers is simple: if this resource vanished tonight and got rebuilt tomorrow from the same code, would anything be lost? For most infrastructure the answer is no — compute is fungible, and rebuilding it from source is the whole point of infrastructure as code. But for a database, an object store, a queue, the answer is yes, and it's irreversible: the code describes the *shape* of a database, not the rows in it. Tiering exists because "immutable, replace freely" is correct for one of those answers and catastrophic for the other, and a design that doesn't say which resource is which is a design that will eventually apply the wrong one.

## Table of contents
- How to classify a resource
- The disposable tier
- The durable tier
- The failure mode of mis-tiering

## How to classify a resource

Ask one question per resource: **does it hold state, data, or in-flight messages that cannot be regenerated from the code and config that describe it?** Not "is it expensive," not "is it hard to configure," not "would it be annoying to lose" — those are all true of plenty of disposable resources too. The only thing that moves a resource into the durable tier is that its *content*, not just its *configuration*, is unique and unrecoverable from anything else in the repo.

The reason the test is this narrow: a broader test (e.g. "anything important is durable") makes every resource durable, which makes the tier meaningless — everything gets deletion-protection, everything is precious, and the signal that should make you pause before a destructive apply disappears into noise. Tying the tier strictly to *content that can't be rebuilt from code* keeps the durable set small and keeps it meaning something when you see it.

Apply the test resource by resource, not service by service — a managed database cluster is durable, but a read-replica or a connection-pooling proxy in front of it may not be; the data lives in one place, and only that place needs the guard.

## The disposable tier

Compute, functions, containers, load balancers, most networking (subnets, routes, security groups) belong here — anything whose entire definition lives in code and config, with no unique content of its own. Treat these as **immutable and replace-don't-mutate**: when a change is needed, the tool tears down the old resource and stands up a new one rather than patching it in place, and that's fine, because "new one" and "old one" are indistinguishable — both are fully described by the same source.

The reason replace-don't-mutate is the right default here, not just a tolerated one: mutation in place is how configuration drifts from what the code says, resource by resource, until the actual infrastructure and the repo describing it quietly diverge. Replacing forces every change to go through the code, which is what keeps code the single source of truth. Losing a disposable resource costs an apply; it never costs data.

## The durable tier

Databases, object/blob stores, queues, topics, event buses — anything holding data or messages that exist nowhere else — belong here. These are **never deleted or replaced as a side effect of a change.** Two things make that non-negotiable in practice, not just in intent:

- **Deletion-protection and no-destroy lifecycle guards**, configured directly on the resource, so that a plan which would destroy or force-replace it is rejected by the tool itself — not caught only if a human happens to notice it in a diff.
- **Migrate, don't recreate.** When a durable resource's shape needs to change — a new column, a new index, a renamed queue — that's a schema or data migration applied *to* the existing resource, never a teardown-and-recreate that happens to end up with the right shape.

The reason durable resources get protection instead of just caution: caution is a human habit, and habits fail under fatigue, urgency, or a reviewer who's seen a hundred green plans in a row. A lifecycle guard fails the apply mechanically, every time, regardless of who's reviewing or how confident the diff looked. The guard is the actual control; the discipline around it is what keeps the guard from being routinely disabled to "get this one apply through."

## The failure mode of mis-tiering

Mis-tiering has exactly one shape: a resource that should have been durable gets treated as disposable, its config changes in a way the tool can't apply in place (a renamed identifier, a changed engine version, an attribute that's immutable-in-cloud-API-terms), and the plan proposes a forced replacement. If nothing catches that plan before apply, the tool does what disposable resources are always allowed to do — deletes the old and creates a new — except this time "the old" was holding the only copy of the data, and "the new" starts empty.

That's the entire reason this tier distinction exists: not to organize resources for tidiness, but because the disposable tier's core convenience — replace freely, the code is the truth — is precisely the operation that destroys a durable resource's data. Getting the tier wrong doesn't fail loudly at design time; it fails silently at apply time, as a plan that looks like routine infrastructure churn until the durable resource in it is gone. (The apply-time backstop for this — checking every plan for a destroy/replace of a durable resource before it runs — is its own convention; see `review-before-apply.md`.)
