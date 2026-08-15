# GitHub Release Process Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each of the repo's two plugins a tagged GitHub Release whose notes are generated from conventional commits by git cliff.

**Architecture:** Two independent release streams share one `cliff.toml`; the stream is selected on the command line via `--tag-pattern` plus path filters, so `craft-ops` notes come from `craft-ops/**` and `craft-code` notes come from everything else. A `workflow_dispatch` workflow reads the version already on `main`, validates it, generates notes, tags, and publishes — it never commits back. A dependency-free `commit-msg` hook keeps the commit stream parseable.

**Tech Stack:** git cliff 2.13.1, GitHub Actions, `gh` CLI, `jq`, POSIX `sh`.

**Spec:** `docs/superpowers/specs/2026-08-15-github-release-process-design.md`

## Global Constraints

- **Tag format:** `craft-code-v<major>.<minor>.<patch>` and `craft-ops-v<major>.<minor>.<patch>`. Annotated tags only.
- **git cliff version:** pinned to `2.13.1` everywhere (CI download and local docs).
- **No new package manager.** The repo has no `package.json`, `Makefile`, or lockfile. Everything added must be POSIX `sh`, a config file, or installed by CI at run time.
- **CI never writes to `main`.** The release workflow's only write is pushing a tag and creating a release. Permissions are exactly `contents: write`.
- **`CHANGELOG.md` and `craft-ops/CHANGELOG.md` are never touched by automation.** They stay hand-written.
- **Allowed commit types:** `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`, `revert`.
- **Manifest paths:** `craft-code` → `.claude-plugin/plugin.json`; `craft-ops` → `craft-ops/.claude-plugin/plugin.json`. Both plugins are also pinned in `.claude-plugin/marketplace.json` under `.plugins[]` matched by `.name`.
- **Current versions:** `craft-code` `0.4.0`, `craft-ops` `0.11.0`.
- **Branch:** all work lands on `feat/release-process`, which already exists and already carries the spec commit.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `.githooks/commit-msg` | Create | Validate a commit subject against the conventional-commit grammar. Only file in this dir — it is `core.hooksPath`. |
| `tools/hook-tests/commit-msg-test.sh` | Create | Self-contained test runner for the hook. Lives under `tools/` alongside the repo's other harnesses. |
| `cliff.toml` | Create | Commit parsing, grouping, and the release-note body template. Shared by both streams. |
| `.github/workflows/release.yml` | Create | The dispatchable release: validate, generate, tag, publish. |
| `docs/releasing.md` | Create | Commit grammar, hook install, how to cut a release, how to preview notes. |
| `README.md` | Modify | One pointer to `docs/releasing.md`. |

---

### Task 1: Commit-message hook

Builds the hook and its test runner together — the test runner is the only way to exercise the hook, so they are one reviewable unit.

**Files:**
- Create: `.githooks/commit-msg`
- Test: `tools/hook-tests/commit-msg-test.sh`

**Interfaces:**
- Consumes: nothing.
- Produces: `.githooks/commit-msg` — an executable invoked by git as `commit-msg <path-to-message-file>`. Exit `0` = accept, exit `1` = reject with an explanation on stderr. Task 5 documents its install line.

- [ ] **Step 1: Write the failing test**

Create `tools/hook-tests/commit-msg-test.sh`:

```sh
#!/bin/sh
# Tests for .githooks/commit-msg. Run from anywhere: tools/hook-tests/commit-msg-test.sh
set -u

HOOK="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)/.githooks/commit-msg"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

passed=0
failed=0

# expect_accept <description> <subject>
expect_accept() {
  printf '%s\n' "$2" > "$TMP/msg"
  if "$HOOK" "$TMP/msg" >/dev/null 2>&1; then
    passed=$((passed + 1))
  else
    failed=$((failed + 1))
    printf 'FAIL (expected accept): %s -- %s\n' "$1" "$2"
  fi
}

# expect_reject <description> <subject>
expect_reject() {
  printf '%s\n' "$2" > "$TMP/msg"
  if "$HOOK" "$TMP/msg" >/dev/null 2>&1; then
    failed=$((failed + 1))
    printf 'FAIL (expected reject): %s -- %s\n' "$1" "$2"
  else
    passed=$((passed + 1))
  fi
}

# Every allowed type, unscoped.
for t in feat fix docs refactor perf test chore build ci revert; do
  expect_accept "type $t" "$t: do a thing"
done

expect_accept "scoped"                "feat(craft-ops): add a skill"
expect_accept "scope with dashes"     "fix(craft-code): correct the thing"
expect_accept "breaking marker"       "feat!: drop the old flag"
expect_accept "scoped breaking"       "refactor(craft-code)!: rename the namespace"
expect_accept "merge commit"          "Merge pull request #3 from bryceklinker/feat/x"
expect_accept "merge branch"          "Merge branch 'main' into feat/x"
expect_accept "git revert subject"    'Revert "feat: add a thing"'
expect_accept "fixup"                 "fixup! feat: add a thing"
expect_accept "squash"                "squash! feat: add a thing"

expect_reject "no type"               "add a thing"
expect_reject "unknown type"          "feet: add a thing"
expect_reject "missing colon"         "feat add a thing"
expect_reject "missing space"         "feat:add a thing"
expect_reject "empty description"     "feat: "
expect_reject "empty scope"           "feat(): add a thing"
expect_reject "unclosed scope"        "feat(craft-code: add a thing"
expect_reject "leading whitespace"    "  feat: add a thing"

# A comment-only or empty message file must not be accepted as a subject.
expect_reject "empty message"         ""

printf '\n%d passed, %d failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
```

Make it executable:

```bash
chmod +x tools/hook-tests/commit-msg-test.sh
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `tools/hook-tests/commit-msg-test.sh`
Expected: FAIL. Every `expect_accept` case fails because `.githooks/commit-msg` does not exist yet (so invoking it is a non-zero exit). Output ends with a non-zero `failed` count and a non-zero exit status.

- [ ] **Step 3: Write the minimal implementation**

Create `.githooks/commit-msg`:

```sh
#!/bin/sh
# Rejects commit subjects that are not conventional commits.
# Install: git config core.hooksPath .githooks
set -u

msg_file="$1"

# The subject is the first line that is not a comment.
subject="$(grep -v '^#' "$msg_file" | sed -n '1p')"

# Git generates these itself; their formats are not ours to police.
case "$subject" in
  "Merge "*|"Revert "*|"fixup! "*|"squash! "*) exit 0 ;;
esac

types='feat|fix|docs|refactor|perf|test|chore|build|ci|revert'

if printf '%s' "$subject" | grep -Eq "^($types)(\([a-z0-9][a-z0-9._-]*\))?!?: .+"; then
  exit 0
fi

cat >&2 <<EOF
Commit rejected: the subject is not a conventional commit.

  subject: $subject

Expected:

  <type>(<optional scope>)<optional !>: <description>

Allowed types: feat, fix, docs, refactor, perf, test, chore, build, ci, revert

Examples:

  feat(craft-ops): add the release workflow
  fix: correct the tag pattern
  refactor(craft-code)!: rename the skill namespace

Release notes are generated from these subjects, so a malformed one is
silently dropped from the changelog.
EOF
exit 1
```

Make it executable:

```bash
chmod +x .githooks/commit-msg
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `tools/hook-tests/commit-msg-test.sh`
Expected: PASS — `28 passed, 0 failed` and exit status 0.

- [ ] **Step 5: Activate the hook in this clone and prove it works on a real commit**

```bash
git config core.hooksPath .githooks
git add .githooks/commit-msg tools/hook-tests/commit-msg-test.sh
git commit -m "not a conventional commit"
```

Expected: the commit is REJECTED and the grammar message prints. This is the hook running for real, not the test harness.

- [ ] **Step 6: Commit**

```bash
git commit -m "ci: add commit-msg hook enforcing conventional commits"
```

Expected: the commit succeeds.

---

### Task 2: Baseline tags

Without these, `--unreleased` has no lower bound and the first release of each plugin sweeps in the entire history.

**Files:** none — this task creates git refs only.

**Interfaces:**
- Consumes: nothing.
- Produces: tags `craft-code-v0.4.0` and `craft-ops-v0.11.0` on the current `main` `HEAD`. Task 3 and Task 4 both depend on these existing; `--tag-pattern` resolves `--unreleased` from them.

> **Stop and confirm with the user before Step 3.** Pushing tags is a public, shared-state change. Steps 1–2 are local and reversible; Step 3 is not.

- [ ] **Step 1: Identify the commit to tag**

```bash
git rev-parse main
git log --oneline -1 main
```

Expected: `e4635aa` — the `Merge pull request #3` commit. Tag `main`, not the current branch: everything on `feat/release-process` should land inside the *next* craft-code release, not the baseline.

- [ ] **Step 2: Create both annotated tags locally**

```bash
git tag -a craft-code-v0.4.0 main -m "Baseline tag for craft-code 0.4.0 (no release notes)"
git tag -a craft-ops-v0.11.0  main -m "Baseline tag for craft-ops 0.11.0 (no release notes)"
git tag -l 'craft-*'
```

Expected: both tags listed.

- [ ] **Step 3: Push the tags**

```bash
git push origin craft-code-v0.4.0 craft-ops-v0.11.0
```

Expected: `* [new tag]` twice.

- [ ] **Step 4: Verify no GitHub Releases were created**

Run: `gh release list`
Expected: empty. These tags are range baselines only — the spec attaches no release to them.

---

### Task 3: `cliff.toml`

**Files:**
- Create: `cliff.toml`

**Interfaces:**
- Consumes: the baseline tags from Task 2.
- Produces: `cliff.toml` at the repo root, consumed by Task 4's workflow and Task 5's docs via these exact invocations:
  - `git-cliff --config cliff.toml --tag-pattern 'craft-ops-v.*' --include-path 'craft-ops/**' --unreleased --tag <tag> --output <file>`
  - `git-cliff --config cliff.toml --tag-pattern 'craft-code-v.*' --exclude-path 'craft-ops/**' --unreleased --tag <tag> --output <file>`

- [ ] **Step 1: Write the config**

Create `cliff.toml`:

```toml
# Generates GitHub Release bodies only. The hand-written CHANGELOG.md files
# are not managed by git cliff -- see docs/releasing.md.
#
# The stream (craft-code vs craft-ops) is selected on the command line with
# --tag-pattern plus --include-path/--exclude-path, so this one config serves both.

[changelog]
# No document header and no version heading: GitHub renders the tag name as the
# release title, so repeating it in the body is noise.
header = ""
# Breaking changes get their own section at the top. They also remain listed
# under their type group -- the repetition is deliberate emphasis.
body = """
{%- set breaking = commits | filter(attribute="breaking", value=true) -%}
{%- if breaking | length > 0 %}
### Breaking Changes
{% for commit in breaking %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{%- endfor %}
{% endif -%}
{%- for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{%- endfor %}
{% endfor %}
"""
footer = ""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
split_commits = false
protect_breaking_commits = true
filter_commits = false
topo_order = false
sort_commits = "oldest"

commit_parsers = [
  { message = "^Merge ", skip = true },
  { message = "^Revert ", skip = true },
  { message = "^chore\\(release\\)", skip = true },
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^docs", group = "Documentation" },
  { message = "^test", skip = true },
  { message = "^chore", group = "Chores" },
  { message = "^build", group = "Chores" },
  { message = "^ci", group = "Chores" },
]
```

- [ ] **Step 2: Generate the craft-ops stream and read the output**

```bash
git-cliff --config cliff.toml \
  --tag-pattern 'craft-ops-v.*' \
  --include-path 'craft-ops/**' \
  --unreleased --tag craft-ops-v0.11.1
```

Expected: **empty output** (no groups, no bullets). Task 1 and Task 3 touched only root-level files, so there are zero `craft-ops/**` commits after the `craft-ops-v0.11.0` baseline. This is the correct result and is exactly what the workflow's empty-release guard must catch in Task 4.

- [ ] **Step 3: Generate the craft-code stream and read the output**

```bash
git-cliff --config cliff.toml \
  --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' \
  --unreleased --tag craft-code-v0.4.1
```

Expected: a `### Chores` group containing the commit-msg hook commit, and a `### Documentation` group containing the design-spec commit. No `## [craft-code-v0.4.1]` heading line, no merge commits, and no commits from before the baseline tag. Read the actual output and confirm each of those.

- [ ] **Step 4: Verify the baseline actually bounds the range**

```bash
git-cliff --config cliff.toml \
  --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' \
  --unreleased --tag craft-code-v0.4.1 | wc -l
```

Expected: fewer than 20 lines. If this returns hundreds of lines, the baseline tag is not being honoured — stop and fix `--tag-pattern` before continuing.

- [ ] **Step 5: Commit**

```bash
git add cliff.toml
git commit -m "ci: add cliff.toml for per-plugin release notes"
```

---

### Task 4: Release workflow

**Files:**
- Create: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: `cliff.toml` from Task 3 and the baseline tags from Task 2.
- Produces: a `workflow_dispatch` workflow named `Release` with one input, `plugin`, whose value is `craft-code` or `craft-ops`. Task 5 documents dispatching it; Task 6 runs it for real.

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      plugin:
        description: Which plugin to release
        required: true
        type: choice
        options:
          - craft-code
          - craft-ops

permissions:
  contents: write

env:
  GIT_CLIFF_VERSION: "2.13.1"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Resolve version and tag
        id: resolve
        run: |
          set -euo pipefail
          plugin='${{ inputs.plugin }}'

          if [ "$plugin" = "craft-code" ]; then
            manifest='.claude-plugin/plugin.json'
          else
            manifest='craft-ops/.claude-plugin/plugin.json'
          fi

          version="$(jq -r '.version' "$manifest")"
          if [ -z "$version" ] || [ "$version" = "null" ]; then
            echo "::error::could not read .version from $manifest"
            exit 1
          fi

          marketplace_version="$(jq -r --arg p "$plugin" \
            '.plugins[] | select(.name == $p) | .version' .claude-plugin/marketplace.json)"

          if [ "$version" != "$marketplace_version" ]; then
            echo "::error::version mismatch: $manifest is $version but marketplace.json pins $marketplace_version for $plugin. Bump both before releasing."
            exit 1
          fi

          tag="${plugin}-v${version}"
          if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
            echo "::error::tag $tag already exists. Bump the version before releasing."
            exit 1
          fi

          {
            echo "version=$version"
            echo "tag=$tag"
          } >> "$GITHUB_OUTPUT"

      - name: Install git-cliff
        run: |
          set -euo pipefail
          url="https://github.com/orhun/git-cliff/releases/download/v${GIT_CLIFF_VERSION}/git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
          mkdir -p "$RUNNER_TEMP/git-cliff"
          curl -fsSL "$url" -o "$RUNNER_TEMP/git-cliff.tar.gz"
          tar -xzf "$RUNNER_TEMP/git-cliff.tar.gz" -C "$RUNNER_TEMP/git-cliff"
          # Don't assume the archive's directory layout -- find the binary.
          bin="$(find "$RUNNER_TEMP/git-cliff" -type f -name git-cliff -perm -u+x | head -1)"
          if [ -z "$bin" ]; then
            echo "::error::git-cliff binary not found in the downloaded archive"
            exit 1
          fi
          mkdir -p "$RUNNER_TEMP/bin"
          cp "$bin" "$RUNNER_TEMP/bin/git-cliff"
          echo "$RUNNER_TEMP/bin" >> "$GITHUB_PATH"

      - name: Verify git-cliff
        run: git-cliff --version

      - name: Generate release notes
        run: |
          set -euo pipefail
          plugin='${{ inputs.plugin }}'
          tag='${{ steps.resolve.outputs.tag }}'

          if [ "$plugin" = "craft-ops" ]; then
            git-cliff --config cliff.toml \
              --tag-pattern 'craft-ops-v.*' \
              --include-path 'craft-ops/**' \
              --unreleased --tag "$tag" --output notes.md
          else
            git-cliff --config cliff.toml \
              --tag-pattern 'craft-code-v.*' \
              --exclude-path 'craft-ops/**' \
              --unreleased --tag "$tag" --output notes.md
          fi

          if [ ! -s notes.md ] || ! grep -q '^- ' notes.md; then
            echo "::error::no releasable commits for $plugin since its last tag. Nothing to release."
            exit 1
          fi

          echo "--- generated notes ---"
          cat notes.md

      - name: Create and push tag
        run: |
          set -euo pipefail
          tag='${{ steps.resolve.outputs.tag }}'
          git config user.name  'github-actions[bot]'
          git config user.email 'github-actions[bot]@users.noreply.github.com'
          git tag -a "$tag" -m "$tag"
          git push origin "$tag"

      - name: Publish release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          tag='${{ steps.resolve.outputs.tag }}'
          gh release create "$tag" --title "$tag" --notes-file notes.md
```

- [ ] **Step 2: Verify the workflow file parses as YAML**

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/release.yml')); print('yaml ok')"
```

Expected: `yaml ok`.

- [ ] **Step 3: Verify the guard logic locally against the real manifests**

Run each guard's core expression by hand and read the values:

```bash
jq -r '.version' .claude-plugin/plugin.json
jq -r '.plugins[] | select(.name == "craft-code") | .version' .claude-plugin/marketplace.json
jq -r '.version' craft-ops/.claude-plugin/plugin.json
jq -r '.plugins[] | select(.name == "craft-ops") | .version' .claude-plugin/marketplace.json
```

Expected: `0.4.0`, `0.4.0`, `0.11.0`, `0.11.0` — the two pairs match, so the consistency guard passes for both plugins today.

- [ ] **Step 4: Verify the tag-uniqueness guard fires**

```bash
git rev-parse -q --verify refs/tags/craft-code-v0.4.0 && echo "guard would fire"
```

Expected: a SHA followed by `guard would fire` — confirming that re-releasing the current version is correctly blocked.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add dispatchable per-plugin release workflow"
```

---

### Task 5: Release documentation

**Files:**
- Create: `docs/releasing.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: the hook from Task 1, `cliff.toml` from Task 3, and the workflow from Task 4.
- Produces: no code interface — documentation only.

- [ ] **Step 1: Write the release doc**

Create `docs/releasing.md`:

````markdown
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
2. Merge to `main`.
3. Run the **Release** workflow from the Actions tab, choosing the plugin.

The workflow reads the version off `main` — there is no version input. It fails
before pushing anything if the manifest and marketplace versions disagree, if
the tag already exists, or if there are no releasable commits since the last tag.

## Previewing notes locally

```sh
brew install git-cliff   # pinned to 2.13.1 in CI

# craft-ops
git-cliff --config cliff.toml --tag-pattern 'craft-ops-v.*' \
  --include-path 'craft-ops/**' --unreleased --tag craft-ops-v0.12.0

# craft-code
git-cliff --config cliff.toml --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' --unreleased --tag craft-code-v0.5.0
```
````

- [ ] **Step 2: Add the README pointer**

`README.md` has a `## Maintaining the suite` section (line 89) whose bullets
follow the form `` - [`path`](path) — description``. Insert a third bullet after
the `tools/behavioral-evals/` bullet (line 92) and before the
`craft-code-workspace/` bullet (line 93):

```markdown
- [`docs/releasing.md`](docs/releasing.md) — the commit grammar, the `commit-msg` hook, and how to cut a tagged release with generated notes.
```

- [ ] **Step 3: Verify every command in the doc actually runs**

Copy each shell command out of `docs/releasing.md` and run it:

```bash
git config core.hooksPath .githooks
tools/hook-tests/commit-msg-test.sh
git-cliff --config cliff.toml --tag-pattern 'craft-code-v.*' \
  --exclude-path 'craft-ops/**' --unreleased --tag craft-code-v0.5.0
```

Expected: the hook tests report `0 failed`, and the git cliff invocation prints
grouped bullets. A documented command that does not run is a documentation bug —
fix the doc, not the reader.

- [ ] **Step 4: Commit**

```bash
git add docs/releasing.md README.md
git commit -m "docs: document the release process and commit grammar"
```

---

### Task 6: End-to-end verification with a real release

The workflow cannot be proven by inspection. This task merges the branch and
cuts an actual `craft-code` patch release.

**Files:**
- Modify: `.claude-plugin/plugin.json` (version `0.4.0` → `0.4.1`)
- Modify: `.claude-plugin/marketplace.json` (craft-code entry `0.4.0` → `0.4.1`)
- Modify: `CHANGELOG.md` (new `0.4.1` entry, hand-written)

**Interfaces:**
- Consumes: everything from Tasks 1–5.
- Produces: the published GitHub Release `craft-code-v0.4.1`.

> **Stop and confirm with the user before Step 2.** Merging to `main` and publishing a release are public actions.

- [ ] **Step 1: Bump craft-code to 0.4.1 and write the changelog entry**

Set `.version` to `0.4.1` in `.claude-plugin/plugin.json`, and set the
`craft-code` entry's `version` to `0.4.1` in `.claude-plugin/marketplace.json`.

Then add a hand-written entry at the top of the version list in `CHANGELOG.md`,
matching the prose voice of the existing entries — read the `[0.4.0]` entry
first and follow its structure. The entry covers: the repo gained a release
process; `craft-code` now ships as tagged GitHub Releases with notes generated
from conventional commits; a `commit-msg` hook enforces the grammar for anyone
who runs `git config core.hooksPath .githooks`.

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md
git commit -m "chore(craft-code): bump to 0.4.1 for the first tagged release"
```

- [ ] **Step 2: Open a PR and merge to main**

```bash
git push -u origin feat/release-process
gh pr create --title "feat: tagged GitHub releases with git cliff release notes" --body "Implements docs/superpowers/specs/2026-08-15-github-release-process-design.md"
```

Merge once checks are green.

- [ ] **Step 3: Dispatch the release workflow**

```bash
gh workflow run release.yml -f plugin=craft-code
gh run watch
```

Expected: all steps succeed. Read the "Generate release notes" step's log — it
prints the generated notes before publishing.

- [ ] **Step 4: Read the published release**

```bash
gh release view craft-code-v0.4.1
```

Expected, confirmed by reading the actual output:
- title is `craft-code-v0.4.1`
- the body has grouped sections with bullets from this branch's commits
- no merge commits appear
- no commits from before `craft-code-v0.4.0` appear

- [ ] **Step 5: Verify the empty-release guard on the real workflow**

```bash
gh workflow run release.yml -f plugin=craft-ops
gh run watch
```

Expected: the run **fails** at "Generate release notes" with
`no releasable commits for craft-ops since its last tag`. This is the guard
working — none of this work touched `craft-ops/**`. Confirm no `craft-ops-v0.11.0`
release was created and no new tag was pushed:

```bash
gh release list
git ls-remote --tags origin 'craft-ops-*'
```

Expected: `craft-code-v0.4.1` is the only release; the only `craft-ops` tag is
the `craft-ops-v0.11.0` baseline.

- [ ] **Step 6: Clean up**

```bash
git checkout main && git pull
git branch -d feat/release-process
```
