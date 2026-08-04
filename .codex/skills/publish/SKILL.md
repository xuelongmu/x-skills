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
- After selecting the publish remote, derive its hostname and require an active login for that host with `gh auth status --active --hostname <host>`. Do not let stale credentials for unrelated hosts block publication.
- Stop and explain the blocker if authentication, the repository target, or the intended change scope cannot be established safely.

## Workflow

1. Confirm the intended scope.
   - Inspect `git status -sb` and the complete diff before staging.
   - Enumerate untracked paths with `git ls-files --others --exclude-standard` and read or diff the contents of every intended untracked file before staging it.
   - If unrelated changes exist, ask which files belong in the PR.
   - Select and verify the GitHub remote that will receive the branch. Derive the hostname, head owner, and repository from it, reuse it for the push, and do not assume it is named `origin`.
   - Derive the target base owner, repository, and branch. Preserve an explicitly requested base branch; consult the repository default only when the user did not specify one. In fork workflows, keep the head and base repositories distinct.
   - Preserve the selected hostname in every `gh` repository selector and pass `--hostname <host>` to `gh api`; do not fall back implicitly to `github.com`.
2. Determine the branch strategy.
   - If `git branch --show-current` is empty, create a focused named branch before staging or committing.
   - If the current branch is the selected base branch, create a focused branch using the environment's branch-naming convention.
   - Otherwise remain on the current branch unless the user requests a new one.
   - Before staging, committing, or pushing, check whether the selected head branch already has an open PR in the target repository. If one exists, report it and require explicit confirmation that updating that PR is intended; otherwise stop without mutating it.
   - Refresh a local ref for the target base repository and branch.
   - Before staging or pushing, inspect `git log <base-ref>..HEAD --oneline` and `git diff <base-ref>...HEAD` to confirm the complete PR scope, including existing branch commits.
3. Stage only the intended files.
   - Prefer explicit file paths when the worktree is mixed.
   - Use `git add -A` only when the entire worktree is confirmed in scope.
4. If the index contains staged changes, create a terse commit whose message summarizes them. If the index is empty but the confirmed branch range contains unpublished commits, continue without creating an empty commit. Stop only when neither staged changes nor branch commits are available to publish.
5. Run the most relevant available checks.
   - Fix attributable failures when that remains within scope.
   - After applying a validation fix, rerun the affected checks, stage only the fix, and commit it before pushing.
   - Report environmental or unrelated failures accurately.
6. Push the branch to the selected GitHub remote with upstream tracking.
7. Open a pull request ready for review.
   - Prefer the connected GitHub app after the branch is pushed, and explicitly target the derived base repository, base branch, head repository, and head branch.
   - Set the PR's draft state to `false` explicitly when the connector supports that field.
   - For a same-repository PR, use a bare head branch with the CLI fallback:

     ```sh
     gh pr create --repo "<host>/<base-owner>/<base-repository>" --base "<base-branch>" --head "$(git branch --show-current)" --title "<title>" --body-file "<body-file>"
     ```

   - For a cross-repository, user-owned fork, use `<head-owner>:<head-branch>` with the CLI fallback.
   - For a cross-repository, organization-owned head, do not use `gh pr create --head <organization>:<branch>` because the CLI does not support organization owners there. Use the connected GitHub app or `gh api --hostname <host>` with explicit base repository, base branch, head repository, head branch, title, body, and draft state. When both repositories share an organization owner, pass the REST API's `head_repo` field explicitly. Stop if neither path is available.

   - Do not pass `--draft` unless the user explicitly requests a draft.
   - Write the generated PR body through a temporary file so Markdown contains real newlines, and pass the generated title and body to every creation path.
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
