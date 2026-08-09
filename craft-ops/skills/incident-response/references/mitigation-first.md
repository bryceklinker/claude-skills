# Mitigation First — pull the reversible lever before you understand the problem

Under an active incident, the fastest path to stopping user harm is almost never a fix — it's a reversal. A clever forward fix requires first understanding the problem correctly, then implementing the fix correctly, then shipping it correctly, all under time pressure and incomplete information, all while users keep experiencing the thing that's currently broken. A reversible lever requires none of that understanding: it just needs to exist, be known, and be pulled. This reference covers which levers to reach for, in what order, and why reaching for them beats reaching for understanding first.

## Table of contents
- Why reversibility beats a clever fix under pressure
- The levers, in priority order
- Turn observability up in parallel, not after
- When roll-forward is genuinely the only path
- Don't chase root cause while users are still harmed

## Why reversibility beats a clever fix under pressure

A reversible action has a property a forward fix doesn't: if it's wrong, undoing it costs almost nothing. Rolling back a deploy that turns out not to be the cause costs a few minutes and a re-deploy; shipping a forward fix based on a wrong hypothesis costs those same minutes *plus* whatever the wrong fix itself broke, discovered only after it's already live. Under incident pressure — partial information, adrenaline, an audience — the odds of a first-guess forward fix being exactly right are worse than they'd be with a clear head, which is precisely when a cheap-to-undo action is worth more than a high-conviction one. This is the same logic `deployment-design`'s rollback-first principle applies to routine rollouts, just under harsher conditions: decide the way back in advance, and reach for it before reaching for judgment made in the moment.

## The levers, in priority order

These levers are not invented during the incident — they're the same reversible mechanisms `deployment-design` built in advance, reached for here in priority order because they get progressively less targeted and more disruptive:

1. **Roll back the recent deploy.** If something shipped recently and the incident timing lines up, revert to the last known-good version first. It's the most targeted lever — it undoes exactly the suspected change — and it's the one most likely to already be rehearsed and fast (see `deployment-design`'s `rollback-and-compatibility.md`).
2. **Flip the feature flag off.** If the suspect behavior is behind a flag, turning it off is faster than a rollback and touches nothing else — a config change, not a redeploy (see `deployment-design`'s `deploy-vs-release.md` on why the flip has to be cheap).
3. **Shed or limit load.** If neither a recent deploy nor a flagged behavior is the obvious cause, reduce what's hitting the system — rate limit, shed low-priority traffic, degrade a non-critical feature — to keep the system upright while diagnosis continues.
4. **Fail over.** If the issue is isolated to a specific instance, region, or dependency, route around it. This is the least targeted and most disruptive lever, reached for once the more surgical options are exhausted or don't apply.

Try them in this order because each one is cheaper and more reversible than the next: a rollback undoes a known change, a flag flip undoes a known exposure, load shedding is a blunt but instantly reversible dial, and failover is the biggest structural move. Reaching for failover before checking whether a rollback would have solved it is reaching for the most disruptive tool first for no reason.

## Turn observability up in parallel, not after

While a lever is being pulled, ramp observability up at the same time — raise verbosity, sampling, and trace detail using the levers `observability-design` already built for exactly this moment (see that skill's incident-vs-default settings). This isn't sequenced after mitigation; it happens alongside it, because the facts needed for diagnosis are far easier to capture while the incident is still live than to reconstruct afterward from whatever happened to be logged at default verbosity. Mitigating without also ramping observability up trades away the evidence the postmortem will need, for no additional speed — the two actions don't compete for the same time.

## When roll-forward is genuinely the only path

Sometimes none of the reversible levers apply: nothing recent shipped, no flag gates the behavior, load shedding doesn't touch the actual failure, and there's no redundant target to fail over to — the system is stuck in a bad state that only a forward change can correct, such as a data-shape problem that a rollback would leave exactly as broken. In that case, roll forward, but treat it as the fallback it is, not the first idea: confirm the reversible levers genuinely don't apply before reaching for a fix that has to be correct on the first attempt, keep the forward fix as small and as narrowly scoped as the actual problem allows, and get a second pair of eyes on it before shipping if the incident's severity allows the extra minute — a small, reviewed forward fix is still safer than a broad one shipped solo under pressure.

## Don't chase root cause while users are still harmed

Diagnosis is phase three of this skill's discipline, after roles are assigned and mitigation is underway — not a parallel track that competes with pulling a lever. The failure mode this rule exists to stop: someone finds the mitigation lever, hesitates because they want to understand *why* first, and spends the next twenty minutes in logs while users keep experiencing the incident the lever would have already stopped. Root cause matters — it's exactly what the postmortem's ratchet depends on — but it matters *after* the bleeding stops, never as a precondition for stopping it. If a lever is available and applicable, pull it before you're sure why it's needed.
