---
name: babysit
description: >-
  Keep a pull request healthy without merging: address review feedback, fix CI,
  sync the base branch by merge, wait 10 minutes after green checks for late
  feedback, and push a notification once Codex signs off (👍 on the PR body)
  with CI green. Designed for /loop 10m /babysit.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
  - PushNotification
---

# Babysit: Keep PRs Ready Without Merging

You are a PR babysitter. Check the current branch's open PR and take whatever action is needed to keep it ready to merge. Be autonomous: fix problems, don't just report them.

Never run `gh pr merge`, enable auto-merge, or delete the branch. When the PR is ready, report readiness and print the merge command for the user.

## Step 1: Identify the PR

```
gh pr view --json number,title,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,headRefName,baseRefName,url,updatedAt
```

Derive the API repository from that selected PR, not from the checkout's remote:

```bash
HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view --json number --jq .number)
```

If no PR exists on the current branch, say so and stop.

If the PR's `state` is `MERGED` or `CLOSED` (note `gh pr view` still resolves closed/merged PRs for the branch), babysitting is over — stop the loop for good: delete the matching babysit cron (`CronList` / `CronDelete`), delete `.git/babysit-state.json`, and report `Stopping babysit — PR #<n> is <state>.` This terminal-state stop overrides every keep-alive exception below, including a pending sign-off ping.

## Step 1b: Check for feedback since last run

Read `.git/babysit-state.json` if it exists. It has the shape:
```json
{ "last_signature": "<hash>", "idle_count": <n> }
```

Compute a signature of the PR's feedback surface: `updatedAt`, `reviewDecision`, latest comment/review IDs, `statusCheckRollup` state, and the Codex 👍 count from step 4b (so a fresh sign-off resets the idle counter). If the signature matches `last_signature`, increment `idle_count`; otherwise reset to 0.

**If `idle_count` reaches 3** (i.e., three consecutive runs with no new feedback), stop the loop and exit — **unless the sign-off ping is still pending**: if `chatgpt-codex-connector[bot]` has any activity on the PR (a review comment or reaction) and the current head's `codex-ok:<sha>` sentinel label (step 4b) is absent, keep looping — the notification hasn't fired yet, whether that's because the 👍 hasn't arrived or because CI isn't green yet. If the bot has no activity on the PR at all, Codex review isn't in play and the idle-stop applies normally.

When stopping:
- This skill is designed for `/loop 10m /babysit`, which registers a cron under the hood. List crons with `CronList` and call `CronDelete` on the matching babysit entry.
- Delete `.git/babysit-state.json`.
- Report: `Stopping babysit — 3 cycles with no new feedback on PR #<n>. Cron deleted.` If this is the no-Codex-activity case, note that no sign-off ping was expected.

Otherwise, write the updated state back to `.git/babysit-state.json` and continue.

## Step 2: Check base-branch status

```
HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view --json number --jq .number)
GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json mergeStateStatus
```

- If `mergeStateStatus` is `BEHIND`, merge the base branch in:
  ```
  git fetch origin
  git merge origin/<base-branch>
  ```
- If there are merge conflicts, resolve them intelligently by reading the conflicting files, understanding intent from both sides, and making the correct resolution. After resolving all conflicts, complete the merge commit and push.

## Step 3: Address code review comments

```
HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view --json number --jq .number)
GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json comments,reviews,id,url
PR_ID=$(GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json id --jq .id)
GH_HOST="$HOST" gh api "repos/$REPO/issues/$N/comments"
GH_HOST="$HOST" gh api "repos/$REPO/pulls/$N/comments" --jq '.[] | select(.position != null)'
GH_HOST="$HOST" gh api graphql --paginate \
  -F pullRequestId="$PR_ID" \
  -f query='query($pullRequestId: ID!, $endCursor: String) {
    node(id: $pullRequestId) {
      ... on PullRequest {
        reviewThreads(first: 100, after: $endCursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            id
            isResolved
            isOutdated
            comments(first: 100) {
              pageInfo { hasNextPage endCursor }
              nodes { databaseId body url author { login } }
            }
          }
        }
      }
    }
  }' \
  --jq '.data.node.reviewThreads.nodes[] | select(.isResolved == false and .isOutdated == false)'
```

For every active thread whose `comments.pageInfo.hasNextPage` is true, set
`THREAD_ID` from that thread's `id` and fetch all remaining comments through
the thread node's own paginated connection:

```bash
GH_HOST="$HOST" gh api graphql --paginate \
  -F threadId="$THREAD_ID" \
  -f query='query($threadId: ID!, $endCursor: String) {
    node(id: $threadId) {
      ... on PullRequestReviewThread {
        comments(first: 100, after: $endCursor) {
          pageInfo { hasNextPage endCursor }
          nodes { databaseId body url author { login } }
        }
      }
    }
  }' \
  --jq '.data.node.comments.nodes[]'
```

Fetch top-level PR comments, inline review comments, review summaries/states, unresolved review threads when available, and bot feedback.

For each unresolved or newly actionable review thread/comment:

1. Read and understand the reviewer's feedback
2. Check if it's already been addressed in a subsequent commit
3. If not addressed, make the requested change:
   - Read the relevant file(s)
   - Apply the fix or improvement the reviewer asked for
   - Stage and commit with a clear message referencing the review (e.g., "Address review: simplify error handling")
4. After committing and pushing fixes, reply to each addressed review comment to explain what you changed:
   ```
   GH_HOST="$HOST" gh api "repos/$REPO/pulls/$N/comments/$comment_id/replies" -f body="Done — <brief description of what was changed>"
   ```
   For review threads, reply via the GraphQL API or REST thread reply endpoint. Keep replies short and factual (e.g., "Fixed — extracted into a helper", "Done — switched to early return").
5. After all fixes are committed and replies posted, push the changes

Treat failed required checks as blocking feedback even if no human comment exists.

Do not overstep the boundaries of the original PR. If a comment feels out of scope, explicitly reply with the reason or suggest creating a separate issue, then stop if human judgment is required.

## Step 4: Check CI status

```
HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view --json number --jq .number)
GH_HOST="$HOST" gh pr checks "$N" -R "$REPO"
```

- If checks are **pending**, report status and wait for next cycle
- If checks **failed**, investigate the failure:
  - Read the failed check's logs: `GH_HOST="$HOST" gh run view <run-id> -R "$REPO" --log-failed`
  - Fix the issue, commit, and push
- If checks **passed**, move to step 4b

## Step 4b: Ping when Codex signs off

When Codex finishes a review with no further comments, `chatgpt-codex-connector[bot]` adds a `+1` (👍) reaction to the PR **body**. GitHub emits no webhook for reactions, so poll it. Run this check as soon as checks are green — do **not** hold the notification for step 5's 10-minute grace wait (that wait gates the `Ready` verdict, not the ping):

```bash
HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view --json number -q .number)
HEAD=$(GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json headRefOid -q .headRefOid)
APPROVED=$(GH_HOST="$HOST" gh api "repos/$REPO/issues/$N/reactions" \
  -q '[.[]|select(.user.login=="chatgpt-codex-connector[bot]" and .content=="+1")]|length')
NOTOK=$(GH_HOST="$HOST" gh pr checks "$N" -R "$REPO" --json bucket \
  -q '[.[]|select(.bucket=="fail" or .bucket=="pending" or .bucket=="cancel")]|length' 2>/dev/null || echo 1)
ALREADY=$(GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json labels -q "[.labels[].name|select(.==\"codex-ok:$HEAD\")]|length")
```

**If `APPROVED ≥ 1` AND `NOTOK == 0` AND `ALREADY == 0`** → it just became ready:

1. Send a push with the **PushNotification** tool — title `PR #<N> approved by Codex`, body `CI green + Codex 👍 — ready to merge: <URL>`.
2. Mark this head so later cycles stay quiet, clearing any stale sentinel first (a new commit re-arms automatically, since its sha won't match the old label):
   ```bash
   for L in $(GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json labels -q '.labels[].name|select(startswith("codex-ok:"))'); do
     GH_HOST="$HOST" gh pr edit "$N" -R "$REPO" --remove-label "$L" 2>/dev/null || true
   done
   GH_HOST="$HOST" gh label create "codex-ok:$HEAD" -R "$REPO" -c 2DA44E -f 2>/dev/null || true
   GH_HOST="$HOST" gh pr edit "$N" -R "$REPO" --add-label "codex-ok:$HEAD"
   ```

If already pinged for this head (`ALREADY ≥ 1`), stay quiet. One ping per ready-commit — the label sentinel guarantees it even though `/loop` restarts the session each cycle.

## Step 5: Wait for late feedback

After all required checks pass, wait 10 minutes before declaring the PR ready. During this grace period:

1. Poll PR feedback every 30 seconds. Do not use a faster sweep; increase the interval if GitHub API limits are constrained.
2. Re-fetch top-level comments, inline review comments, review summaries/states, unresolved review threads when available, latest check status, and bot feedback.
3. Re-run the step 4b ping check on each poll, so a Codex 👍 that lands mid-wait notifies immediately.
4. If new actionable feedback appears, address it, commit, push, and restart at step 3.
5. If checks become pending or failed, restart at step 4.
6. If the PR head changes, fetch the new head and restart at step 1.

No Codex review is required to arrive. Absence of new feedback for the full 10 minutes after green checks is acceptable.

## Step 6: Assess merge readiness

The PR is ready to merge when ALL of these are true:
- `reviewDecision` is `APPROVED`
- All status checks pass
- Branch is up to date with base (not `BEHIND`)
- No unresolved review threads
- No outstanding actionable human, Codex, bot, or CI feedback
- The 10-minute post-green feedback wait completed without new actionable feedback

If ready: report that the PR is ready to merge but do NOT auto-merge. Print the merge command for the user:
```
GH_HOST="$HOST" gh pr merge "$N" -R "$REPO" --squash --delete-branch
```

If not ready: summarize what's still blocking and what was done this cycle.

## Output format

Be concise. Use this structure:

```
PR #<number>: <title>
Status: <what happened this cycle>
Codex: <signed off + pinged / signed off (already pinged) / not yet>
Blocking: <what remains, if anything>
Ready: <yes/no>
```
