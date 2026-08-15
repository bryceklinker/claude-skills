# Releasing

Each plugin releases on its own cadence, with its own tag stream and its own
GitHub Releases:

- `craft-code` → `craft-code-vX.Y.Z`
- `craft-ops` → `craft-ops-vX.Y.Z`

Release notes are generated from conventional commits by
[git cliff](https://git-cliff.org/). The hand-written `CHANGELOG.md` files are
**not** generated — they stay editorial prose and are updated by hand.

## Commit grammar

```
<type>(<optional scope>)<optional !>: <description>
```

Allowed types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`,
`build`, `ci`, `revert`.

Scope is conventionally `craft-code` or `craft-ops`, but attribution to a
release stream is by **file path**, not by scope — see below.

### Enable the hook

Git does not clone hooks, so each clone opts in once:

```sh
git config core.hooksPath .githooks
```

This activates `.githooks/commit-msg`, which rejects subjects that do not
parse. It is a discipline aid, not a gate: it is bypassable with `--no-verify`
and absent in any clone that never ran the line above. A subject that does not
parse is silently dropped from the release notes.

Run its tests with:

```sh
tools/hook-tests/commit-msg-test.sh
```

## How commits map to a plugin

- `craft-ops` notes = commits touching `craft-ops/**`
- `craft-code` notes = commits touching anything else

Because `craft-code` lives at the repo root, root-level changes (`README.md`,
`PRINCIPLES.md`, `docs/`, `tools/`, `.github/`, `cliff.toml`) belong to the
`craft-code` stream. A commit touching both trees appears in both.

## Cutting a release

1. In one normal commit on a branch, bump:
   - the plugin's `plugin.json` `version`
   - that plugin's entry in `.claude-plugin/marketplace.json`
   - a new entry in the plugin's `CHANGELOG.md` (hand-written)
2. Merge to `main` with a **merge commit or a rebase — never a squash**. Squash
   merging collapses a branch into a single commit, and the release notes are
   generated per commit, so a squashed release branch would reduce its whole
   release body to one bullet.
3. Run the **Release** workflow from the Actions tab, choosing the plugin.

The workflow reads the version off `main` — there is no version input. It fails
before pushing anything if the manifest and marketplace versions disagree, if
the tag already exists, or if there are no releasable commits since the last tag.

When dispatching, leave the workflow's ref selector on `main`. `workflow_dispatch`
lets you pick any branch to run from, and the workflow reads the manifest version
off whatever is checked out — dispatching from a feature branch tags that
branch's commit instead of the merged release.

The workflow pushes the tag and creates the GitHub Release as two separate
steps. If the push succeeds but `gh release create` fails (a transient API
error is enough), the tag ends up on origin with no release attached, and
re-dispatching trips the "tag already exists" guard. Don't bump the version to
work around it — instead delete the stray tag (`git push --delete origin
<tag>`) and re-dispatch, or create the release by hand from the pushed tag.

## Previewing notes locally

CI pins git cliff to 2.13.1. Homebrew installs whatever version its formula
currently points at, so a newer local build may format the notes slightly
differently from what the workflow publishes.

```sh
brew install git-cliff

# craft-ops
git-cliff --config cliff.toml --tag-pattern 'craft-ops-v.*' \
  --include-path 'craft-ops/**' --unreleased --tag craft-ops-v0.12.0

# craft-code
git-cliff --config cliff.toml --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' --unreleased --tag craft-code-v0.5.0
```
