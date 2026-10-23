# Rollout Authoring Hygiene

Each rule, and the failure it prevents.

- **Rollback is authored and exercised first.** Trigger the undo in a test environment and watch it land on the prior version before the forward path gets real traffic. A rollback that exists only as YAML is like a backup never restored from: the moment you need it is when you learn the previous config drifted or a migration isn't reversible. This rule outranks the rest — they make a good rollout; this one makes a survivable one.
- **Gate and promotion logic is visible and runnable.** Put thresholds and promote/halt decisions in the controller's analysis config or a script the rollout calls, in one reviewable place — not scattered through inline manifest fields where a changed threshold is invisible in the diff. That keeps the logic runnable on its own against a recorded signal.
- **Health gates are objective thresholds** — error rate, latency, saturation, a business metric — evaluated automatically. A person glancing at a dashboard is unrepeatable and leaves nothing to review. Prove the gate by feeding it a bad signal and watching it halt.
- **Deploy decoupled from release.** Ship dark — behind a flag or at zero traffic — and flip exposure as a separate, deliberate decision. Otherwise every deploy carries release risk, and there's no window to smoke a build before users see it.
- **No secrets in the config.** Manifests, flag config, and scripts reference secrets by indirection resolved at deploy time.
- **Honor the compatibility window through the whole transition.** Old and new versions coexist for the length of the canary, so every step — not just the final state — must respect the expand-contract or N-1 decision the design made.
- **Idempotent and re-runnable.** Rollouts fail partway for reasons unrelated to the release; a re-run must not re-promote, re-migrate, or re-notify. Check current state before acting, and make flag changes a set, not a toggle.
- **Only the mechanism the risk needs.** Not every release needs rings, flags, and automated analysis; add what the design called for and nothing more.
