---
name: babysit
description: Keep a pull request healthy without merging it. Use when asked to babysit, shepherd, monitor, address feedback, fix CI, or keep a PR ready for merge.
---

# Babysit

## Goals

- Keep the current branch PR conflict-free, reviewed, and green.
- Address actionable review feedback and CI failures.
- Reuse the `land` skill's watcher to wait for late feedback after green checks (15 minutes by default).
- For continuous babysitting, use the host's recurring monitor or loop mechanism instead of relying on a single interactive turn.
- Stop with a readiness report and merge command.
- Never merge, squash-merge, delete branches, or enable auto-merge.

## Preconditions

- `gh` CLI is installed and authenticated.
- You are on the PR branch.
- The sibling `land` skill is installed in the same scope because this skill
  reuses `scripts/land_watch.py` from that skill.
- Resolve the active `babysit` skill directory from the path used to load this
  `SKILL.md`, then resolve `land` as its sibling. Do not hard-code a host skills
  directory. Run watcher commands from the PR repository working directory;
  `gh` resolves repository context from the process working directory.

## Steps

1. Locate the PR for the current branch:
   ```sh
   gh pr view --json number,title,state,url,headRefName,baseRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt
   ```
   Derive the selected PR coordinates for all follow-up CLI and API calls:
   ```sh
   PR_HOST=$(gh pr view --json url --jq '.url | split("/")[2]')
   PR_REPO=$(gh pr view --json url --jq '.url | split("/") | .[3:5] | join("/")')
   PR_NUMBER=$(gh pr view --json number --jq .number)
   ```
   If no PR exists on the current branch, say so and stop. If the PR state is
   `MERGED` or `CLOSED`, babysitting is terminal: stop the matching recurring
   monitor, delete `.git/babysit-state.json`, and report
   `Stopping babysit — PR #<n> is <state>.` This immediate stop overrides the
   idle threshold.
2. If the user asks to keep watching, continuously babysit, check back later,
   or monitor over time, create or update the host's recurring monitor for this
   PR. Use the current repository working directory, include the PR number and
   branch in the monitor prompt, tell it not to merge, and have it run this
   workflow. Prefer updating an existing matching monitor over creating a
   duplicate.

   For that continuous automation flow, stop after **3 consecutive runs** with **no new actionable feedback**:

   - Persist state in `.git/babysit-state.json` with shape `{"last_signature":"...","idle_count":0}`.
   - Compute `last_signature` from the PR feedback surface, including
     `updatedAt`, `reviewDecision`, latest comment and review IDs, and
     `statusCheckRollup` conclusions. When the host exposes the Claude sign-off
     notification adapter below, also include the Codex `+1` reaction count so
     a new sign-off resets the idle counter.
   - If the signature is unchanged vs the last run, increment `idle_count`; otherwise reset it to 0.
   - When `idle_count >= 3`, normally stop the recurring monitor and delete
     `.git/babysit-state.json`. On a host exposing the Claude sign-off adapter,
     keep monitoring instead when the Codex bot has activity on the PR and the
     current head has not yet received its `codex-ok:<sha>` sentinel: either
     sign-off or green CI may still arrive and trigger the promised
     notification. Terminal `MERGED` or `CLOSED` state always stops monitoring.
   - Report `Stopping babysit — 3 cycles with no new feedback on PR #<n>.`
     when the idle stop applies.
3. If the working tree has uncommitted changes, commit the intended scope and push before monitoring.
4. Check whether the PR is behind or conflicting with its base branch.
5. If behind or conflicting, merge the base branch, resolve conflicts, validate, commit, and push.
6. Run the shared watcher from the sibling `land` skill:
   ```sh
   python "$LAND_SKILL_DIR/scripts/land_watch.py"
   ```
   Resolve `LAND_SKILL_DIR` as the `land` sibling of the active installed
   `babysit` directory. Run the command from the PR repository working directory
   so `gh` uses the right repository. Use `python3` instead of `python` when that
   is the available launcher.
   The watcher polls GitHub every 30 seconds by default. To reduce API traffic further, set `LAND_WATCH_POLL_SECONDS` to an integer from 30 to 300 seconds before launching it. The feedback window defaults to 900 seconds; override it with `LAND_WATCH_FEEDBACK_GRACE_SECONDS`, using an integer from 30 to 86400. Before reporting readiness, it synchronously refreshes feedback, CI, the PR head, and merge state until consecutive feedback and PR snapshots are unchanged.
7. If the watcher exits `2`, fetch top-level comments, inline review comments, review summaries, unresolved threads when available, latest checks, and bot feedback. Classify each item, address actionable feedback, commit, push, leave `[agent]` response comments for addressed or intentionally deferred feedback, and rerun the watcher.
8. If the watcher exits `3`, inspect failing checks with `GH_HOST="$PR_HOST" gh pr checks "$PR_NUMBER" -R "$PR_REPO"` and `GH_HOST="$PR_HOST" gh run view <run-id> -R "$PR_REPO" --log`, fix the failure when concrete, commit, push, leave an `[agent]` response if the failure was reported in PR feedback, and rerun the watcher.
9. If the watcher exits `4`, refresh local state from the remote branch and rerun the watcher.
10. If the watcher exits `5`, merge the base branch, resolve conflicts, validate, push, leave an `[agent]` response if a thread/comment reported the conflict, and rerun the watcher.
11. If the watcher exits `6`, refresh the PR state. For `MERGED` or `CLOSED`,
    stop the matching recurring monitor, delete `.git/babysit-state.json`, and
    report the terminal stop without rerunning the watcher.
12. When the watcher succeeds, do not merge. Report the PR as ready and include:
    ```sh
    GH_HOST="$PR_HOST" gh pr merge "$PR_NUMBER" -R "$PR_REPO" --squash
    ```

## Claude sign-off notification adapter

Claude Code surfaces may expose `/loop`, `CronList`, `CronDelete`, and
`PushNotification`. These are host-only interfaces around the canonical
babysitting workflow, not a separate skill implementation. When they are
available:

- Use `/loop` or the equivalent recurring facility for continuous monitoring,
  and use `CronList` plus `CronDelete` to remove the matching loop on terminal
  or idle stop.
- When checks are green, poll `repos/$PR_REPO/issues/$PR_NUMBER/reactions` for
  a `+1` reaction from `chatgpt-codex-connector[bot]`. GitHub does not emit the
  needed wake-up reliably for reactions, so repeat this during the grace wait.
- Read `headRefOid` and labels. If the reaction is present, CI has no failed,
  pending, or cancelled checks, and `codex-ok:<head-sha>` is absent, call
  `PushNotification` with title `PR #<n> approved by Codex` and body
  `CI green + Codex 👍 — ready to merge: <url>`, then replace any stale
  `codex-ok:*` label with `codex-ok:<head-sha>`.
- Send at most one notification per head. A new commit changes the head SHA and
  therefore re-arms the notification. If the host lacks any of these
  interfaces, continue the normal watcher and readiness report without
  treating that absence as an error.
- Before reporting `Ready: yes` on Claude Code, synchronously refresh
  `reviewDecision` and require `APPROVED`. Treat `REVIEW_REQUIRED`, an empty
  decision, or `CHANGES_REQUESTED` as blocking even when the shared watcher
  succeeds. Other hosts follow the repository's required-approval policy.

## Review Handling

- Treat human review feedback as blocking until addressed or explicitly pushed back with rationale.
- Treat Codex review feedback as actionable when it raises a correctness, validation, or scope issue.
- Treat failed required checks as blocking feedback even if no human comment exists.
- After addressing a review thread, top-level comment, or bot feedback item, reply on GitHub with a concise `[agent]` comment that names the commit or rationale. Do not resolve review threads or submit a review unless the user explicitly asks.
- Use `[agent]` in GitHub comments so the watcher can distinguish acknowledgements from unresolved feedback. The watcher also accepts the legacy `[codex]` prefix.
- Do not over-expand PR scope. If a review asks for unrelated work, explain the deferral and suggest a follow-up.

## Watcher Semantics

The shared `land` watcher monitors feedback, checks, and PR head changes in parallel at a 30-second default polling cadence. It returns success only after the PR is conflict-free and the configurable feedback grace window (15 minutes by default) completes with no outstanding feedback, followed by authoritative final feedback, CI, PR-head, and merge-state refreshes that converge on unchanged feedback and PR snapshots. CI checks and review feedback are monitored independently; when no CI checks are detected, the watcher still runs the feedback grace window while continuing to poll for checks.

A Codex review is not required to arrive. Absence of new actionable feedback for the full configured post-green wait is acceptable.

Exit codes:

- `2`: review or bot feedback must be handled
- `3`: CI checks failed
- `4`: PR head changed and local state must be refreshed
- `5`: PR is behind its base, has merge conflicts, or has a dirty merge state
- `6`: PR was merged or closed; stop watching permanently

## Output

```text
PR #<number>: <title>
Status: <what was handled this cycle>
Ready: <yes/no>
Merge: GH_HOST="$PR_HOST" gh pr merge "$PR_NUMBER" -R "$PR_REPO" --squash
Blocking: <remaining blocker or "none">
```
