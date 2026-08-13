# Promotion — build once, move the same artifact forward

The question promotion answers is simple: when code reaches production, is it the thing that was tested, or a thing that merely resembles it? Build once, promote the same artifact everywhere is the discipline that keeps the answer "the same thing" — because every rebuild is a chance for the artifact in production to diverge, invisibly, from the artifact every earlier stage vouched for.

## Table of contents
- Build once, identify by digest
- Promote the artifact, not the source
- What's allowed to differ per environment
- Never rebuild for prod
- Automated gates vs. human gates

## Build once, identify by digest

Produce the deployable artifact **exactly once per change**, during the pipeline's build stage, and give it an identity that can't silently change underneath it: a **content digest or a commit digest**, not a mutable tag like `latest` or even a branch-scoped tag that gets reassigned on every push.

The reason a digest matters and a tag doesn't: a tag is a pointer, and pointers move. If "the staging artifact" means "whatever `staging-latest` currently points to," that meaning changes the moment someone pushes again — the artifact you promote to prod later might not be the one that passed staging's tests earlier, even though the tag name never changed. A digest is a fixed fingerprint of the actual bytes; when you promote by digest, "this exact artifact passed every gate" is a claim that stays true no matter what else happens to the registry.

## Promote the artifact, not the source

Once built, that one artifact — identified by its digest — is what moves dev → staging → prod. Promotion is a **reference change** (pointing an environment's deployment at a given digest), not a rebuild, a re-checkout, or a re-run of the build stage against the same commit.

This is what makes the earlier pipeline stages meaningful. If staging tested digest `abc123` and production deploys a fresh build of the same source instead of `abc123` itself, then everything staging verified is a claim about a *different* artifact — same source, but potentially a different compiler version, a different dependency resolution, a different timestamp baked in, a different anything that build-time nondeterminism can introduce (see `reproducible-builds.md`). Promoting the literal artifact closes that gap: what staging verified is, byte for byte, what reaches users.

## What's allowed to differ per environment

Only **configuration and secrets** vary between dev, staging, and prod — and they're injected at deploy time from the environment (an environment variable, a mounted secret, a config service lookup), never baked into the artifact and never branched on inside the build. Database URLs, API keys, feature flag defaults, log levels: all environment concerns, all external to the artifact.

The reason the line is drawn exactly there: anything baked into the artifact at build time is, by definition, no longer something promotion can change — and build once forbids rebuilding to change it. If environment-specific values lived inside the artifact, "promote the same artifact" and "each environment needs different config" would be flatly incompatible. Keeping config and secrets external is what lets one immutable artifact legitimately serve three different environments without becoming three different artifacts in disguise.

## Never rebuild for prod

It follows directly from the above, but it's worth stating on its own because it's the mistake this convention exists to prevent: **production never gets its own build.** Not a "final" build, not a build with production flags baked in, not a rebuild-to-be-safe. If prod needs a different build than what staging tested, then staging never actually tested prod's artifact — it tested a stand-in, and every gate staging enforced was gating the wrong thing.

If a build step appears to legitimately need to differ for production, that's a signal the difference belongs in externally injected configuration instead of in the build — see the previous section. Escape hatch: the rare case where an artifact genuinely cannot be identical across environments (e.g., an architecture-specific binary matrix built once per target, not per environment) is still build-once *per target* — identify each target's artifact by its own digest and promote each one unchanged; it's not license to rebuild the same target per environment.

## Automated gates vs. human gates

Promotion between environments crosses a gate, and gates come in two kinds:

- **Automated gates** decide by objective, repeatable criteria — tests passed, a security scan came back clean, a health check went green. These should never wait on a human, because a human adds latency without adding judgment: the criteria are already fully specified, so a person is just re-running a checklist a machine runs faster and more consistently.
- **Human gates** exist where the decision genuinely requires judgment a machine can't encode — "is now a safe time to change what production-facing behavior users see," a compliance sign-off, a business-risk call given context outside the pipeline's view. Reserve human gates for decisions that actually need a human; a human gate that just rubber-stamps a checklist an automated gate could enforce is latency with no judgment attached, and it trains reviewers to click through without looking.

The promote-the-same-artifact rule applies identically on either side of a gate: whichever kind of gate approves the promotion, what moves forward across it is still the one artifact, unchanged, now pointed at by the next environment.
