---
name: publish
description: Publish intended local changes by confirming scope, committing, validating, pushing, and opening a GitHub PR ready for review. Create a draft only when explicitly requested.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Publish Changes

Perform the complete publish flow from the current checkout: confirm scope, prepare the branch, commit, validate, push, and open a pull request ready for review.

## Step 1: Confirm scope

Inspect the repository before changing Git state:

```sh
git status -sb
git diff
git diff --cached
git ls-files --others --exclude-standard
git remote -v
```

- Identify exactly which changes belong in the pull request.
- Read or diff the contents of every intended untracked file before staging it; its `??` status line alone is not enough to confirm scope.
- If unrelated changes exist, ask the user which files are in scope.
- Select and verify the GitHub remote that will receive the branch. Store its name as `<publish-remote>` and derive `<host>/<head-owner>/<head-repository>` from its URL. Do not assume it is named `origin`.
- Derive the publish remote's hostname and verify only its active account with `gh auth status --active --hostname "<host>"`. Do not let stale credentials for unrelated hosts block publication.
- Derive `<base-owner>/<base-repository>` and `<base-branch>` from the user's requested target or repository relationships. Preserve an explicitly requested base branch; query the repository default only when the user did not supply one. In a fork workflow, keep the head and base repositories distinct.
- Preserve `<host>` in every `gh` repository selector and pass `--hostname "<host>"` to `gh api`; do not fall back implicitly to `github.com`.
- Never stage unrelated changes silently.

## Step 2: Prepare the branch

Determine the target base branch and current branch explicitly:

```sh
git branch --show-current
# Run only when no base branch was explicitly requested:
gh repo view "<host>/<base-owner>/<base-repository>" --json defaultBranchRef -q .defaultBranchRef.name
```

- If the current branch name is empty because `HEAD` is detached, create a focused named branch before staging or committing.
- If currently on the default branch, create a focused branch using the repository's naming convention.
- Otherwise remain on the current branch unless the user requested a new one.
- Before staging, committing, or pushing, check whether the selected head branch already has an open PR in the target repository. If one exists, report it and require explicit confirmation that updating it is intended; otherwise stop without mutating it.
- Refresh a local `<base-ref>` from the target base repository and branch; do not assume the push remote owns the base in fork workflows.
- Before staging or pushing, inspect the complete branch scope:

  ```sh
  git log "<base-ref>"..HEAD --oneline
  git diff "<base-ref>"...HEAD
  ```

- If the range contains unrelated or stale commits, stop and confirm scope before publishing.

## Step 3: Commit intentionally

1. Stage only the confirmed files. Prefer explicit paths when the worktree is mixed.
2. Review the staged diff:

   ```sh
   git diff --cached
   ```

3. Create a terse commit summarizing the complete staged change.
4. Do not create an empty commit.

## Step 4: Validate

Run the most relevant checks available for the changed scope.

- Fix attributable failures when that remains within the requested scope.
- After applying a validation fix, rerun the affected checks, stage only the fix, and commit it before pushing.
- Report environmental or unrelated failures accurately.
- Do not claim checks passed unless they ran successfully.

## Step 5: Push

Push with upstream tracking:

```sh
git push -u "<publish-remote>" HEAD
```

Never force-push unless the user explicitly authorizes it and the target branch is verified.

## Step 6: Open a ready pull request

Use the derived target repository and base branch. Generate a concise title and a Markdown body covering:

- what changed
- why it changed
- user or developer impact
- root cause for defect fixes
- validation performed
- known limitations or follow-up work

Write the body to a temporary file with real newlines, then select the supported creation path:

- Same repository: use a bare head branch.

  ```sh
  gh pr create --repo "<host>/<base-owner>/<base-repository>" --base "<base-branch>" --head "$(git branch --show-current)" --title "<title>" --body-file "<temp-file>"
  ```

- Cross-repository user-owned fork: use `<head-owner>:<head-branch>` with `gh pr create`.
- Cross-repository organization-owned head: do not use `gh pr create --head <organization>:<branch>` because the CLI does not support organization owners there. Use `gh api --hostname "<host>"` against the pull-request creation endpoint with explicit base repository, base branch, head owner and branch, title, body, and draft state; stop if that API path is unavailable.

- Do not pass `--draft`; the default is ready for review.
- Create a draft only when the user explicitly requests one.
- If the branch already has a PR, report it instead of creating a duplicate. Change its draft/readiness state only when the user requested that change.

## Output

```text
Branch: <branch>
Commit: <sha> <subject>
PR: #<number> <url>
Ready for review: <yes/no from GitHub PR state>
Validation: <checks and results>
Blocking: <remaining concern or "none">
```
