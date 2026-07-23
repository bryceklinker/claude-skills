---
name: dependency-maintenance
description: "Use to update dependencies and tooling safely — the work dev-workflow deliberately excludes because it changes no product behavior. Trigger whenever bumping package/library versions, updating a lockfile, applying a security/CVE patch, upgrading a framework, runtime, or build tool, or resolving dependency drift. The discipline: one logical update per commit, read the changelog for breaking changes, and run the full unit AND acceptance suites after each so the existing tests prove nothing broke. Not for adding features or changing behavior (that's dev-workflow) — but if an upgrade forces code changes, that portion graduates into the strict-tdd cycle."
---

# Dependency Maintenance — update without breaking

## Why this exists

Upgrading a dependency changes no product behavior, so it doesn't belong in `dev-workflow` — there's nothing to design, decompose, or acceptance-test into existence. But "no new behavior" is not "no risk": a version bump can silently change an API, tighten a validation, shift a default, or drag in a transitive break. Ungoverned, these updates are where "nothing changed" outages come from. This skill is the lighter, separate lane for that work — disciplined enough to be safe, without the full feature pipeline it doesn't need.

The safety net here is the one the rest of the suite built: your **existing unit and acceptance tests**. A dependency update is exactly the moment they earn their keep — they're the proof that behavior survived the change.

## The core discipline

<HARD-GATE>
One logical update per commit, and the full unit AND acceptance suites green after each one. Never batch unrelated upgrades into a single commit — when something breaks two weeks later, a one-update-per-commit history is bisectable and a giant "bump everything" commit is not.
</HARD-GATE>

"One logical update" is usually one dependency, but may be a coherent group that must move together (a framework and its companion packages). The test is: could this unit be reverted on its own if it caused a regression?

## The loop, per update

1. **Know what's changing.** Read the changelog / release notes for the version range you're crossing — especially the **breaking changes** and **security advisories**. An upgrade you didn't read is a behavior change you didn't review. Note CVEs a security update closes.
2. **Apply one update.** Bump the single dependency (or the coherent group) and update the lockfile. Don't let the tool opportunistically bump neighbors — pin the scope.
3. **Run the full unit suite.** All of it, pristine output. A break here is the dependency telling you an assumption moved.
4. **Run the acceptance suite.** This is the step unit tests can't replace — it exercises the real deployment, real DB, and real integrations against the new versions, catching the wiring and runtime breaks a bump most often causes. If the feature has acceptance coverage (`acceptance-testing`), run it; if a touched flow has none, that gap is worth filling before trusting the upgrade.
5. **Confirm the build, lint, and format still pass** under the new versions — toolchain updates especially can shift these.
6. **Commit the single update** with a message naming the version delta and why (routine bump, security patch + CVE, unblock a feature).

## When an upgrade forces code changes

Sometimes a major bump changes an API you call, and the code must change to compile or pass. That portion is no longer pure maintenance — it's a behavior-adjacent change, and it **graduates into the strict-tdd cycle**:

- If existing tests now fail because the *contract* changed, adjust them deliberately (understand why the library changed the behavior; don't just make the test green).
- If you must write new adapter code against the new API, do it test-first via `strict-tdd`.
- Keep that code change in its own commit, separate from the mechanical bump, so the "update" and the "adapt to the update" are independently reviewable.

A large migration (a framework major, a runtime jump) that ripples through the codebase may be big enough to deserve the full `dev-workflow` treatment — intake its scope, plan the increments, do it in a worktree. Use judgment: a routine patch is this lane; a migration that reshapes code is the pipeline.

## Prioritization

- **Security patches first.** A CVE fix is not optional maintenance; treat it as urgent and note the advisory it closes.
- **Patch and minor** updates are low-risk — group-review them, but still one-per-commit for bisectability, and still run both suites.
- **Majors** get individual, deliberate treatment — they're the ones with the breaking changes that force code work.
- **Don't mix maintenance with feature work.** A dependency bump riding inside a feature commit hides both. Keep the lanes separate.

## Exit condition

Each update is its own commit with the changelog reviewed, the full unit and acceptance suites green against the new versions, and build/lint/format passing. Any upgrade that forced code changes was handled test-first and committed separately. Dependency drift is resolved without a single unexplained behavior change.
