# Fix Options — choosing the level, and recommending one

Read this when a change could reasonably be made at more than one level and the cheap option is tempting. It exists because the shallowest fix that turns a test green is the one most likely to bring you back to the same file a third time — see the craft-code principle *fix the cause at its level, and recommend the durable option* (`PRINCIPLES.md` at the plugin root).

## The four levels

Any defect can usually be addressed at one of these. They are not ranked by virtue — they're ranked by how much of the problem they remove.

**1. Symptom.** Suppress or tolerate the visible failure without changing what produced it: widen a timeout, add a retry, guard the branch that threw, disable the control that misbehaves, filter the noisy log line.
*Removes:* the report. *Leaves:* the mechanism, free to surface somewhere else.
*Legitimate when:* you're stopping the bleeding under a real deadline, or the cause sits in code you don't own and can't change yet.

**2. Cause.** Change the thing the investigation actually named: the comparison that sorted strings, the state that wasn't reset, the missing await.
*Removes:* this bug, permanently. *Leaves:* whatever made that mistake easy to make.
*Legitimate when:* the cause is local and the surrounding design is sound. **This is the normal answer.**

**3. Structural.** Change the shape that allowed the cause to exist: remove the shared mutable state two features were racing on, delete the duplicated code path instead of fixing it twice, split the component whose two responsibilities kept interfering, replace a sentinel flag with a state model that can't hold an invalid value.
*Removes:* this bug and the family it belongs to. *Costs:* a bigger diff, more review, more test surface.
*Legitimate when:* this is the second or third bug from the same shape — or when the "cause" fix would be a guard whose only job is to keep two things from colliding.

**4. Make it observable.** Not an alternative to the others — an addition that's easy to skip. Whatever level you fix at, if the failure was silent or the investigation was slow for lack of evidence, land the missing signal too: the log that would have named it, the artifact the harness now keeps, the failure that now surfaces instead of being swallowed.
*Legitimate when:* always, if the failure was hard to see. A silent failure is itself a defect.

## Choosing

Ask, in order:

1. **Have I actually explained the mechanism?** If the proposed fix is a guard, delay, retry, or "disable it while X happens" and you cannot say *why* that works, you're at level 1 by accident. Go back to `systematic-debugging`.
2. **Is this the second time here?** A third patch to the same thirty lines, or the same environmental failure deferred twice, is the evidence that levels 1–2 aren't holding. Price level 3.
3. **What's the blast radius of the fix itself?** Especially for anything that blocks, disables, locks, serializes, or guards: *could this block the operation it's meant to protect?* A guard that disables a control during an async operation can disable the very interaction that completes it; a lock taken to prevent a race can deadlock the thing waiting on it. Name what the change makes impossible, not just what it prevents.
4. **What breaks if this stays forever?** Assume the stopgap is permanent, because unnamed stopgaps are. If that answer is unacceptable, it isn't a stopgap — it's the design, and it should be chosen as one.
5. **Does the constraint that favors the cheap option actually exist?** "There's a deadline" and "this feels big" are different things. Only the first is a constraint.

## Don't weaken a guarantee to make a symptom go away

Some cheap fixes work by removing a promise the system was making: making a confirmation non-blocking so the UI stops waiting, dropping a consistency check that was failing, accepting the request before the server has agreed to it. These look like level 2 — they change real code, the flakiness disappears — but they buy the green by making the system do less than it claimed.

Treat any option that relaxes a correctness guarantee as a **separate, explicitly-flagged decision**, never as an implementation detail of a bugfix. If a user must know the operation succeeded, "it's fine, it usually succeeds" is a product change and needs to be agreed as one.

## Writing the options up

Short. Three options at most, in a few lines each, in the work item or the design note:

```
Option A (symptom) — retry the assignment call up to 3×.
  ~20 min. Hides the race; it will resurface under load and in any new caller.
Option B (cause) — await the confirmation before clearing the drag state.
  ~2 h, touches 2 files. Removes this failure; the two components still share drag state.
Option C (structural) — RECOMMENDED. Move drag state into the container that owns it
  so the two components can't disagree. ~half a day, touches 5 files + tests.
  Removes this class of failure; C is B's fix plus the reason B was needed.
Regardless of choice: keep the browser trace and app logs on acceptance failure —
  this took three CI rounds to see (level 4).
```

Rules for the write-up:

- **Exactly one option is marked RECOMMENDED**, and it's the most durable one that fits the real constraints. Not the cheapest, not "it depends."
- **Costs are stated in effort and blast radius**, not in adjectives.
- **Each non-recommended option states what it leaves behind** — that's what makes the comparison real.
- **If a stopgap is chosen**, it ships with a *why*-comment naming the condition for removing it ("drop this retry once the assignment is confirmed server-side — see #123"), so it stays known debt instead of quietly becoming the design.
