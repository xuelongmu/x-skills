---
name: publish
description: Publish intended local changes by confirming scope, committing, validating, pushing, and opening a GitHub PR ready for review. Create a draft only when explicitly requested.
allowed-tools:
  - Bash
  - Read
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
git remote -v
```

- Identify exactly which changes belong in the pull request.
- If unrelated changes exist, ask the user which files are in scope.
- Select and verify the GitHub remote that will receive the branch, and store its name as `<publish-remote>` for every later remote operation. Do not assume it is named `origin`.
- Never stage unrelated changes silently.

## Step 2: Prepare the branch

Determine the default branch and current branch:

```sh
git branch --show-current
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```

- If the current branch name is empty because `HEAD` is detached, create a focused named branch before staging or committing.
- If currently on the default branch, create a focused branch using the repository's naming convention.
- Otherwise remain on the current branch unless the user requested a new one.

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

Derive the base branch from the user's request or the remote default branch. Generate a concise title and a Markdown body covering:

- what changed
- why it changed
- user or developer impact
- root cause for defect fixes
- validation performed
- known limitations or follow-up work

Write the body to a temporary file with real newlines, then create the PR:

```sh
gh pr create --base "<base>" --head "$(git branch --show-current)" --title "<title>" --body-file "<temp-file>"
```

- Do not pass `--draft`; the default is ready for review.
- Create a draft only when the user explicitly requests one.
- If the branch already has a PR, report it instead of creating a duplicate. Change its draft/readiness state only when the user requested that change.

## Output

```text
Branch: <branch>
Commit: <sha> <subject>
PR: #<number> <url>
Ready for review: yes
Validation: <checks and results>
Blocking: <remaining concern or "none">
```
