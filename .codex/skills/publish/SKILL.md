---
name: publish
description: Publish intended local changes to GitHub by confirming scope, creating or selecting a branch, committing intentionally, validating, pushing, and opening a pull request that is ready for review. Use when asked to publish changes, push work and open a PR, or perform the complete commit-to-ready-PR workflow. Create a draft only when the user explicitly requests one.
---

# Publish Changes

## Overview

Perform the complete publish flow from a local checkout: confirm scope, prepare the branch, commit, validate, push, and open a pull request ready for review.

Use local `git` for branch creation, staging, commits, and pushes. Prefer the connected GitHub app for pull request creation; use `gh` when connector coverage is insufficient.

## Preconditions

- Require a local Git repository with an accessible GitHub remote.
- Require GitHub CLI `gh`. Check `gh --version`.
- Require an authenticated GitHub session. Check `gh auth status`.
- Stop and explain the blocker if authentication, the repository target, or the intended change scope cannot be established safely.

## Workflow

1. Confirm the intended scope.
   - Inspect `git status -sb` and the complete diff before staging.
   - If unrelated changes exist, ask which files belong in the PR.
2. Determine the branch strategy.
   - If on the default branch, create a focused branch using the environment's branch-naming convention.
   - Otherwise remain on the current branch unless the user requests a new one.
3. Stage only the intended files.
   - Prefer explicit file paths when the worktree is mixed.
   - Use `git add -A` only when the entire worktree is confirmed in scope.
4. Create a terse commit whose message summarizes the complete staged change.
5. Run the most relevant available checks.
   - Fix attributable failures when that remains within scope.
   - Report environmental or unrelated failures accurately.
6. Push the branch with upstream tracking.
7. Open a pull request ready for review.
   - Prefer the connected GitHub app after the branch is pushed.
   - Set the PR's draft state to `false` explicitly when the connector supports that field.
   - Derive the repository from the remote, the head from the current branch, and the base from the user's request or the remote default branch.
   - For forks, cross-repository heads, or ambiguous connector targeting, use the CLI fallback:

     ```sh
     gh pr create --fill --base "<base-branch>" --head "$(git branch --show-current)"
     ```

   - Do not pass `--draft`.
   - Write a custom PR body through a temporary file so Markdown contains real newlines.
   - Create a draft only when the user explicitly requests one; then use the connector's draft option or `gh pr create --draft`.
8. Summarize the branch, commit, PR target and URL, readiness state, validation, and any remaining concerns.

## Write Safety

- Never stage unrelated user changes silently.
- Never push when a mixed worktree's scope remains ambiguous.
- Never force-push unless the user explicitly authorizes it or the established workflow clearly requires it and the target is verified.
- Never overwrite an existing PR. If the current branch already has one, report it and update its draft/readiness state only when the user requested that change.
- Default to a ready-for-review PR, not a draft.

## Pull Request Content

Write a title that summarizes the full diff. Write a Markdown description covering:

- what changed
- why it changed
- user or developer impact
- root cause when fixing a defect
- validation performed
- known limitations or follow-up work
