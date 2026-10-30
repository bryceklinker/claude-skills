# Testing and Verifying Observability

Observability is tested by watching it work against real or synthetic signals. A dashboard's or alert rule's only behavior is what it makes the metrics store, query engine, and alerting backend do; a test that mocks the backend passes even when a panel points at a renamed metric or a rule filters on a label that's never emitted.

## The always-runnable minimum

Validate rules and dashboards with the backend's own tools (`promtool check rules`, `amtool config check`, the dashboard tool's lint), and run any generator or lever script through the exact entrypoint the pipeline or deploy step calls. That catches malformed rules, invalid queries, undefined datasources, and wrong module paths with no live signal.

## Queries resolve to real data

Run each dashboard query against the real store and confirm it returns series. A query that silently returns nothing looks identical to "all quiet."

## Prove the alert fires — and stays quiet

An alert isn't verified until it has been fired against a synthetic or replayed signal that should trip it, and seen to transition to firing. Then confirm it stays quiet on a healthy signal. Reading the expression doesn't reveal that the label doesn't match what the metric emits, that the evaluation window is shorter than the scrape interval, or that the query returns no series instead of zero. Firing it does.

## Prove the lever flips

Change each runtime lever and observe the emitted signals change without a redeploy, and observe the revert bring them back down.

## When a computation earns a unit test

Generators and lever toggles mostly assemble config; run them and inspect the output rather than unit-testing them. A burn-rate or SLO computation with real edge cases — an empty window, a missing data point, a rate flapping at the boundary — can earn a small test as a pure function, built with craft-code's `strict-tdd` where installed. The alert built on it is still proven by firing it.
