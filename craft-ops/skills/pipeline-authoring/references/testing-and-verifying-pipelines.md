# Testing and Verifying Pipelines

A pipeline and its scripts are tested by running them. The question isn't "do the functions return the right values in isolation" but "does this step do its job when the pipeline calls it." That question can only be answered by executing it.

## Run each script through the entrypoint the pipeline uses

Invoke every script exactly as the pipeline does — `./ci/deploy.sh`, `python -m ci.promote`, `mytool generate` — against a real or throwaway target, and observe that it did its job: the image exists in the registry with the expected digest, the version string is right, the policy check rejects a deploy it should reject. Use a scratch registry, tag, or target, or the script's own `--dry-run` where a real run would touch production.

Running the real entrypoint catches what a separate unit suite never would: a wrong module name, a broken argument parser, a renamed file, a missing executable bit, a credential the script expects but the pipeline doesn't pass.

## Run the pipeline against a test artifact

Trigger the real definition on a scratch branch or disposable tag and record what happened:

- which stages ran, in what order;
- that a gate meant to block actually blocks — make the check fail and watch promotion stop;
- that the artifact promoted is the digest that was built.

A gate never seen rejecting anything is an assumption. When no runner is available, the minimum is the CI system's own lint or validation of the definition plus every script run locally through its entrypoint; name the full run as unverified.

## When a script earns a unit test

Most pipeline scripts drive external systems — the registry, the CI API, a deploy target. A unit test for them mostly mocks those systems and asserts the script calls the mocks, which proves little and costs maintenance. Skip it.

Write a test when a script holds decision logic with more cases than running it covers cheaply: a version computation with several branches, a parser of tool output with real edge cases, a policy with many conditions. Keep that logic in a pure function so the test needs no mocks, and build it with craft-code's `strict-tdd` where installed. The script is still proven by running it.
