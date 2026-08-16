---
name: land
description: >-
  Publish local changes into a pull request when needed, then land the PR by
  resolving conflicts, keeping CI green, handling feedback, and merging with the
  repository's customary merge method. Use when asked to land, merge, or
  shepherd work or a PR to completion.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# Land: Merge the PR

Take the intended work all the way to a merged pull request. Be autonomous: open the PR when it does not exist, fix conflicts and CI, handle feedback, and merge once every gate passes.

Unlike `babysit`, this skill **does** merge. Keep the watch loop running until the PR is merged or you are genuinely blocked; do not yield with the PR still open unless you are reporting a blocker.

## Goals

- Ensure the PR is conflict-free with its base branch.
- Open a ready-for-review PR when the intended work does not already have one.
- Keep CI green and fix failures when they occur.
- Merge with the repository's customary method: merge commit, rebase, or squash.
- Do not delete the remote branch after merging; repositories that want that auto-delete head branches.

## Preconditions

- A local Git repository with an accessible GitHub remote.
- `gh` CLI installed and authenticated for the PR's host (`gh auth status --active --hostname "<host>"`).
- Run every command from the PR repository's working directory so `gh` resolves the right repo.

## Step 1: Establish scope and PR identity

Inspect the repository before changing Git state:

```sh
git status -sb
git diff
git diff --cached
git ls-files --others --exclude-standard
git branch --show-current
git remote -v
```

Identify exactly which changes belong in this PR, the GitHub remote, the target repository, and the base branch. Never include unrelated changes silently; ask which files are in scope when the worktree is mixed.

Then select the PR and derive the coordinates every later call uses from the **selected PR**, not from the checkout's remote. When the user named a PR by number or URL, that selector wins — an unqualified `gh pr view` would silently resolve the current branch's PR instead and land the wrong change:

```bash
# PR_SELECTOR is the user's number/URL when they gave one; empty means current branch.
PR_URL=$(gh pr view ${PR_SELECTOR:+"$PR_SELECTOR"} --json url --jq .url)
HOST=$(gh pr view "$PR_URL" --json url --jq '.url | split("/")[2]')
REPO=$(gh pr view "$PR_URL" --json url --jq '.url | split("/") | .[3:5] | join("/")')
N=$(gh pr view "$PR_URL" --json number --jq .number)
GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json number,title,body,state,url,isDraft,headRefName,headRefOid,baseRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt
```

Keep `$PR_URL` for the whole run and re-select from it, never from the branch, so a checkout that moves cannot swap the PR underneath you.

- If no open PR exists, run **Step 2: Open a PR when needed**, then re-derive these coordinates from the PR you created.
- If `isDraft` is true, the merge will be rejected no matter how many gates pass. Do not enter the watch loop first: if the user asked to land this PR, mark it ready now with `GH_HOST="$HOST" gh pr ready "$N" -R "$REPO"`; if they explicitly wanted it kept as a draft, stop and say landing is paused until they authorize marking it ready.
- If the PR state is `MERGED`, report successful external completion and stop. If it is `CLOSED` without a merge, that is terminal — report that no merge occurred and stop.
- Pass `GH_HOST="$HOST"` on every `gh` call so custom GitHub Enterprise hosts and ports survive; do not fall back implicitly to `github.com`.

If the PR already existed and the worktree has intended uncommitted changes, stage only those changes, review the staged diff, run the relevant validation against that exact state, commit, and push before watching.

## Step 2: Open a PR when needed

Use the `publish` skill to do this — it already covers scope confirmation, branch preparation, intentional commits, validation, push, and ready-for-review PR creation (including fork and organization-owned head cases). Then continue landing.

If `publish` is unavailable, do it inline:

1. Select and verify the push remote, host, head repository, target repository, and base branch. Preserve an explicitly requested base; otherwise use the repository default. Keep head and base repositories distinct for fork workflows.
2. If `HEAD` is detached or sits on the target base branch, create a focused branch before staging or committing. Otherwise stay on the current branch.
3. Refresh the target base ref and inspect the full scope together with the worktree diff and every intended untracked file:

   ```sh
   git log "<base-ref>"..HEAD --oneline
   git diff "<base-ref>"...HEAD
   ```

   Stop if scope is ambiguous or there is nothing to publish.
4. Stage only intended files and review the complete staged diff. Do not commit yet.
5. Run the relevant local validation against that exact staged worktree. Fix attributable failures within scope, stage the fixes, review the staged diff again, and rerun the affected checks. When unrelated unstaged changes coexist, materialize the index in an isolated temporary worktree and validate there; do not test the mixed working tree and do not stash the user's changes. Then create a terse commit when staged changes exist. Reuse unpublished branch commits; never create an empty commit.
6. Push with upstream tracking (`git push -u "<remote>" HEAD`). Never force-push unless the user explicitly authorized it or the established workflow clearly requires it against a verified target.
7. Write a title covering the full branch diff and a Markdown body covering what changed, why, user impact, validation, and known limitations.
8. Re-check for an open PR after the push to avoid duplicates. If none exists, create it ready for review:

   ```sh
   gh pr create --repo "<host>/<base-owner>/<base-repository>" \
     --base "<base-branch>" \
     --head "$(git branch --show-current)" \
     --title "<title>" \
     --body-file "<body-file>"
   ```

   For a user-owned fork, use `<head-owner>:<head-branch>`. For an organization-owned fork, `gh pr create --head <organization>:<branch>` is unsupported — use `GH_HOST="<host>" gh api` against the pull-request creation endpoint with explicit base/head repositories and branches.

Persist the returned PR URL, number, host, and repository, and pass that exact identity through every later call. If the user requested a draft, publish it and stop, explaining that landing is paused until they authorize marking it ready. Otherwise continue landing without yielding.

## Step 3: Resolve conflicts and staleness

```bash
GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json mergeable,mergeStateStatus
```

- If `mergeable` is `UNKNOWN`, wait and re-check; GitHub computes it asynchronously.
- If `mergeStateStatus` is `BEHIND`, or `mergeable` is `CONFLICTING`, merge the base branch in (`git fetch <remote>` then `git merge <remote>/<base-branch>`). Use `git merge`, not rebase, so no force push is needed.
- Resolve conflicts by reading the conflicting files and reconciling both sides' intent — never by blindly taking one side. Complete the merge commit, re-run the relevant validation, and push.
- If the remote branch advanced because of your own earlier push or merge, avoid a redundant merge; re-run the formatter locally if needed and push with `git push --force-with-lease`.

## Step 4: Watch checks and feedback

Poll the PR every 30 seconds. If GitHub API limits are constrained, slow to at most 300 seconds so CI is still sampled several times. Each cycle, refresh:

```bash
GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json state,isDraft,headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt
GH_HOST="$HOST" gh pr checks "$N" -R "$REPO"
GH_HOST="$HOST" gh api "repos/$REPO/issues/$N/comments"
GH_HOST="$HOST" gh api "repos/$REPO/pulls/$N/comments"
GH_HOST="$HOST" gh api "repos/$REPO/pulls/$N/reviews"
```

The `reviews` endpoint is not optional. A reviewer can put actionable feedback in the review **summary body** alone, which appears in neither the issue-comment nor the review-comment list, and a `COMMENTED` review does not move `reviewDecision` — without this call the grace window can expire and merge over feedback you never saw.

React to whatever changed:

- **Review or bot feedback outstanding** → handle it per **Step 5**, then restart this step.
- **Checks failed** → pull details with `GH_HOST="$HOST" gh pr checks "$N" -R "$REPO"`, derive the repository owning the failed run from its rollup details URL, and read logs with `GH_HOST="$HOST" gh run view <run-id> -R "<check-repository>" --log-failed`. Fix locally, commit, push, restart this step.
- **PR head changed** (a new `headRefOid` you did not push, e.g. a CI auto-fix commit) → integrate the new head without discarding local work: `git fetch <remote>` then `git merge --ff-only <remote>/<head-branch>`. Never `git reset --hard` and never stash — the worktree may legitimately hold tracked edits the user placed out of scope in Step 1. If the fast-forward is refused, or the worktree is dirty enough to block it, inspect the new head in an isolated temporary worktree (`git worktree add`) and reconcile deliberately. Auto-fix commits authored by GitHub Actions do **not** retrigger CI: merge the base ref if needed, add a real author commit, and push to retrigger. Then restart this step.
- **Behind, conflicting, or dirty merge state** → go back to **Step 3**.
- **State is `MERGED` or `CLOSED`** → stop watching. Report external merge as success; report a close without merge as terminal.

Treat every reported CI failure as blocking. If a failure looks flaky (for example, a single-platform timeout), rerun or re-watch until the check is green — never merge past it. If all jobs fail with a corrupted lockfile on the merge commit, the remediation is to fetch and merge the base ref, push, and rerun CI.

## Step 5: Handle review feedback

- Human review comments are blocking and must be addressed before merging.
- Codex reviews arrive as issue comments posted by GitHub Actions, starting with `## Codex Review — <persona>`. Treat them as feedback that must be acknowledged before merge. Codex review jobs retry on failure and are non-blocking; merge is gated by outstanding feedback plus the post-green wait, not by a requirement that a Codex review must arrive.
- Fetch inline feedback from the **review comment** endpoint and top-level discussion from the **issue comment** endpoint:

  ```bash
  GH_HOST="$HOST" gh api "repos/$REPO/pulls/$N/comments"
  GH_HOST="$HOST" gh api "repos/$REPO/issues/$N/comments"
  ```

  For unresolved threads, query `reviewThreads` via `gh api graphql --paginate` on the PR node id, selecting threads where `isResolved` and `isOutdated` are both false, and paginating each thread's own `comments` connection when `hasNextPage` is true.

**Per-comment mode.** For each comment choose exactly one of accept, clarify, or push back, and **reply before changing code**, stating the mode:

```bash
GH_HOST="$HOST" gh api --method POST \
  "repos/$REPO/pulls/$N/comments" \
  -f body='<response>' -F in_reply_to=<comment_id>
```

`in_reply_to` must be the numeric review comment id (e.g. `2710521800`), not the GraphQL node id. A 404 usually means the endpoint is missing the PR number or the token lacks scope — list comments first to verify. If a GraphQL reply mutation is forbidden, use REST. Reply to Codex review issue comments in the issue thread, not a review thread.

Then implement the fix, commit, push, and post the outcome (what changed plus the commit sha) in the same place you acknowledged the feedback.

- **Context guard:** before implementing feedback, confirm it does not conflict with the user's stated intent. If it does, reply inline with your justification and ask the user before changing code.
- **Pushback template:** acknowledge + rationale + offer an alternative.
- **Ambiguity gate:** when ambiguity blocks progress, assign the PR to the current GitHub user, mention them, and wait — do not implement until it is resolved. If you are confident you know better than the reviewer, you may proceed without asking, but reply inline with your rationale.
- If multiple reviewers comment in one thread, respond to each (batching is fine) before closing it.
- Do not submit a review unless the user asks. A thread counts as **addressed** for the Step 7 gate once you have replied to every comment in it and pushed the fix (or a justified pushback) — reviewers often never come back to resolve a thread themselves, and requiring GitHub's resolved flag would deadlock the loop. Resolve the thread yourself when your acknowledgement is the newest comment in it and the fix is pushed; leave it unresolved, and treat it as still blocking, whenever the newest comment is someone else's.
- Only request a new Codex review when there is at least one new commit since the last request and zero outstanding review comments. After pushing new commits, post a concise root-level delta summary:

  ```text
  Changes since last review:
  - <short bullets of deltas>
  Commits: <sha>, <sha>
  Tests: <commands run>
  ```

## Step 6: Wait for late feedback

Before starting this wait, make sure checks have actually appeared. An empty check list on an early poll usually means GitHub has not registered the workflow yet, not that the repository has no CI — starting the grace period there can merge just as the first job appears. Keep polling for at least 120 seconds after the head commit before accepting "no checks configured" as true, and restart at Step 4 the moment a check shows up.

After all required checks are green, wait 15 minutes before merging. If `LAND_WATCH_FEEDBACK_GRACE_SECONDS` is set to an integer from 30 to 86400, use that many seconds instead; reject invalid values rather than silently falling back to the default. During the wait, keep polling on the Step 4 cadence and restart the corresponding step whenever feedback appears, checks go pending or red, the head changes, or the merge state degrades.

Immediately before merging, synchronously refresh feedback, CI, the PR head, and merge state, and repeat until consecutive feedback and PR snapshots are unchanged with CI revalidated between them. Do not rely on an independently scheduled poll for the readiness verdict.

No Codex review is required to arrive. Absence of new actionable feedback for the full grace period after green checks is enough to proceed.

## Step 7: Merge

Merge only when all of these hold: not a draft, conflict-free and not behind, all checks green, every review thread addressed with no outstanding actionable feedback, and the grace window completed unchanged.

Use the repository's customary method. Prefer explicit user guidance; otherwise infer it from recent merge history (`git log <base-branch> -20 --merges` versus a linear history). Confirm the method is enabled on the repository; if it is ambiguous, ask instead of guessing.

Pin the merge to the exact head you validated. A commit pushed between the final snapshot and the merge call would otherwise be merged unvalidated; `--match-head-commit` makes GitHub reject the merge instead:

```sh
HEAD_SHA=$(GH_HOST="$HOST" gh pr view "$N" -R "$REPO" --json headRefOid -q .headRefOid)  # the validated head

# merge:  GH_HOST="$HOST" gh pr merge "$N" -R "$REPO" --merge  --match-head-commit "$HEAD_SHA"
# rebase: GH_HOST="$HOST" gh pr merge "$N" -R "$REPO" --rebase --match-head-commit "$HEAD_SHA"
# squash: GH_HOST="$HOST" gh pr merge "$N" -R "$REPO" --squash --match-head-commit "$HEAD_SHA" --subject "<pr-title>" --body "<pr-body>"
```

If the merge is rejected because the head moved, do not retry blindly — go back to Step 4 and revalidate the new head.

Do not enable auto-merge — a repository without required checks can auto-merge past a failing test. Do not delete the remote branch manually.

## Scope and PR metadata

- The PR title and description must reflect the full scope of the change, not just the latest fix.
- Classify each review comment as correctness, design, style, clarification, or scope.
- For correctness feedback, provide concrete validation (test, log, or reasoning) before closing it. If you plan to defer or decline a correctness concern, validate first and explain why it does not apply.
- When accepting feedback, include a one-line rationale in the root-level update; when declining, offer a brief alternative or follow-up trigger.
- Prefer a single consolidated "review addressed" root-level comment after a batch of fixes over many small updates.
- For documentation feedback, confirm the doc change matches behavior — no doc-only edits made to appease review.

## Output

```text
PR: #<number> <url>
Status: <what was handled this run>
Checks: <green/failed/pending summary>
Feedback: <handled / outstanding items>
Merged: <yes, via <method> / no — <blocker>>
```
