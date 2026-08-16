---
name: land
description:
  Publish local changes into a pull request when needed, then land the PR by
  resolving conflicts, keeping CI green, handling feedback, and using the
  repository's customary merge method; use when asked to land, merge, or
  shepherd work or a PR to completion.
---

# Land

## Goals

- Ensure the PR is conflict-free with main.
- Open a ready-for-review PR when the intended work does not already have one.
- Keep CI green and fix failures when they occur.
- Use the repository's customary merge method: merge commit, rebase, or squash.
- Do not yield to the user until the PR is merged; keep the watcher loop running
  unless blocked.
- No need to delete remote branches after merge; the repo auto-deletes head
  branches.

## Preconditions

- Require a local Git repository with an accessible GitHub remote.
- Require an authenticated connected GitHub app or `gh` CLI session for the
  selected host.
- When `gh` is unavailable but the connected GitHub app is authenticated, use
  the app for PR creation and perform equivalent CI, feedback, head, and merge
  polling; never skip a land gate because the bundled watcher cannot run.
- This skill may be installed project-locally in `.codex/skills/land` or globally in `$CODEX_HOME/skills/land` / `~/.codex/skills/land`.
- Run watcher commands from the PR repository working directory. The watcher script path comes from this installed skill directory, but `gh` resolves repository context from the process cwd.

## Steps

1. Establish the intended scope, GitHub remote, target repository, and base
   branch. Inspect the complete status, diff, untracked files, and branch range;
   never include unrelated changes silently.
2. Locate an open PR for the current branch in the target repository. Prefer a
   PR the user named by number or URL over current-branch discovery. Read
   `isDraft` with the rest of the PR fields: a draft cannot merge, so mark it
   ready before watching when the user asked to land it, or stop and say
   landing is paused when they explicitly want it kept as a draft. Treat a
   `MERGED`/`CLOSED` result as terminal only when the user named that PR;
   `gh pr view` also resolves stale branch PRs, so publish the branch's newer
   work through step 3 instead.
3. If no open PR exists, prepare and publish one using the **Open a PR when
   needed** workflow below. Create it ready for review unless the user
   explicitly requested a draft.
4. Before every push, stage and review only the intended changes, then confirm
   the full gauntlet is green against that exact state. If the PR already
   existed, commit the validated staged changes and push them to the selected PR
   branch.
5. Check mergeability and conflicts against the target base branch.
6. If conflicts exist, use the `pull` skill to fetch/merge the target base and
   resolve conflicts, then use the `push` skill to publish the updated branch.
7. Ensure Codex review comments (if present) are acknowledged and any required
   fixes are handled before merging.
8. Watch checks until complete, then continue watching PR feedback for the
   configured grace window (15 minutes by default) before merging.
9. If checks fail, pull logs, fix the issue, commit with the `commit` skill,
   push with the `push` skill, and re-run checks.
10. After all merge gates pass, use the repository's customary method: prefer
   explicit guidance, otherwise infer from recent merge history. Confirm the
   method is enabled; if ambiguous, ask instead of guessing. Do not manually
   delete the remote branch.
11. **Context guard:** Before implementing review feedback, confirm it does not
    conflict with the user’s stated intent or task context. If it conflicts,
    respond inline with a justification and ask the user before changing code.
12. **Pushback template:** When disagreeing, reply inline with: acknowledge +
    rationale + offer alternative.
13. **Ambiguity gate:** When ambiguity blocks progress, use the clarification
    flow (assign PR to current GH user, mention them, wait for response). Do not
    implement until ambiguity is resolved.
    - If you are confident you know better than the reviewer, you may proceed
      without asking the user, but reply inline with your rationale.
14. **Per-comment mode:** For each review comment, choose one of: accept,
    clarify, or push back. Reply inline (or in the issue thread for Codex
    reviews) stating the mode before changing code.
15. **Reply before change:** Always respond with intended action before pushing
    code changes (inline for review comments, issue thread for Codex reviews).

## Open a PR when needed

When the current work has no open PR:

1. Select and verify the push remote, GitHub hostname, head repository, target
   repository, and base branch. Preserve an explicitly requested base; otherwise
   use the repository default. Keep head and base repositories distinct for
   fork workflows.
2. If detached or on the target base branch, create a focused branch before
   staging or committing. Otherwise keep the current branch unless the user
   requested a new one.
3. Refresh the target base ref. Inspect `git log <base-ref>..HEAD --oneline` and
   `git diff <base-ref>...HEAD` together with the worktree diff and every
   intended untracked file. Stop if scope is ambiguous or there is nothing to
   publish.
4. Stage only intended files and review the complete staged diff. Do not commit
   yet.
5. Run the relevant local validation against that exact staged worktree. Fix
   attributable failures within scope, stage the fixes, review the staged diff
   again, and rerun affected checks. When unrelated unstaged changes coexist,
   materialize the index in an isolated temporary worktree and validate there;
   do not test the mixed working tree or stash the user's changes. Then create a
   terse commit when staged changes exist. Reuse unpublished branch commits;
   never create an empty commit.
6. Push the selected branch with upstream tracking. Never force-push unless the
   user explicitly authorized it or the established workflow clearly requires
   it and the target is verified.
7. Write a title for the full branch diff and a Markdown body covering what and
   why, user impact, validation, and any limitations.
8. Recheck for an open PR after the push to avoid duplicates. If none exists,
   create it with the prepared title and body. Prefer the connected GitHub app;
   use `gh` only as fallback. Explicitly target the selected base/head
   repositories and branches, and set draft to false unless the user requested
   a draft. Persist the returned PR URL, number, hostname, and repository; pass
   that exact identity through the watcher, review-handling, and merge flows. If
   the user requested a draft, stop after publishing it and explain that landing
   is paused until they authorize marking it ready. Otherwise continue the land
   workflow without yielding.

For a same-repository CLI fallback:

```sh
gh pr create --repo "<host>/<base-owner>/<base-repository>" \
  --base "<base-branch>" \
  --head "$(git branch --show-current)" \
  --title "<title>" \
  --body-file "<body-file>"
```

For a user-owned fork, use `<head-owner>:<head-branch>`. For an
organization-owned fork, use the connected GitHub app or
`GH_HOST="<host>" gh api` with explicit base/head repositories and branches;
do not rely on the unsupported CLI `--head <organization>:<branch>` path or an
unqualified API call that defaults to `github.com`.

## Commands

```
# Ensure branch and PR context
branch=$(git branch --show-current)
# If no open PR resolves here, run "Open a PR when needed" above, then retry.
pr_url="${LAND_WATCH_PR:-}"
if [ -z "$pr_url" ]; then
  pr_url=$(gh pr view --json url -q .url)
fi
export LAND_WATCH_PR="$pr_url"
pr_number=$(gh pr view "$pr_url" --json number -q .number)
pr_host=$(gh pr view "$pr_url" --json url --jq '.url | split("/")[2]')
pr_repo=$(gh pr view "$pr_url" --json url --jq '.url | split("/") | .[3:5] | join("/")')
pr_selector="$pr_repo"
pr_title=$(GH_HOST="$pr_host" gh pr view "$pr_number" -R "$pr_selector" --json title -q .title)
pr_body=$(GH_HOST="$pr_host" gh pr view "$pr_number" -R "$pr_selector" --json body -q .body)

# Check out the selected PR by number before touching Git state; otherwise
# conflict resolution and CI fixes mutate whatever branch happens to be checked
# out. Do not skip this on a matching branch name — a fork's head branch can
# share the local name while pointing at unrelated commits. Use
# `git worktree add` instead when the current worktree must be preserved.
GH_HOST="$pr_host" gh pr checkout "$pr_number" -R "$pr_selector"

# Check mergeability and conflicts
mergeable=$(GH_HOST="$pr_host" gh pr view "$pr_number" -R "$pr_selector" --json mergeable -q .mergeable)

if [ "$mergeable" = "CONFLICTING" ]; then
  # Run the `pull` skill to handle fetch + merge + conflict resolution.
  # Then run the `push` skill to publish the updated branch.
fi

# Capture the head immediately before watching — after any conflict-resolution
# push above, or the merge would pin a superseded sha and be rejected. A clean
# watcher exit proves this exact sha stayed green (it exits 4 on any head
# change), so it is the validated sha to pin at merge.
head_sha=$(GH_HOST="$pr_host" gh pr view "$pr_number" -R "$pr_selector" --json headRefOid -q .headRefOid)

# Preferred: use the Async Watch Helper below. It watches review feedback,
# checks, and PR head changes in parallel. After checks pass (or when no CI
# checks are detected), it keeps polling feedback for the configured grace
# window (15 minutes by default). A Codex review is not required to arrive; no
# actionable feedback during that wait is enough to proceed.
if ! LAND_WATCH_PR="$pr_url" python3 "$LAND_SKILL_DIR/land_watch.py"; then
  # Exit code 2 means review feedback must be handled.
  # Exit code 3 means checks failed.
  # Exit code 4 means the PR head changed and local state must be refreshed.
  # Exit code 5 means the PR is behind, conflicting, or dirty.
  # Exit code 6 means the PR was merged or closed while being watched.
  exit 1
fi

# Run the customary enabled method, pinned to the validated head so a commit
# pushed in the gap is rejected. On rejection, re-run the watcher against the
# new head instead of retrying.
# merge:  GH_HOST="$pr_host" gh pr merge "$pr_number" -R "$pr_selector" --merge  --match-head-commit "$head_sha"
# rebase: GH_HOST="$pr_host" gh pr merge "$pr_number" -R "$pr_selector" --rebase --match-head-commit "$head_sha"
# squash: GH_HOST="$pr_host" gh pr merge "$pr_number" -R "$pr_selector" --squash --match-head-commit "$head_sha" --subject "$pr_title" --body "$pr_body"

# A successful merge command only enqueues the PR when the base branch uses a
# merge queue, and a queued PR can be ejected. Re-check until GitHub reports
# MERGED; rerun the watcher if it comes back blocked.
GH_HOST="$pr_host" gh pr view "$pr_number" -R "$pr_selector" --json state,mergeStateStatus
```

## Async Watch Helper

Preferred: use the asyncio watcher to monitor review comments, CI, and head
updates in parallel:

```
python3 "$LAND_SKILL_DIR/land_watch.py"
```

Resolve `LAND_SKILL_DIR` to this installed skill directory before running the
watcher. Prefer the current repo's `.codex/skills/land` when present; otherwise use
`${CODEX_HOME:-$HOME/.codex}/skills/land` or
`%USERPROFILE%\.codex\skills\land`. Run the command from the PR repository
working directory so `gh` uses the right repo.

The watcher polls GitHub every 30 seconds by default to avoid exhausting API
limits. For a slower cadence, set `LAND_WATCH_POLL_SECONDS` to an integer from
30 to 300 before launching it. The feedback grace window defaults to 900
seconds (15 minutes); set `LAND_WATCH_FEEDBACK_GRACE_SECONDS` to an integer from
30 to 86400 to override it. Set `LAND_WATCH_PR` to the exact PR URL returned by
creation so the watcher cannot resolve another PR for the same branch or
checkout. Before returning success, the watcher performs
authoritative final CI, PR-head, merge-state, and feedback refreshes until
consecutive feedback and PR snapshots are unchanged. For example:

```
LAND_WATCH_PR="$pr_url" LAND_WATCH_POLL_SECONDS=60 LAND_WATCH_FEEDBACK_GRACE_SECONDS=600 python3 "$LAND_SKILL_DIR/land_watch.py"
```

Exit codes:

- 2: Review comments detected before merge (address feedback)
- 3: CI checks failed
- 4: PR head updated (autofix commit detected)
- 5: PR is behind, conflicting, or dirty
- 6: PR is merged or closed; refresh state and stop watching

The helper returns success only after the PR is conflict-free, checks are green,
and the configured feedback grace period passes after green checks with no
outstanding feedback. It does not require a Codex review to arrive; absence of
feedback after the grace period is acceptable.

## Failure Handling

- If checks fail, pull details with
  `GH_HOST="$pr_host" gh pr checks "$pr_number" -R "$pr_selector"` and
  derive the repository that owns the failed run from its rollup details URL,
  then use `GH_HOST="$pr_host" gh run view <run-id> -R "<check-repository>" --log`.
  Fix locally, commit
  with the `commit` skill, push with the `push` skill, and re-run the watch.
- Treat every reported CI failure as blocking. If a failure looks flaky (for
  example, a timeout on one platform), rerun or re-watch until the check is
  green before proceeding.
- If CI pushes an auto-fix commit (authored by GitHub Actions), it does not
  trigger a fresh CI run. Detect the updated PR head, pull locally, merge
  the selected target base ref if needed, add a real author commit, and push to
  the verified PR remote to retrigger CI, then restart the checks loop.
- If all jobs fail with corrupted pnpm lockfile errors on the merge commit, the
  remediation is to fetch and merge the selected target base ref, push to the
  verified PR remote, and rerun CI.
- If mergeability is `UNKNOWN`, wait and re-check.
- If the watcher exits `6`, refresh the PR state. Treat `MERGED` as successful external completion; treat `CLOSED` without merge as terminal and report that no merge occurred.
- Do not merge while review comments (human or Codex review) are outstanding.
- Codex review jobs retry on failure and are non-blocking; merge is gated by
  outstanding feedback plus the configured post-green feedback wait, not by a
  requirement that a Codex review comment must arrive.
- Do not enable auto-merge; this repo has no required checks so auto-merge can
  skip tests.
- If the remote PR branch advanced, fetch and fast-forward or merge that head
  before pushing again; avoid redundant merges and re-run the formatter locally
  if needed. Do not force-push over it: `--force-with-lease` only compares the
  remote ref against your last fetch, so after a fetch it will still discard CI
  fixes or another worktree's commits. Reserve force-pushing for a history
  rewrite the user explicitly authorized.

## Review Handling

- Codex reviews now arrive as issue comments posted by GitHub Actions. They
  start with `## Codex Review — <persona>` and include the reviewer’s
  methodology + guardrails used. Treat these as feedback that must be
  acknowledged before merge.
- Human review comments are blocking and must be addressed (responded to and
  resolved) before requesting a new review or merging.
- If multiple reviewers comment in the same thread, respond to each comment
  (batching is fine) before closing the thread.
- Derive API coordinates from the selected PR before fetching or replying; do
  not use checkout-derived placeholders or the CLI's default hostname:
  ```sh
  PR_URL="${LAND_WATCH_PR:-$(gh pr view --json url --jq .url)}"
  PR_HOST=$(gh pr view "$PR_URL" --json url --jq '.url | split("/")[2]')
  PR_REPO=$(gh pr view "$PR_URL" --json url --jq '.url | split("/") | .[3:5] | join("/")')
  PR_NUMBER=$(gh pr view "$PR_URL" --json number --jq .number)
  ```
- Fetch review comments via `gh api` and reply with a prefixed comment.
- Use review comment endpoints (not issue comments) to find inline feedback:
  - List PR review comments:
    ```
    GH_HOST="$PR_HOST" gh api --paginate "repos/$PR_REPO/pulls/$PR_NUMBER/comments"
    ```
  - PR issue comments (top-level discussion):
    ```
    GH_HOST="$PR_HOST" gh api --paginate "repos/$PR_REPO/issues/$PR_NUMBER/comments"
    ```
  - Review summaries (feedback left only in a review body appears in neither
    list above):
    ```
    GH_HOST="$PR_HOST" gh api --paginate "repos/$PR_REPO/pulls/$PR_NUMBER/reviews"
    ```
  - Reply to a specific review comment:
    ```
    GH_HOST="$PR_HOST" gh api --method POST \
      "repos/$PR_REPO/pulls/$PR_NUMBER/comments" \
      -f body='[codex] <response>' -F in_reply_to=<comment_id>
    ```
- `in_reply_to` must be the numeric review comment id (e.g., `2710521800`), not
  the GraphQL node id (e.g., `PRRC_...`), and the endpoint must include the PR
  number (`/pulls/<pr_number>/comments`).
- If GraphQL review reply mutation is forbidden, use REST.
- A 404 on reply typically means the wrong endpoint (missing PR number) or
  insufficient scope; verify by listing comments first.
- All GitHub comments generated by this agent must be prefixed with `[codex]`.
- For Codex review issue comments, reply in the issue thread (not a review
  thread) with `[codex]` and state whether you will address the feedback now or
  defer it (include rationale).
- If feedback requires changes:
  - For inline review comments (human), reply with intended fixes
    (`[codex] ...`) **as an inline reply to the original review comment** using
    the review comment endpoint and `in_reply_to` (do not use issue comments for
    this).
  - Implement fixes, commit, push.
  - Reply with the fix details and commit sha (`[codex] ...`) in the same place
    you acknowledged the feedback (issue comment for Codex reviews, inline reply
    for review comments).
  - The land watcher treats Codex review issue comments as unresolved until a
    newer `[codex]` issue comment is posted acknowledging the findings.
- Only request a new Codex review when you need a rerun (e.g., after new
  commits). Do not request one without changes since the last review.
  - Before requesting a new Codex review, re-run the land watcher and ensure
    there are zero outstanding review comments (all have `[codex]` inline
    replies).
  - After pushing new commits, the Codex review workflow will rerun on PR
    synchronization (or you can re-run the workflow manually). Post a concise
    root-level summary comment so reviewers have the latest delta:
    ```
    [codex] Changes since last review:
    - <short bullets of deltas>
    Commits: <sha>, <sha>
    Tests: <commands run>
    ```
  - Only request a new review if there is at least one new commit since the
    previous request.
  - Having requested one, wait for that review to arrive before merging. This
    is the only case where a Codex review is required; otherwise the grace
    window alone gates the merge.

## Scope + PR Metadata

- The PR title and description should reflect the full scope of the change, not
  just the most recent fix.
- If review feedback expands scope, decide whether to include it now or defer
  it. You can accept, defer, or decline feedback. If deferring or declining,
  call it out in the root-level `[codex]` update with a brief reason (e.g.,
  out-of-scope, conflicts with intent, unnecessary).
- Correctness issues raised in review comments should be addressed. If you plan
  to defer or decline a correctness concern, validate first and explain why the
  concern does not apply.
- Classify each review comment as one of: correctness, design, style,
  clarification, scope.
- For correctness feedback, provide concrete validation (test, log, or
  reasoning) before closing it.
- When accepting feedback, include a one-line rationale in the root-level
  update.
- When declining feedback, offer a brief alternative or follow-up trigger.
- Prefer a single consolidated "review addressed" root-level comment after a
  batch of fixes instead of many small updates.
- For doc feedback, confirm the doc change matches behavior (no doc-only edits
  to appease review).
