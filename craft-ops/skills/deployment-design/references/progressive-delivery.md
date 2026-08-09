# Progressive Delivery — widen the blast radius only on a healthy signal

Every rollout strategy answers the same question differently: how many real users hit the new version before you know whether it's safe? A release flipped everywhere at once bets the entire outcome — and every user's experience — on the very first observation. Progressive delivery replaces that bet with a sequence: expose a little, observe, widen only when the observation is good. Canary, blue-green, rolling, and rings are different mechanisms for the same discipline — which one your tooling calls it matters less than whether the discipline is actually followed.

## Table of contents
- Four shapes of rollout, and what decides between them
- Widening on a healthy signal, not on a timer
- Health-gated promotion: the gate is a machine check, not a human
- You can only gate on signals that already exist

## Four shapes of rollout, and what decides between them

**Canary** routes a small, growing slice of real traffic — a percentage, a single instance, a subset of requests — to the new version alongside the old, widening the slice as confidence grows. It fits stateless or near-stateless services where traffic can be split at a fine grain without breaking session affinity, and it's cheap because it doesn't need a full second environment — just enough new-version capacity to absorb the initial slice.

**Blue-green** runs two complete environments at full scale, old (blue) and new (green), and cuts traffic from one to the other in a single switch — often at a load balancer or DNS layer — while keeping the old environment warm as an instant rollback target. It fits changes where a clean, all-or-nothing cutover matters more than gradual exposure: a breaking wire-protocol change, a cache or connection pool that can't safely be shared between old and new code at the request level. The cost is real: a full second environment running concurrently, even if only for the cutover window.

**Rolling** replaces instances a batch at a time — old drains, new comes up, the next batch follows. It fits horizontally scaled, stateless compute and is the cheapest of the four because it reuses existing capacity rather than standing up a parallel environment. The trade is control: which user lands on old or new code is a function of which instance answers their request, not a deliberate percentage or cohort, and a full rollback means reversing the same batch-by-batch replacement, which is slower than blue-green's single switch.

**Ring-based** rollout expands by population — internal/dogfood first, then a beta cohort, then everyone — rather than by random percentage. It fits changes best validated by a specific population that can be reasoned about (employees who report issues through internal channels before customers ever see the change; a tenant, region, or account tier whose traffic can be attributed by identity rather than split at random). The cost is mostly organizational: maintaining ring membership and the channels that get feedback back from an inner ring before it widens.

Pick the shape the change's traffic shape, statefulness, and budget for a second environment actually justify — not whichever one shows up first in the platform's documentation.

## Widening on a healthy signal, not on a timer

Widen the population or percentage only when the current step has stayed healthy for the observation window it needs — never because a fixed amount of wall-clock time has simply elapsed. A timer measures how long the rollout has been running, not whether the new version is actually behaving; if the signal that would reveal a problem needs more traffic volume or more elapsed time to surface than the timer's default, the rollout promotes past the evidence, not on it. Blast radius should step no faster than the gate at the current radius can actually confirm.

## Health-gated promotion: the gate is a machine check, not a human

Promotion and abort are automated decisions, triggered off objective, pre-declared signals — error rate, latency (p95/p99), saturation (CPU, memory, queue depth), a key business metric — against thresholds set before the rollout starts. "Someone is watching a dashboard and it looks fine" is not a gate. The reason: human attention degrades with time, distraction, and fatigue, and a live rollout is exactly the moment attention is most likely to be split across something else. A machine check applies the same threshold at 3pm and at 3am without needing to remember to look, and it removes the lag between "the signal crossed the line" and "a person noticed, decided, and acted" — lag during which more users are exposed to the regression every second it persists.

## You can only gate on signals that already exist

The observability a rollout will gate on has to be built, wired to the right version, and validated *before* the rollout — not bolted on after a problem is suspected. A gate that checks a metric which doesn't exist, isn't split by version, or lags by minutes isn't a gate; it's a hope wearing a gate's clothes, and the gap gets discovered at the worst possible time — mid-incident, when the rollout has already progressed on the strength of a check that was never really watching. If the signal that matters can't be observed yet, the honest move is either to gate on a coarser signal that does exist, or to invest in the missing observability before this rollout — not to design a gate that assumes visibility the system doesn't have.
