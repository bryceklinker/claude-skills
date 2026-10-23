# Observability-as-Code Hygiene

Each rule, and the failure it prevents. Tools named are examples; the rules apply to any stack.

- **Dashboards and alerts as code, never click-ops or copy-paste.** A UI-built dashboard lives in one person's session; a copied alert threshold drifts from its sibling the first time the service changes. Declared or generated once, in the repo, they get a reviewable diff, a history of why thresholds changed, and one source every environment renders from.
- **One shared instrumentation helper where the same fields are emitted in many places.** Ad hoc calls drift — one service tags a field the others don't, names diverge. Introduce the helper when the repetition exists, not in anticipation.
- **Runtime levers wired for real.** Verbosity, sampling, and trace detail are runtime config or flags, not build-time constants, with a default setting, an incident setting with its own cost and cardinality ceiling, and an automatic revert (a TTL, a scheduled reset, a step in incident close). Detail has to move faster than a deploy, and elevated detail left on quietly multiplies the bill.
- **Alert on symptoms, not causes.** Page on what users or the SLO experience — error rate, latency, saturation, burn — not on a queue spike or a pod restart that may never reach a user. A pager that fires on causes trains people to ignore it.
- **Bounded cardinality.** Every metric label has a small, enumerable value set decided at authoring time. User IDs, raw URL paths, request and session IDs go in logs or traces, or get templated or bucketed. Unbounded labels look fine locally and break the metrics store in production.
- **No secrets in dashboard, datasource, or alert config.** Reference credentials and token-bearing webhook URLs by indirection resolved at deploy time; these files don't look like they hold secrets, which is why they leak.
