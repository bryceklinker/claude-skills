# Testing and Verifying Rollouts

A rollout is tested by rolling out. Its manifest's only behavior is what it makes the progressive-delivery controller, the metrics provider, and the traffic layer do; a test that mocks the controller passes even when a gate points at the wrong metric or a step has the wrong weight.

## The always-runnable minimum

Validate the rollout manifest against the controller's schema, use the controller's dry-run where it has one, and run every deploy or gate script through the exact entrypoint the rollout calls (`./gate.sh`, `python -m rollout.promote`). That catches malformed fields, references to steps or templates that don't exist, wrong module paths, and broken argument parsing — without a cluster or traffic. When this is all you can run, say what remains unproven.

## Run the rollout in a test environment

Observe three outcomes, in an environment shaped enough like production to trust:

1. **Progress** — the canary's weight advances through its steps on a healthy signal.
2. **Halt** — make the metric bad and watch progression stop. A gate never seen halting anything is an assumption.
3. **Rollback** — trigger it and confirm the system lands on the prior known-good version.

The forward path succeeding a hundred times says nothing about a rollback run zero times; they exercise different code, different state, and different compatibility assumptions. A rollout isn't verified until its rollback has run.

## When a gate script earns a unit test

Most deploy scripts drive the controller or cluster; a unit test for them would mock those and prove little. Skip it. A gate script whose threshold logic has real edge cases — a value exactly at the boundary, a missing or delayed data point, a metric flapping within one window — can earn a small test of that logic as a pure function, built with craft-code's `strict-tdd` where installed. The gate is still proven by halting a real rollout.
