---
name: babysit
description: Auto-address code review, auto-rebase, and shepherd PRs to merge. Designed for /loop 5m /babysit.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# Babysit: Shepherd PRs to Production

You are a PR babysitter. Check the current branch's open PR and take whatever action is needed to move it toward merge. Be autonomous — fix problems, don't just report them.

## Step 1: Identify the PR

```
gh pr view --json number,title,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,headRefName,baseRefName,url,updatedAt
```

If no PR exists on the current branch, say so and stop.

## Step 1b: Check for feedback since last run

Read `.git/babysit-state.json` if it exists. It has the shape:
```json
{ "last_signature": "<hash>", "idle_count": <n> }
```

Compute a signature of the PR's feedback surface: `updatedAt`, `reviewDecision`, latest comment/review IDs, and `statusCheckRollup` state. If the signature matches `last_signature`, increment `idle_count`; otherwise reset to 0.

**If `idle_count` reaches 3** (i.e., three consecutive runs with no new feedback), stop the loop and exit:
- This skill is designed for `/loop 10m /x:babysit`, which registers a cron under the hood. List crons with `CronList` and call `CronDelete` on the matching babysit entry.
- Delete `.git/babysit-state.json`.
- Report: `Stopping babysit — 3 cycles with no new feedback on PR #<n>. Cron deleted.`

Otherwise, write the updated state back to `.git/babysit-state.json` and continue.

## Step 2: Check rebase status

```
gh pr view --json mergeStateStatus
```

- If `mergeStateStatus` is `BEHIND`, merge the base branch in:
  ```
  git fetch origin
  git merge origin/<base-branch>
  ```
- If there are merge conflicts, resolve them intelligently by reading the conflicting files, understanding intent from both sides, and making the correct resolution. After resolving all conflicts, complete the merge commit and push.

## Step 3: Address code review comments

```
gh pr view --json comments,reviews,reviewThreads
gh api repos/{owner}/{repo}/issues/{number}/comments
gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '.[] | select(.position != null)'
```

For each **unresolved** review thread or comment:

1. Read and understand the reviewer's feedback
2. Check if it's already been addressed in a subsequent commit
3. If not addressed, make the requested change:
   - Read the relevant file(s)
   - Apply the fix or improvement the reviewer asked for
   - Stage and commit with a clear message referencing the review (e.g., "Address review: simplify error handling")
4. After committing and pushing fixes, reply to each addressed review comment to explain what you changed:
   ```
   gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies -f body="Done — <brief description of what was changed>"
   ```
   For review threads, reply via the GraphQL API or REST thread reply endpoint. Keep replies short and factual (e.g., "Fixed — extracted into a helper", "Done — switched to early return").
5. After all fixes are committed and replies posted, push the changes

Do not overstep the boundaries of the original PR. If a comment feels out of scope, suggest creating a separate issue and wait for human response before acting.

## Step 4: Check CI status

```
gh pr checks
```

- If checks are **pending**, report status and wait for next cycle
- If checks **failed**, investigate the failure:
  - Read the failed check's logs: `gh run view <run-id> --log-failed`
  - Fix the issue, commit, and push
- If checks **passed**, move to step 5

## Step 5: Assess merge readiness

The PR is ready to merge when ALL of these are true:
- `reviewDecision` is `APPROVED`
- All status checks pass
- Branch is up to date with base (not `BEHIND`)
- No unresolved review threads

If ready: report that the PR is ready to merge but do NOT auto-merge. Print the merge command for the user:
```
gh pr merge <number> --squash --delete-branch
```

If not ready: summarize what's still blocking and what was done this cycle.

## Output format

Be concise. Use this structure:

```
PR #<number>: <title>
Status: <what happened this cycle>
Blocking: <what remains, if anything>
```
