# Incident Command — declare early, assign the two roles, escalate on a clock

An incident that never gets declared never gets a commander, never gets a comms lead, and never gets the coordination that turns a scramble into a response. Most of what goes wrong in the first ten minutes of a bad incident isn't technical — it's structural: nobody decided who's deciding, so three people are debugging in parallel and nobody's updating stakeholders. This reference covers the structure that has to exist before mitigation can start, not the mitigation itself (see `mitigation-first.md`).

## Table of contents
- Bias to declare
- One incident commander, not a committee
- The commander delegates; the commander does not debug
- A comms lead, always, so the commander stays heads-down
- Severity levels and what each one triggers
- Hand-off for long incidents

## Bias to declare

Declare the moment an incident is *suspected*, not once it's confirmed. The asymmetry is the whole argument: a declared-then-retracted incident costs a few minutes of coordination overhead and an "all clear" message; an incident that should have been declared but wasn't costs users the entire gap between "someone noticed" and "someone official started coordinating a response." That gap is pure unmitigated harm with no offsetting benefit — waiting for certainty doesn't make the outage smaller, it just delays the response to it. Treat every ambiguous signal — an odd spike, a handful of user reports, a dashboard that looks wrong — as a reason to declare and downgrade later, never as a reason to wait and see.

## One incident commander, not a committee

Every declared incident gets exactly one incident commander (IC). The IC owns the decision to mitigate, escalate, bring in more people, or stand down — a single point of decision-making authority, not a vote. The reason it has to be one person rather than "whoever's around": under time pressure, a decision made by consensus is a decision made slowly, and a decision nobody explicitly owns is a decision that doesn't get made at all until harm forces it. Naming one IC doesn't mean one person does all the work — it means one person is accountable for what happens next, and everyone else knows who to route decisions and findings to instead of guessing or freelancing.

## The commander delegates; the commander does not debug

The IC's job is to decide and delegate — who investigates what, which mitigation to pull, when to escalate, when to declare resolved — not to be the one heads-down in logs chasing the cause. The moment the IC starts debugging, the incident loses its one point of coordination: nobody is watching the whole picture, deciding what to try next, or deciding when enough mitigation has happened to call it contained. If the most technically capable person available is also the only plausible IC, that's a staffing gap to fix after this incident, not a reason to collapse the two roles now — a commander who's also debugging is a commander in name only.

## A comms lead, always, so the commander stays heads-down

Every declared incident also gets a comms lead — a second, distinct person who owns keeping stakeholders and status pages updated, fielding questions from outside the response, and freeing the IC from having to context-switch between coordinating the response and narrating it. The same person filling both roles is how updates stop going out: coordinating a live response is already a full-time job, and every minute spent drafting a status update is a minute not spent deciding the next mitigation step. Two roles, two people, minimum — even on a small team, even for a short incident.

## Severity levels and what each one triggers

Severity is decided at declaration and revisited as facts change, and it's what determines who gets paged, how often updates go out, and whether leadership is looped in — not a label applied after the fact for the postmortem. A workable shape:

- **SEV1 — critical.** Widespread user-facing impact or full outage. Pages the on-call immediately, pulls in an IC and comms lead without discussion, triggers a status page update, and gets leadership visibility while it's active.
- **SEV2 — major.** Significant but partial impact — a degraded feature, a slice of users affected, an SLO burning fast. Same IC/comms structure, status page update expected, leadership informed but not necessarily paged.
- **SEV3 — minor.** Limited or internal impact, no urgent user harm. Still declared and still gets an owner, but without the same paging or status-page urgency.

The exact labels and thresholds are a team decision — what matters is that severity is a defined, agreed scale before an incident happens, so declaring at SEV1 versus SEV3 is a fast lookup against known criteria, not a debate held mid-incident about how bad this really is.

## Hand-off for long incidents

An incident commander does not run indefinitely. When an incident stretches past a shift, past the point of sustainable focus, or past whatever the team has agreed is the maximum single-IC stint, hand off explicitly: name the new IC, brief them against the running timeline, and confirm they've accepted before the outgoing IC steps back. The reason hand-off has to be explicit rather than assumed: an exhausted IC makes worse decisions and misses things, but an incident with *no* IC — because the old one quietly stopped and nobody noticed — is worse still, since it silently reverts to the no-single-owner failure mode this whole discipline exists to avoid. For incidents that cross time zones or run overnight, plan the hand-off chain — who's next, how they get briefed — before the first shift ends, not when the first IC is already too tired to write a good hand-off note.
