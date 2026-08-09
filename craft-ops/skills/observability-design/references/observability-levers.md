# Observability Levers — ramp detail up and down without a redeploy

The moment something breaks, the right response is to see more — more log detail, more trace depth, more of what's actually happening — not to guess harder from what's already being collected. That only works if "see more" is a dial someone can turn *during* the incident, not a code change that has to be written, reviewed, and deployed while the incident is still live. This reference is about building that dial in advance: what the dials are, how narrowly to scope them, what their two settings are, how they're flipped, and what stops a turned-up dial from becoming its own incident.

## Table of contents
- The dials: verbosity, sampling rate, trace/span detail, debug logging
- Scope every lever as narrowly as the blast radius, not the fleet
- Two settings per lever: default and incident
- Flip via runtime config or flags — never a redeploy
- Cost and cardinality guardrails
- Auto-revert: a lever left up is a bill or an outage waiting to happen

## The dials: verbosity, sampling rate, trace/span detail, debug logging

Four runtime-adjustable dials cover most of what a live incident needs, and each answers a different question when turned up:

- **Log verbosity** — moving from `info` to `debug` (or finer) surfaces the intermediate steps a request took, not just its outcome. Answers "what did this code path actually do."
- **Sampling rate** — the fraction of traces or events actually captured. Turning it up (toward, or to, 100%) stops the incident's low-frequency edge case from being the one request that didn't get sampled. Answers "can I even see the request that failed."
- **Trace/span detail** — how finely a single request's execution is broken into spans, and how much is attached to each (attributes, timing, child calls). Answers "where, inside this one request, did the time or the error actually happen."
- **Debug logging** — verbose, often per-library or per-module logging that's too noisy and too expensive to run by default. Answers "what is this specific dependency doing, argument by argument."

Each is a dial, not a switch, because "on" for an entire fleet is rarely the right amount of "on" — which is exactly what the next rule is about.

## Scope every lever as narrowly as the blast radius, not the fleet

Every lever needs a scope it can be applied to that's no wider than the incident actually is: a single service, a single route, a single tenant, even a single request (via a header or a targeted flag), not a global flip that turns every dial on for every request across the whole system. The reason narrow scoping is the default, not an optimization applied later under pressure: a global flip multiplies the lever's cost (see cardinality guardrails below) by however many services, tenants, and requests aren't actually part of the incident, while adding zero signal about the one that is — all the extra volume is exhaust, not evidence. A lever that can be scoped to "this tenant, this route" turns on exactly where the blast radius is and nowhere else, which is both cheaper and, because the resulting signal isn't diluted by everything unaffected, more useful for actually finding the cause.

## Two settings per lever: default and incident

Every lever has exactly two named settings decided in advance, not tuned live: a **default** setting that's affordable to run indefinitely (low verbosity, a sampling rate the budget tolerates, coarse trace detail), and an **incident** setting that's expensive but affordable for the duration of an incident (verbose, high or full sampling, fine-grained tracing). The reason both are decided at design time rather than improvised during the incident: deciding "how loud is loud enough" while an incident is already live means guessing under pressure, and a lever with no pre-agreed incident setting either gets under-turned (still not enough signal to find the cause) or over-turned (see cost guardrails below) — both failures that a pre-agreed setting, chosen calmly, avoids by construction.

## Flip via runtime config or flags — never a redeploy

The mechanism that moves a lever from default to incident setting is a runtime config change or a feature flag flip — evaluated live, taking effect in seconds — never a code change that has to go through build, review, and deploy. This is the same discipline `deployment-design`'s deploy-vs-release split relies on (see `deployment-design/references/deploy-vs-release.md`): the *capability* to run at incident-level detail ships fully built into the deployed artifact ahead of time, and the *decision* to actually use it is a separate, much cheaper action taken only when needed. A lever that requires a redeploy to turn up isn't a lever during an incident — a redeploy pipeline, however fast, is minutes when the need is seconds, and it adds exactly the kind of pressure-driven code change (rushed, under-reviewed, deployed straight into a live incident) that mitigate-before-you-diagnose exists to avoid. If turning up detail requires touching code at all, the lever wasn't built — build it before the next incident needs it, not during this one.

## Cost and cardinality guardrails

An incident setting turned up is, by design, expensive — more log volume, more traces, more high-cardinality attributes — and that cost has to be bounded before the lever ships, not discovered on the bill afterward. Every lever needs a stated ceiling: a maximum sampling rate, a cap on how many services or tenants can run at incident-level detail simultaneously, a cardinality limit on which fields get attached at the verbose setting. The reason the ceiling has to be decided in advance: mid-incident is the worst time to notice that "turn everything up" also means "the observability backend falls over from the ingest volume it's now receiving," which trades a service incident for an observability-platform incident, or replaces user pain with a bill that has to be explained after the fact. A ceiling decided calmly, before it's needed, is what lets someone flip the lever during an incident without also having to reason about its cost in that moment.

## Auto-revert: a lever left up is a bill or an outage waiting to happen

Every lever that gets turned up needs a mechanism that turns it back down without depending on a human remembering to do it — a time-to-live on the flag, an expiring config override, a scheduled sweep that resets anything still on incident settings past a threshold. The reason auto-revert isn't optional: the moment an incident ends, attention moves immediately to the retro and the next thing on fire, and "remember to flip the debug flag back off" is exactly the kind of manual follow-up that reliably falls through — not because anyone's careless, but because it's competing with everything else that also needs attention right after an incident. A lever with no auto-revert doesn't fail loudly when forgotten; it fails quietly, days or weeks later, as a cardinality bill that's crept up or an ingest pipeline that's been running hot since an incident nobody remembers turning the dial for. Building the revert in at design time is what makes turning the lever up during an incident a decision with a natural expiration, not a standing liability someone has to remember to clean up.
