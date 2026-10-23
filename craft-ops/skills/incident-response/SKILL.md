---
name: incident-response
description: "Use when an incident is active or imminent — production down, error rate or latency spiking, an SLO burning, a bad deploy in progress — or when running the postmortem afterward, or deciding incident severity and process. Drives the response as a discipline: declare and assign an incident commander early, mitigate before you diagnose (roll back / flip the flag / shed load / fail over, and turn observability levers up), diagnose with method against the ramped-up signals, resolve and verify on real evidence, then run a blameless postmortem that ratchets — tracked action items plus at least one new test or alert that would have caught it. It defers root-cause mechanics to systematic-debugging and owns the incident wrapper. Not for designing observability/SLOs, CI/CD, infrastructure, or deployment strategy — those are other skills."
---

# Incident Response

Stop the harm, then find the cause, then make the next one less likely — in that order. The levers you pull were designed earlier (`deployment-design`'s rollback and flags, `observability-design`'s runtime levers); this skill reaches for them under pressure. Read `deployment.rollback_command` and `observability.*` from `.craft-ops.yml` (`craft-ops-conventions`).

## 1. Declare and set roles

Bias toward declaring: a false alarm costs minutes, a late declaration costs users hours. Name one **incident commander** who decides — mitigate, escalate, stand down — and delegates rather than debugging, and a separate **comms lead** who keeps stakeholders updated. Set severity by user impact. `references/incident-command.md`.

## 2. Mitigate before you diagnose

Stop user harm with a reversible lever before spending time on why: roll back the recent deploy, flip the flag off, shed load, fail over. At the same time, turn the observability levers up so diagnosis has signals when it starts. `references/mitigation-first.md`.

## 3. Diagnose with method

Once harm is contained, find the cause against the ramped-up signals — reproduce, narrow, one hypothesis at a time — keeping a written timeline. The mechanics are craft-code's `systematic-debugging` (or the same method applied directly without it).

## 4. Resolve and verify on evidence

Close when the signal that declared the incident — the SLO, the error rate — shows recovery, not when the fix should have worked. Closing isn't fixing: the lever bought time. The cause becomes tracked work with a recommended fix level, and any mitigation kept in place (flag left off, capacity left doubled) records what would let it be removed (`PRINCIPLES.md` core 10).

## 5. Blameless postmortem that ratchets

A timeline, the contributing conditions across system and process (never a person), and owned, time-bound action items — including at least one new test or alert that would have caught this earlier. A narrative with no ratchet isn't finished. `references/blameless-postmortem.md`.

## Exit condition

Harm stopped and verified on the real signal; a blameless postmortem with a timeline, contributing conditions, tracked action items, and at least one new test or alert.
