---
name: incident-response
description: "Use when an incident is active or imminent — production down, error rate or latency spiking, an SLO burning, a bad deploy in progress — or when running the postmortem afterward, or deciding incident severity and process. Drives the response as a discipline: declare and assign an incident commander early, mitigate before you diagnose (roll back / flip the flag / shed load / fail over, and turn observability levers up), diagnose with method against the ramped-up signals, resolve and verify on real evidence, then run a blameless postmortem that ratchets — tracked action items plus at least one new test or alert that would have caught it. It defers root-cause mechanics to systematic-debugging and owns the incident wrapper. Not for designing observability/SLOs, CI/CD, infrastructure, or deployment strategy — those are other skills."
---

# Incident Response — stop the harm, then find the cause

## Why this exists

Under an active incident, the instinct is to start debugging the interesting puzzle while users are still hurting — chasing root cause on a hunch, digging through logs at default verbosity, treating the outage as a mystery to solve rather than harm to stop. The discipline forces mitigation first, method second, and a review that makes the next occurrence less likely, in that order, every time.

It is a **doing** phase, not a design one. Nothing here is decided under pressure for the first time — the reversible levers, the observability dials, and the debugging method were all designed and built earlier. This skill is the wrapper that reaches for them, in order, while an incident is live. Its five phases apply the principles in `craft-ops/PRINCIPLES.md`'s "Observability & incident response" section (mitigate-before-diagnose, blameless, the ratchet, method-not-guesses).

## Seams

- **`deployment-design`** designed the reversible mitigation levers — rollback, feature flag, load shedding, failover — before this incident started. This skill pulls them; it doesn't invent a new one under pressure.
- **`observability-design`** designed the runtime levers — verbosity, sampling, trace detail — and their incident-vs-default settings. This skill turns them up to gather facts, and back down once calm.
- **craft's `systematic-debugging`** owns the root-cause *mechanics* — reproduce, bisect, one hypothesis at a time. This skill owns the incident wrapper around it: when diagnosis starts relative to mitigation, whose job it is, and what evidence closes it out. It does not restate debugging technique.
- **Reads `.craft-ops.yml`** for this project's `deployment.rollback_command` and `observability.*` before mitigating or diagnosing — see `craft-ops-conventions`, which records and reads it.

## The discipline

Five phases, in order. Skipping ahead — diagnosing before mitigating, resolving without evidence, closing out without a ratchet — is the failure mode this skill exists to prevent.

### 1. Declare and set roles early

Bias toward declaring. A false alarm costs a few minutes of coordination; a slow declaration costs users minutes-to-hours of unmitigated harm. The moment an incident is suspected, name a single **incident commander** — one person who owns the decision to mitigate, escalate, or stand down — and a **comms lead** who keeps stakeholders and status updated so the commander can stay heads-down. Two roles minimum, one person each; the same person filling both is how updates stop going out and mitigation stalls waiting on a Slack thread. See `references/incident-command.md`.

### 2. Mitigate before you diagnose

Stop user harm with a **reversible lever** before spending a single minute on why: roll back the recent deploy, flip the flag off, shed load, fail over. These levers already exist — `deployment-design` decided them in advance — so pulling one is mechanical, not a judgment call made under pressure. In parallel, **ramp observability up**: raise verbosity, sampling, and trace detail using the levers `observability-design` already built, so the signals needed for diagnosis exist by the time diagnosis starts. Root cause comes after the bleeding stops, never before. See `references/mitigation-first.md`.

### 3. Diagnose with method

Once harm is mitigated, find the cause against the now-ramped-up signals: reproduce, narrow, one hypothesis at a time, with a running written timeline so the incident doesn't re-litigate the same dead end twice. **This phase defers its mechanics entirely to craft's `systematic-debugging`** — this skill's job is knowing that diagnosis happens here, third, after mitigation and with roles already assigned, not what debugging technique to apply once you're in it.

### 4. Resolve and verify on evidence

Close the incident when the real signal — the SLO, the error rate, the metric that paged in the first place — shows recovery, not when the fix "should" have worked or the dashboard looks calmer to the eye. Verification reads the same signal that declared the incident; a fix that hasn't moved that signal hasn't resolved anything yet.

### 5. Blameless postmortem that ratchets

Every incident gets a review: a timeline, the contributing conditions (system and process, not people), and **tracked action items**. The review is not complete as a narrative — it must produce **at least one new test or alert** that would have caught this before it paged. An incident that changes nothing will happen again. See `references/blameless-postmortem.md`.

## Guardrails

- **Mitigate before you root-cause.** Diagnosing while users are still hurting is the single failure this discipline exists to prevent.
- **Blameless, always.** The postmortem targets the conditions that allowed the incident, never who was on call when it happened.
- **Declare early; bias to declaring.** A retracted declaration is cheap. A late one is not.
- **The postmortem must ratchet.** A well-written timeline with no tracked action item and no new test or alert is not done.
- **Defer root-cause technique to `systematic-debugging`.** If you catch yourself explaining bisection or hypothesis framing here, stop — that content lives there, not in this skill's incident wrapper.

## Exit condition

User harm is stopped and verified from the real signal that declared the incident — not from inspection or a calmer-looking dashboard. A blameless postmortem exists with a timeline, contributing conditions, tracked action items, and at least one new test or alert that would have caught the incident earlier.
