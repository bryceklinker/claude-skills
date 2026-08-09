# SLOs & Alerting — the error-budget contract and paging on what users feel

An SLO is only useful if it's built on an SLI that measures what a user actually experiences, and an alert is only useful if it fires on that same user-facing signal instead of on whatever internal metric happened to move first. This reference covers both together because they're one mechanism, not two: the SLO defines the line, the alert is what fires when the line is being crossed, and every rule below exists to keep that line meaningful and that alert rare enough to trust.

## Table of contents
- SLIs are defined from the user's perspective, not the system's internals
- SLOs and error budget: the ship-vs-stabilize contract
- Alert on symptoms, not causes
- Multi-window burn-rate alerting vs. static thresholds
- Severity and routing follow the budget, not the dashboard
- Why paging on causes drowns out the pages that matter

## SLIs are defined from the user's perspective, not the system's internals

An SLI answers "was the user's request served correctly and fast enough," not "was CPU under 80%" or "did the queue stay short." The reason to insist on the user framing even when an internal metric correlates well in practice: internal metrics measure the system's convenience, not the user's experience, and the correlation between them silently breaks the moment the system changes — a new caching layer, a re-architected queue, a dependency swap — while the user's actual experience is unaffected by any of it. An SLI tied to what the user felt keeps working as the internals evolve; an SLI tied to an internal detail has to be re-derived every time that detail does.

## SLOs and error budget: the ship-vs-stabilize contract

An SLO sets the target (99.9% of requests succeed within 300ms, say) and the error budget is what's left over — the amount of failure the target already tolerates. The budget is a contract, not a report card: while budget remains, the team ships freely, including changes that carry some risk; once it's spent, the team stops shipping features and stabilizes until the budget recovers. The reason this needs to be an explicit, agreed contract rather than an implicit judgment call made per-incident: without it, "should we ship this" gets decided by whoever's loudest or most recently burned, which produces exactly the two failure modes a real contract prevents — shipping through an incident because nobody called it, or freezing indefinitely because nobody said when to resume.

## Alert on symptoms, not causes

Page a human only on user-facing pain — the SLO actively burning — never on every internal condition that might, eventually, turn into pain. A queue depth climbing, a cache hit rate dipping, a single replica's CPU spiking are all *possible causes*; none of them is guaranteed to reach the user, and plenty resolve themselves before they do. The reason to hold the line at symptoms: a cause-based alert fires on every internal fluctuation whether or not it ever affects anyone, and the team either learns to ignore it (see below) or spends on-call cycles chasing conditions that were never going to matter. A symptom-based alert fires exactly when, and only when, a user is or is about to be affected — which is the one condition actually worth waking someone up for.

## Multi-window burn-rate alerting vs. static thresholds

A static threshold ("alert if error rate > 1%") treats every crossing the same regardless of how fast the budget is actually being consumed, which forces a choice between two bad defaults: set it sensitive and get paged on brief, self-healing blips, or set it lax and miss a slow leak that quietly exhausts the whole month's budget before anyone notices. Multi-window burn-rate alerting fixes this by alerting on the *rate* at which the error budget is being consumed, checked across both a short window (catches fast, severe burns fast) and a long window (catches slow burns that a short window alone would treat as noise and dismiss). The reason both windows matter together: a short window alone pages on transient noise that recovers on its own, and a long window alone reacts too slowly to a burn severe enough to exhaust the budget in hours. Together, they page in rough proportion to how much budget is actually at stake and how urgently — fast severe burns page fast, slow burns page before the budget is gone rather than after.

## Severity and routing follow the budget, not the dashboard

An alert's severity — and who it pages — is set by how much error budget is at risk and how fast, not by which dashboard panel it happens to live on or how alarming the underlying metric looks in isolation. A burn rate that will exhaust the monthly budget in an hour is a page-now, wake-someone-up severity regardless of how the raw numbers look; a burn rate that would take three weeks to exhaust it is a ticket for business hours, even if the same underlying metric looks identical in a static view. Routing follows the same logic outward to ownership (see the SKILL.md's ownership checklist item): the team whose SLO is burning is who gets paged, not whichever team happens to own the component the dashboard highlights first.

## Why paging on causes drowns out the pages that matter

Every cause-based alert that fires without a user actually being affected trains whoever's on call to treat pages as noise — to glance, dismiss, and move on, because that's what the last twenty pages taught them to do. That training doesn't stay scoped to the noisy alerts; it generalizes to *all* pages, including the rare one that's a real, budget-burning symptom. A pager that's earned trust by only firing on real user pain gets acted on immediately; a pager that's cried wolf on internal fluctuations gets the same reflexive dismissal applied to the page that actually mattered — which is the entire mechanism by which alert noise turns into a missed incident, not a separate risk from it.
