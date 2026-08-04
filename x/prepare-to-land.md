---
name: prepare-to-land
description: Review and respond to PR feedback, resolve merge conflicts, fix CI failures, and leave the current PR ready for someone else to merge without merging it.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# Prepare to Land

Make the current branch's pull request merge-ready, then stop. Be autonomous about actionable feedback, conflicts, and CI failures.

Never merge the PR, enable auto-merge, close the PR, delete branches, or delegate the merge to another agent or automation.

## Step 1: Inspect the pull request

```sh
gh pr view --json number,title,url,headRefName,baseRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
git status -sb
```

If no PR exists for the current branch, report that and stop. Preserve unrelated working-tree changes.

## Step 2: Review all feedback

Fetch:

```sh
gh pr view --json comments,reviews,reviewThreads
gh api repos/{owner}/{repo}/issues/{number}/comments
gh api repos/{owner}/{repo}/pulls/{number}/comments
```

For each unresolved or newly actionable item:

1. Classify it as `accept`, `clarify`, or `push back`, and as correctness, design, style, clarification, or scope.
2. Confirm it does not conflict with the user's intent.
3. Reply where the feedback appeared before changing code:
   - Accept: acknowledge and state the intended fix.
   - Clarify: ask the smallest blocking question.
   - Push back: acknowledge the concern, give concrete rationale, and offer an alternative.
4. Prefix comments written by this workflow with `[claude]`.
5. Implement accepted feedback without expanding scope unnecessarily.
6. Validate correctness fixes with a focused test, reproduction, log, or concrete reasoning.
7. Commit and push the change.
8. Reply in the same thread with the result, validation, and commit SHA.

Reply inline to inline review comments. Reply in the top-level discussion to top-level and bot comments. Do not resolve threads or submit an approving review unless explicitly requested.

## Step 3: Resolve base-branch conflicts

Fetch the latest base branch:

```sh
git fetch origin
git merge "origin/<base-branch>"
```

If conflicts occur:

1. Read both sides and surrounding history.
2. Preserve the intent of both changes rather than choosing one side wholesale.
3. Resolve every conflict and check for conflict markers.
4. Run the repository's required validation.
5. Complete the merge commit using Git's default merge message and push.

If mergeability is `UNKNOWN`, wait and recheck. If the PR head changes remotely, refresh before continuing.

## Step 4: Fix CI

```sh
gh pr checks
```

- Treat required failures as blocking.
- Inspect logs with `gh run view <run-id> --log-failed`.
- Fix failures attributable to the PR, validate, commit, and push.
- Rerun plausibly flaky failures and require a green result rather than ignoring them.
- If checks are pending, wait and recheck.

## Step 5: Recheck readiness

Repeat feedback, merge-state, and CI checks after every push. Continue until:

- all required checks pass
- the branch is conflict-free and current with its base
- requested changes and correctness concerns are addressed or explicitly declined with evidence
- no actionable feedback remains

Then stop. Do not execute or print a merge command.

## Output

```text
PR #<number>: <title>
Ready to merge: <yes/no>
Feedback handled: <summary>
Conflicts handled: <summary>
Validation: <checks and results>
Blocking: <remaining blocker or "none">
Next action: A human or separately authorized landing workflow may merge the PR.
```
