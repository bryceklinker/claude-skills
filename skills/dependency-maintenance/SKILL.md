---
name: dependency-maintenance
description: "Use to update dependencies and tooling safely — the work dev-workflow deliberately excludes because it changes no product behavior. Trigger whenever bumping package/library versions, updating a lockfile, applying a security/CVE patch, upgrading a framework, runtime, or build tool, or resolving dependency drift. The discipline: one logical update per commit, read the changelog for breaking changes, and run the full unit AND acceptance suites after each so the existing tests prove nothing broke. Not for adding features or changing behavior (that's dev-workflow) — but when an upgrade forces code changes, reimplements a dropped dependency in-house, or surfaces a latent bug, that portion escalates into strict-tdd or the full dev-workflow rather than hiding inside the bump commit."
---

# Dependency Maintenance

A version bump adds no behavior but can still change an API, tighten a validation, or shift a default. The existing unit and acceptance suites are the safety net; this lane is how you lean on them.

## Per update

1. **Read the changelog** for the version range — breaking changes and security advisories especially.
2. **Apply one logical update** — one dependency, or a group that must move together — and update the lockfile. Don't let the tool bump neighbors.
3. **Run the full unit suite, then the acceptance suite** (`commands.test`, `commands.acceptance`). The acceptance suite catches the wiring and runtime breaks bumps most often cause; if a touched flow has no coverage, that's worth filling first.
4. **Confirm build, lint, and format** still pass (`commands.build`, `commands.lint`, `commands.format_check`).
5. **Commit that one update**, naming the version delta and why (routine, CVE, unblocking a feature).

One update per commit keeps history bisectable and each update independently revertible. Security patches first; majors one at a time. Keep maintenance out of feature commits.

Before adding a new dependency, check whether the platform or an existing dependency already covers the need; each one is code you now maintain.

## Escalate, don't smuggle

- **The upgrade forces code changes** → that part goes through `strict-tdd`, in its own commit separate from the bump. If tests fail because the contract changed, understand why before adjusting them.
- **You're replacing a dropped dependency with your own code** → that's a feature with behavior parity as its criterion: full `dev-workflow`.
- **The upgrade surfaces a latent bug** → `systematic-debugging`, then `strict-tdd`, as its own change. A fix hidden in a bump commit can't be reviewed or bisected.

A migration that reshapes the codebase (a framework major, a runtime jump) may deserve `dev-workflow` as a whole.

## Exit condition

Each update is its own commit with its changelog read and both suites, build, lint, and format green; any forced code change went through `strict-tdd` separately.
