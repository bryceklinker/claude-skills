# Trigger evals: does the description make Claude load the skill?

A skill's `description` decides when it fires. These evals measure that
directly: each query in `sets/<skill>.json` runs in a fresh, empty project with
the description installed as a project command, and a run counts as a trigger
if the model invokes it within the first few turns. Negative queries (the
`should_trigger: false` ones) are as important as positive ones; they guard the
"Not for…" clauses that stop overlapping skills stealing each other's requests.

```sh
# one skill
python3 run.py --eval-set sets/strict-tdd.json --skill-path ../../skills/strict-tdd

# A/B every skill against another checkout (e.g. a worktree of main); resumable
./ab.sh <baseline-root> <out-dir> [skill ...]
```

Each query runs 3 times by default; it passes when its trigger rate lands on the expected side of 0.5.

## Reading the numbers

- **Noise.** At 3 runs per query, an unchanged description moves by up to 1–2 queries between runs. Treat a difference of 2 or less as noise.
- **A miss means the model chose not to load it.** Usage limits and auth errors are retried (up to `--max-wait-hours`), and a run that never completes fails loudly instead of being scored as a miss.

## Why it's built this way

Three measurement bugs in the earlier harness made every skill look like it had about one-third recall:

1. **Isolation.** Parallel runs shared one `.claude/commands/`, so the model saw several identical copies of the skill and often picked another run's copy. Each run now gets its own temporary project.
2. **Explore-first models.** It scored a miss whenever the first tool call wasn't the skill. Current models often look around first, so the whole first `--max-turns` (default 4) now counts.
3. **Throttling.** Usage-limit and timeout errors were scored as misses.

Results measured before these fixes (before 2026-10-30) aren't comparable.
