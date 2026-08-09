# Rollback & Compatibility — the way back is decided, rehearsed, and doesn't need data to move

Every rollout, by design, spends time with old and new versions running at once. That window is where rollback and compatibility stop being separate concerns: the way back only works if the old version can still make sense of what the new version already wrote, and the new version's changes only stay safe to expose progressively if reverting them doesn't strand data or break the version being reverted *to*. This reference covers both halves together because a rollback plan that ignores compatibility isn't actually a rollback plan — it's a plan that works right up until it's tested against a real in-flight rollout.

## Table of contents
- Rollback-first: decide the way back before the rollout, not during
- An untested rollback is not a rollback
- Roll-forward vs. roll-back: which is the right call
- Old and new coexist: compatibility across the transition
- Expand-contract and N-1 compatibility
- Why code can roll back without data rolling back

## Rollback-first: decide the way back before the rollout, not during

The specific mechanism — what gets triggered, what config or version it reverts to, what state that reversion leaves the system in — is written down and agreed before the first user sees the new version, not improvised once a health gate has already fired. The reason this has to happen in advance: during an actual regression, the people involved are managing a live incident, under time pressure, often reasoning from incomplete information about what's actually broken. That is the worst possible condition under which to design a rollback procedure for the first time. Decide it when there's no pressure and full information available, so that acting on it during an incident means executing a known procedure — not inventing one while the error rate climbs.

## An untested rollback is not a rollback

The rollback path has to be exercised — actually triggered, at least once, somewhere real — before it's trusted as the safety net for the rollout it's meant to protect. A rollback plan that merely reads correctly on paper carries no more confidence than any other code that's never been run. The forward path gets exercised by every single deploy; the backward path, by construction, only gets exercised when something is already wrong — which is exactly why it's the one most likely to have quietly rotted since the last time it was for real: a script pointing at a renamed resource, a runbook step describing a UI that moved, a credential that expired. Rehearsing it — a scheduled drill, a game day, or deliberately triggering it during a lower-stakes rollout — is what turns "we have a rollback plan" from a claim into evidence.

## Roll-forward vs. roll-back: which is the right call

Roll-back reverts to the last known-good version; roll-forward ships a fix on top of the version that's currently broken. Which is faster and safer is a decision made per-incident against the actual state of things, not a reflex: roll-back is usually right when the regression is confined to the new code path and reverting doesn't strand data or in-flight work in a shape the old version can't handle — it's a known-good target, requiring no new judgment about whether a fix is correct. Roll-forward is right when the fix is small and well understood and faster to ship than a full reversion — for instance when rolling back would have to undo a data change that a forward fix can instead simply correct — or when reverting would resurrect a bug the new version was shipped specifically to fix. The reason this has to stay a choice rather than a default: treating rollback as automatically "the safe one" ignores that the rollback path can carry its own cost and risk (see compatibility below), and the actual goal is reaching a good state fastest, not reaching for the more habitual action.

## Old and new coexist: compatibility across the transition

For the entire duration of any progressive rollout, old and new versions are simultaneously live against the same downstream dependencies — the same database, the same message topics, the same downstream services, the same rollback target — not just for an instant at the boundary. This isn't an edge case to tolerate; it's the defining condition of a progressive rollout. The entire point of canary, rings, and rolling deploys is that old and new run side by side while a gate observes both — which means any assumption like "the new version writes it, so the old one doesn't need to read it," in either direction, breaks the moment the rollout is actually in progress, whether that's at 10% or 90%, not only at a clean cutover line.

## Expand-contract and N-1 compatibility

Schemas, APIs, and messages change through **expand → migrate → contract**, never through a single cutover step: first ship a superset that both the old and new code can understand (expand), let both versions run against that superset for the full rollout window, and only once the old version is fully retired remove what it needed (contract) — in a later, separate release. This is what N-1 compatibility means in practice: any given version only ever has to tolerate the *immediately previous* version's shape, not an arbitrarily old one, because contraction always happens exactly one release after the expansion that made it safe.

Concretely, this means something specific has to ship in a **prior** release — before the one that's rolling out now — to make the current rollout safely reversible: a new column added nullable or defaulted, a new message field that's additive-only, a new API field that's optional. That addition ships and fully rolls out (and, per the rehearsal rule above, gets proven rollback-safe) in the release before this one. Only once it's live everywhere is it safe for the *current* release to start requiring the new shape and to drop the fallback for the old one — never in the same release that introduces the read or write of the new shape.

The reason the split matters: if the release that removes the old shape is the same release that starts depending on the new one, rolling that release back mid-rollout — the exact rollback rehearsed above — simultaneously un-does the removal of the old shape and strands whatever the new code already read or wrote under the new shape. The "fast, rehearsed way back" becomes unsafe or outright impossible precisely at the moment it's needed most. Keeping expand and contract in separate releases is what keeps every single release, on its own, safely revertible on the compatibility axis — not just on the code axis.

## Why code can roll back without data rolling back

Durable resources — databases, object stores, queues, topics, event buses — are managed under the protect-and-migrate rule: never torn down or replaced as a side effect of a change, only migrated (see the infrastructure-design skill's resource-tier convention). Combined with expand-contract above, this means a code rollback is a code-only operation: revert the running version and stop there, with no matching data rollback required to make the system consistent again.

This matters as a rollback-*speed* argument, not only a data-safety one. The fast, rehearsed rollback promised earlier only stays fast if it never also requires an equally fast, equally rehearsed *data* rollback — data doesn't reverse at the pace code does, and a destructive schema change can't be safely undone at all once the rows it removed are gone. Migrate-only durable resources plus expand-contract compatibility are what decouple "how fast can we revert code" from "how fast, or whether, we can revert data" — and it's the coexistence requirement above, that old and new both need the data in a shape they can both tolerate, that makes migrate-only mandatory during a rollout window rather than merely a nice property to have.
