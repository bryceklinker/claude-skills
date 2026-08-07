# Reproducible Builds — same input, same artifact

Promotion (see `promotion.md`) rests on a single artifact carrying its verdict from staging to prod unchanged. That only means something if "build this commit" is a deterministic function — same input, same artifact, every time. If two builds of the same commit can produce different bytes, then the digest you promoted stops being proof of anything: rebuilding to "double-check" or to recover from a lost artifact might silently hand you something that behaves differently than what was actually tested. Reproducibility is the property that makes the artifact's identity trustworthy in the first place.

## Table of contents
- Same input, same artifact
- Pin the toolchain and dependencies
- Isolated, ephemeral build environments
- No network-dependent or wall-clock-dependent steps
- Why this makes promotion and rollback trustworthy

## Same input, same artifact

The standard: given the identical source at a given commit, the build produces byte-identical (or behaviorally identical, where the toolchain can't guarantee bit-for-bit output) output, regardless of when it runs, which machine it runs on, or what else that machine has done recently. This is a stronger property than "the build succeeds" — a build can succeed every time and still be non-reproducible if what it produces quietly varies run to run.

Non-reproducibility isn't usually a single dramatic bug; it's an accumulation of hidden inputs the build silently depends on beyond the source tree: an unpinned dependency resolving to whatever version is newest today, a build tool reading the ambient system clock, a step that reaches out to the network and gets a different answer depending on when it asks. Each of the sections below closes off one category of hidden input.

## Pin the toolchain and dependencies

Every compiler, runtime, package manager, and third-party library the build touches should be pinned to an exact version — not a floating range, not "latest," not "whatever's on the runner's image today." That includes transitive dependencies, resolved and locked, not re-resolved on every run.

The reason: an unpinned dependency is a hidden build input that changes without a corresponding source change. A build that resolves "the latest compatible version" of a library can produce a different artifact from the identical commit two days apart, purely because the library's maintainer shipped a patch release in between — with no change to your source, no code review, and no record in your commit history explaining why the artifact is different. Pinning makes every input to the build traceable to a change someone actually reviewed.

## Isolated, ephemeral build environments

Build in an environment provisioned fresh for that build and discarded afterward — a container or VM spun up from a known base image, not a long-lived build server that accumulates state (leftover caches, manually installed tools, prior builds' artifacts) across runs.

The reason: a long-lived build machine is itself an unpinned, undocumented dependency. If a build only succeeds because someone once ran an extra setup step on that specific machine three years ago, the build isn't reproducible — it's dependent on an environment nobody can recreate on demand, including the CI vendor's own replacement hardware after an outage. An ephemeral environment forces every real dependency to be declared and pinned (per the previous section) because nothing is available unless it was explicitly provisioned for this run; there's no ambient machine state left over to lean on by accident.

## No network-dependent or wall-clock-dependent steps

Two categories of hidden input deserve calling out on their own, because they're easy to introduce without noticing:

- **Network-dependent steps** — fetching a dependency without a pinned version and lockfile-verified checksum, calling out to a live service during the build, resolving "latest" from a registry at build time. Even with everything else pinned, an unverified network fetch means the artifact depends on what a remote server happens to hand back today, which is outside your control and outside your repo's history.
- **Wall-clock-dependent steps** — embedding the current timestamp, the build date, or "days since epoch" logic into the artifact or its metadata in a way that affects its content or digest. Rebuilding the identical commit a minute later then produces a different artifact for no reason connected to the code at all.

Where a build genuinely needs external data (fetching a dependency, for instance), pin it by version *and* verify it by checksum or lock hash, so "the same input" includes a verifiable guarantee that the network handed back the same bytes — not just an assumption that it did.

## Why this makes promotion and rollback trustworthy

Two things downstream depend entirely on reproducibility holding:

- **Promotion** (`promotion.md`) claims that the artifact staging tested is the artifact prod runs, identified by a digest that doesn't change. That claim only has teeth if the same commit reliably produces the same digest — otherwise "promote by digest" degrades into "promote by digest, assuming this build happened to come out the same as last time," which is exactly the unreliable guess the digest was supposed to eliminate.
- **Rollback** means redeploying a *previous* artifact, not rebuilding the previous commit. If builds were non-reproducible, "roll back to last week's version" would mean re-running a non-deterministic process against old source and hoping the result behaves like what was actually running last week — reintroducing, at the exact moment you need certainty most (an incident), the same uncertainty reproducibility exists to remove. A reproducible build pipeline means the old artifact is still sitting in the registry, byte-identical to what was live, ready to redeploy with no rebuild and no guesswork.

Reproducibility is invisible when it's working — every build just quietly succeeds and matches. It becomes visible, expensively, the first time someone needs to trust an old artifact or explain why two builds of "the same" commit behave differently. Pin the toolchain, isolate the environment, and cut the hidden inputs before that moment arrives, not after.
