# GitHub release process: conventional commits + git cliff

*Design spec — 2026-08-15*

## Purpose

This repo ships two plugins and has no release process. There are no git tags, no `.github/`
directory, and no CI of any kind. Versions live only in the plugin manifests and in two
hand-written `CHANGELOG.md` files, so there is no way for a consumer to point at a released
artifact, see what changed between two versions, or install a known-good revision.

This spec establishes tagged GitHub Releases for each plugin, with release notes generated
from conventional commits by [git cliff](https://git-cliff.org/).

## What exists today

- **Two independently versioned plugins in one repo:**
  - `craft-code` — lives at the repo root, manifest at `.claude-plugin/plugin.json`, currently `0.4.0`
  - `craft-ops` — lives in `craft-ops/`, manifest at `craft-ops/.claude-plugin/plugin.json`, currently `0.11.0`
- **A marketplace manifest**, `.claude-plugin/marketplace.json`, which pins the version of *both*
  plugins in its `plugins[]` array. Its own `metadata.version` (`0.1.0`) is not part of this design.
- **Two hand-written changelogs** — `CHANGELOG.md` and `craft-ops/CHANGELOG.md` — written in
  editorial prose (narrative paragraphs under a version heading), following Keep a Changelog loosely.
- **Commit history that already largely conforms** to conventional commits, with `(craft-code)` /
  `(craft-ops)` scopes on most plugin-specific work and bare `docs:` / `chore:` on repo-level work.
- **No tags, no workflows, no package manager, no Makefile.** Any tooling introduced must be
  dependency-free or installed by CI.

## Decisions

These were settled during brainstorming and are not open for re-litigation during implementation:

1. **Per-plugin releases.** Two independent release streams, not one repo-wide version.
2. **Manual dispatch.** Releases are cut by a human triggering a workflow, not automatically on merge.
3. **git cliff generates the GitHub Release body only.** The hand-written `CHANGELOG.md` files are
   untouched by any automation and keep their editorial voice.
4. **Commit-to-plugin attribution is by file path**, not by commit scope.
5. **Baseline tags are backfilled at the current versions only** — no archaeology over past versions.
6. **Conventional commits are enforced by a local `commit-msg` git hook**, not by CI.
7. **The human owns version bumps.** The workflow reads the version off `main` and releases it; CI
   never commits to `main`.

## Tag scheme

```
craft-code-v<major>.<minor>.<patch>
craft-ops-v<major>.<minor>.<patch>
```

Annotated tags. The `-v` infix keeps the two streams unambiguous under a glob and lets git cliff
select a stream with `--tag-pattern 'craft-ops-v.*'`.

## Components

### 1. `cliff.toml` (repo root)

A single shared config. Stream selection happens on the command line, not in the config, so one
file serves both plugins.

**`[git]` settings:**
- `conventional_commits = true`, `filter_unconventional = true` — anything that doesn't parse is
  dropped rather than dumped into a catch-all group.
- `commit_parsers` grouping into: **Features** (`feat`), **Bug Fixes** (`fix`), **Documentation**
  (`docs`), **Refactoring** (`refactor`), **Performance** (`perf`), **Chores** (`chore`, `build`, `ci`).
- Skip rules for merge commits (`^Merge`), `chore(release)` commits, and `test` commits — the last
  is a valid type the hook accepts, but test-only changes are not release-note material.
- Breaking changes (`!` marker or `BREAKING CHANGE:` footer) surface in their own section at the top.

**`[changelog]` template:** emits the release-note body only. No document header, no repeated
version title — GitHub renders the tag name as the release title, so duplicating it in the body is
noise. Each entry is a bullet with the commit subject and a short SHA link.

**Invocation per stream:**

```sh
# craft-ops — only commits touching craft-ops/
git cliff --config cliff.toml \
  --tag-pattern 'craft-ops-v.*' \
  --include-path 'craft-ops/**' \
  --unreleased --tag craft-ops-v<version>

# craft-code — everything except craft-ops/
git cliff --config cliff.toml \
  --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' \
  --unreleased --tag craft-code-v<version>
```

`--tag-pattern` restricts which tags cliff considers when resolving `--unreleased`, so each stream
computes its range from its own most recent tag.

**Known consequence, accepted deliberately:** because `craft-code` occupies the repo root, its
exclude-based filter sweeps in repo-level commits — `README.md`, `PRINCIPLES.md`, `docs/`, `tools/`,
`.github/`, `cliff.toml` itself. This is intended: those changes ship as part of the craft-code
release. Commits touching *both* trees appear in both streams' notes.

### 2. `.github/workflows/release.yml`

Trigger: `workflow_dispatch` with a single input.

| Input | Type | Values |
|---|---|---|
| `plugin` | choice | `craft-code`, `craft-ops` |

There is no version input. The version comes from the manifest on `main`.

Permissions: `contents: write` (needed to push the tag and create the release). Nothing more.

**Steps, in order:**

1. `actions/checkout` with `fetch-depth: 0` — full history and tags are required for cliff.
2. **Resolve the manifest path** for the selected plugin:
   - `craft-code` → `.claude-plugin/plugin.json`
   - `craft-ops` → `craft-ops/.claude-plugin/plugin.json`
3. **Read the version** from that manifest with `jq`.
4. **Guard — manifest consistency.** Read the same plugin's entry from
   `.claude-plugin/marketplace.json` and fail if its `version` differs from the plugin manifest's.
   A mismatch means an incomplete bump, and releasing it would publish a version the marketplace
   doesn't serve.
5. **Guard — tag uniqueness.** Fail if `<plugin>-v<version>` already exists. Re-dispatching after a
   successful release must not silently move a tag or double-publish.
6. **Install git cliff** (pinned version).
7. **Generate notes** using the stream's invocation above, writing to a file.
8. **Guard — non-empty release.** Fail if the generated notes contain no entries. There is nothing to
   release, and an empty release page is worse than no release.
9. **Create and push the annotated tag** at the checked-out commit.
10. **Publish** with `gh release create <tag> --title <tag> --notes-file <file>`.

Guards 4, 5 and 8 all run before step 9, so a rejected dispatch pushes nothing and leaves no partial
state to clean up.

### 3. `.githooks/commit-msg`

POSIX `sh`, no dependencies. Validates the commit subject line against:

```
<type>(<optional scope>)<optional !>: <description>
```

Allowed types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`, `revert`.

**Passes through without validation:** merge commits (`Merge …`), git's auto-generated revert
subjects (`Revert "…"`), and `fixup!` / `squash!` subjects — these have git-defined formats the
grammar doesn't cover. A hand-written `revert:` subject still validates as a normal type.

**On rejection:** print the offending subject line, the expected grammar, and the allowed type list,
then exit non-zero.

Git does not clone hooks, so the hook requires one-time opt-in per clone:

```sh
git config core.hooksPath .githooks
```

**Limits, stated plainly:** the hook is bypassable with `--no-verify` and is absent in any clone that
never ran the config line. It is a discipline aid, not a gate. Malformed commits that reach `main`
are silently dropped from release notes by `filter_unconventional`. If that drift ever shows up in
practice, a CI-side check is the backstop — explicitly out of scope for this spec.

### 4. `docs/releasing.md`

Covers: the commit grammar and allowed types; the `core.hooksPath` install line; how to cut a
release (bump the manifests and changelog, merge, dispatch the workflow); and how to preview notes
locally (`brew install git-cliff`, then the invocations above).

### 5. Baseline tags

Tag the current `main` `HEAD` as both `craft-code-v0.4.0` and `craft-ops-v0.11.0`, and push them.

**No GitHub Releases are attached to these tags.** They exist solely as the range baseline so that
the first real release of each plugin generates bounded notes instead of sweeping in the repo's
entire history.

## The release flow, end to end

1. Work merges to `main` with conventional-commit subjects.
2. When ready to ship, the human bumps in one normal commit: the plugin's `plugin.json`, that
   plugin's entry in `marketplace.json`, and a hand-written `CHANGELOG.md` entry.
3. That commit reaches `main`.
4. The human dispatches `release.yml` with the plugin name.
5. The workflow validates, generates notes, tags, and publishes.

## Verification

Per the repo's own principles, each piece is verified by running it and reading real output — not by
inspection.

- **`commit-msg` hook** — a shell test file exercising accept and reject cases: each allowed type,
  scoped and unscoped, the `!` breaking marker, merge/revert/`fixup!` pass-through, and malformed
  subjects (missing colon, unknown type, empty description). Run it and read the results.
- **`cliff.toml`** — run both stream invocations locally against real history with the backfill tags
  in place, and read the generated markdown. Confirm grouping, path filtering, and merge-commit
  exclusion behave as specified.
- **`release.yml`** — verified by cutting a real release: a `craft-ops` patch, dispatched for real,
  with the published GitHub release page read to confirm the tag, title, and notes body.

## Out of scope

- CI validation of commit messages (the local hook is the chosen mechanism).
- Automatic version bumping or bot commits to `main`.
- Releasing or tagging the `craft-marketplace` umbrella version.
- Backfilling tags or releases for historical versions.
- Publishing anywhere other than GitHub Releases.
