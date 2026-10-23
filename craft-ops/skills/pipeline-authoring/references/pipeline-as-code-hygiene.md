# Pipeline-as-Code Hygiene

Each rule, and the failure it prevents.

- **Script files over inline scripts.** A step that branches, loops, parses output, or makes more than a one-line decision lives in a version-controlled script the pipeline calls. Inline shell can't be run locally without copying it out of the YAML, can't be linted with the rest of the code, buries the pipeline's control flow, and mixes wiring changes with behavior changes in one diff. A script can be run on its own, which is how it's proven (`testing-and-verifying-pipelines.md`). A straight-line one-liner can stay inline; a script per trivial command is its own clutter.
- **Build once, promote the same artifact.** One build stage, one digest, and every later environment references that digest. Every test, gate, and approval is a claim about that artifact; a rebuild makes them claims about something else.
- **Pin every tool version** — compilers, runtimes, base images, actions, plugins. A floating version changes the build with no commit to explain it.
- **Hermetic and idempotent steps.** Each run starts from a fresh environment, and re-running a step after a failure succeeds without manual cleanup. A step that relies on leftovers from a previous run works by accident.
- **No secrets in the definition, its scripts, or the artifact.** Inject them at run time. Anything committed is visible to every reader and permanent in history.
- **No duplicated stage logic.** Repeated logic lives in one script or reusable job; copies drift when one is fixed and the other isn't. But a template or reusable workflow for something used once is indirection with no payoff.
- **Stages in the order the design settled**, halting on first failure. If authoring wants a different order, reconcile with the design rather than keeping whichever was easier to write.
- **Reviewed like code.** The definition and every script go through the same pull-request review as the application. A pipeline edited outside review makes every other rule here optional.
