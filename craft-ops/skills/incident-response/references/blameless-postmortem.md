# Blameless Postmortem — the review only produces truth if nobody's defending themselves

A postmortem exists to make the next incident less likely, and it can only do that if it has accurate information about what actually happened — every decision made, every signal missed, every assumption that turned out wrong. That information only surfaces when the people who have it don't have a reason to hide it. This reference covers how to run the review so it produces that information, and what it has to produce before it counts as done.

## Table of contents
- Why blame suppresses the information a postmortem needs
- A factual timeline, not a narrative
- Contributing conditions: system and process, never a person
- The ratchet: action items plus at least one new test or alert
- Keep actions owned and time-bound

## Why blame suppresses the information a postmortem needs

The moment a postmortem starts looking for who's at fault, everyone in the room has a new incentive: say less, hedge more, frame their own actions in the most defensible light. That's a rational response to a review that might cost someone their standing, and it's exactly the response that makes the review useless — the details that would actually explain the incident (I wasn't sure what that alert meant, I assumed someone else had checked that, the runbook was out of date and I didn't say anything) are the first things people stop volunteering once blame is on the table. Blameless isn't a tone choice or a courtesy; it's a precondition for the review getting the facts it needs to do its job. A postmortem that makes people defensive gets a worse postmortem, not a more accountable team.

## A factual timeline, not a narrative

Build the timeline from what's verifiable — timestamps from logs, alerts, deploys, messages, dashboards — not from memory or from the story that feels like it explains things. Record what happened and when, including the parts that don't yet make sense: an alert that fired and was dismissed, a deploy that went out during the window, a metric that moved twenty minutes before anyone noticed. The reason to resist narrating too early: a timeline that's already been shaped into a story tends to quietly drop the details that don't fit the story, and those are frequently the details that matter most. Get the sequence of verifiable facts down first; the explanation gets built from that sequence, not imposed on it.

## Contributing conditions: system and process, never a person

Every incident has contributing conditions, and they sort into two categories: **system** conditions (a missing alert, an undertested code path, a dependency with no circuit breaker, a dashboard that didn't surface the right signal) and **process** conditions (an on-call rotation with no backup, a runbook nobody had reviewed in a year, a deploy that skipped a review step because of an unrelated deadline). "A person made a mistake" is never a contributing condition on its own — it's a symptom of one of the two categories above. If someone missed an alert, ask why the alert was missable rather than stopping at "they missed it": was it buried in noise, was it ambiguous, was there no backup watching it. Every "someone did X" has a system or process condition sitting underneath it that made X possible or likely; find that condition, because it's the one that's still there for the next person even after this person is more careful.

## The ratchet: action items plus at least one new test or alert

A postmortem is not complete as a document, however accurate its timeline — it has to change something. This is the operational form of the same test-ratchet discipline that applies to a codebase: every incident either leaves the system measurably harder to break the same way again, or it was time spent writing an autopsy nobody acts on. Concretely, the review produces:

- **Tracked action items** — each one addressing a specific contributing condition identified above, filed as real, visible work rather than a bullet point that dies at the bottom of a document.
- **At least one new test or alert that would have caught this incident earlier** — not generic hardening, but something that, had it existed before this incident, would have shortened the time to detection or prevented the incident outright. If the postmortem can't identify one, that's a sign the contributing-conditions analysis didn't go deep enough, not a sign this incident was uniquely uncatchable.

An incident that produces a well-written timeline and nothing else will happen again in the same shape, because nothing about the system or the process that allowed it has changed.

## Keep actions owned and time-bound

Every action item gets a named owner and a target date at the moment the postmortem closes — not "someone should probably." An action item with no owner is a wish, and a wish doesn't ratchet anything; it just makes the postmortem feel more thorough than the system actually became. Track action items to completion the same way any other committed work is tracked, and treat an aging, un-owned action item from a past postmortem as a signal worth surfacing on its own — it means the last incident's lesson never actually landed.
