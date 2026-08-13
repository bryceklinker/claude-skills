# Signals & Cardinality — instrument for the questions you'll ask under pressure

What gets emitted decides what can be answered later, and that decision is made once, at instrumentation time, long before anyone knows which specific question a future incident will actually ask. This reference is about making that bet well: emit signals structured and correlated enough to answer questions nobody's asked yet, while treating the volume and shape of what's emitted as a budget that has to be spent deliberately, not a free good.

## Table of contents
- Structured, wide events over sparse logs
- Correlation: trace/request IDs and consistent high-cardinality fields
- Instrument for the questions you'll ask under pressure
- Cardinality and retention are a budget
- Sampling: head vs. tail
- Aggregation: what survives after sampling

## Structured, wide events over sparse logs

A single wide, structured event per unit of work — one request, one job, one message processed — carrying every field known about it (route, tenant, version, duration, outcome, the parameters that mattered) beats a scattering of narrow, unstructured log lines emitted at various points during that same unit of work. The reason: a sparse log line answers only the question its author anticipated when they wrote it, and reconstructing anything else means grepping across multiple lines, hoping they can be correlated, and parsing free text that was never meant to be queried. A wide structured event is queryable on every field it carries, including combinations nobody anticipated at instrumentation time — which is exactly the property that matters, because the question asked mid-incident is rarely the one anyone thought to log for in advance.

## Correlation: trace/request IDs and consistent high-cardinality fields

Every signal — event, log, span — needs a request or trace ID that's generated once at the edge and threaded through every service and hop the request touches, plus a consistent, shared set of high-cardinality fields (tenant, version, route) present on *every* signal, using the same field names and value formats everywhere they appear. The reason both parts matter together: the trace ID lets a single request be followed across service boundaries — essential when the cause of a symptom in one service is a change in another — while the shared fields let signals from *different* requests be sliced and joined by the dimension an incident actually turns on (this tenant, this version, this route), not just chained one request at a time. Inconsistency defeats both: a trace ID that a downstream service drops breaks the chain at that hop, and a field that's `tenant_id` in one service and `tenantId` in another can't be joined without someone noticing the mismatch and writing a workaround, usually mid-incident.

## Instrument for the questions you'll ask under pressure

Choose what to emit by asking, concretely, "what would I need to know to diagnose a regression in this code path" — not by emitting whatever a library defaults to or whatever's cheap to add. A dashboard built for calm days, showing aggregate throughput and average latency, answers "is everything fine" but not "which tenant, which route, which version is actually broken right now" — and the second question is the one that gets asked at 3 a.m., not the first. The reason to front-load this thinking rather than adding fields reactively during incidents: every field added *after* an incident because it was missing is a field that couldn't help with *that* incident — it only pays off the next time, if there is one, and if it's the same question. Instrumenting for the question in advance is the only way the signal exists when the question is actually asked.

## Cardinality and retention are a budget

Every field added to a signal, especially a high-cardinality one (user ID, request ID, a free-text parameter), multiplies the number of distinct time series or the storage a backend has to index and keep — and every day a signal is retained multiplies that cost by however long it's kept. The reason to treat this explicitly as a budget rather than emitting everything and letting the bill sort itself out: cardinality and retention costs don't fail loudly at the moment they're incurred — they accumulate silently, field by field and day by day, until a bill or a backend performance cliff makes the accumulated cost visible all at once, long after any single addition that caused it. Deciding, per signal, what's worth its cardinality cost and how long it earns its retention cost — rather than defaulting to "keep everything, forever, at full detail" — is what keeps the budget from being spent by default instead of by decision.

## Sampling: head vs. tail

**Head sampling** decides whether to keep a trace or event at the moment it starts, before its outcome is known — cheap and simple, but it samples uniformly, which means it's exactly as likely to discard the one request that was about to fail as the thousand that were about to succeed. **Tail sampling** waits until a request or trace completes, then decides whether to keep it based on what actually happened — which lets it deliberately over-keep errors, slow outliers, and anything else that turned out to be interesting, while still discarding routine, healthy traffic at a high rate. The reason tail sampling is usually worth its added complexity and buffering cost for anything used to diagnose incidents: a uniform head-sampled rate applied to a low-frequency failure mode can sample it into invisibility — exactly the case an incident needs to see. Head sampling stays the right, cheaper choice for high-volume signals where the interesting property isn't "did this one fail" but an aggregate that survives sampling regardless of which individual events were kept — which is what aggregation, below, is for.

## Aggregation: what survives after sampling

Pre-aggregated metrics — counts, rates, percentile histograms — computed from the full, unsampled stream before any sampling decision is applied, are what preserve accurate answers to "how many" and "what's the distribution" even when the underlying raw events are heavily sampled or short-retained. The reason aggregation and sampling have to be paired rather than choosing one alone: raw events, kept at high fidelity, answer "show me this specific request" but get prohibitively expensive to retain at full volume for long, while aggregates stay cheap to keep for months but can't be drilled into for one specific request. Computing aggregates from the full stream and applying sampling only to the raw events they're derived from gets both: trend and distribution questions stay answerable indefinitely and cheaply, while the sampled raw events remain available to drill into the specific requests sampling decided were interesting enough to keep.
