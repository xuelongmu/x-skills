---
name: babysit
description: Keep a pull request healthy without merging it; use when Codex needs to babysit, shepherd, monitor, address feedback, fix CI, or keep a PR ready for merge.
---

# Babysit

## Goals

- Keep the current branch PR conflict-free, reviewed, and green.
- Address actionable review feedback and CI failures.
- Reuse the `land` skill's watcher to wait 10 minutes after green checks for late feedback.
- For continuous babysitting, create or update a Codex cron automation for the PR instead of relying on a single interactive turn.
- Stop with a readiness report and merge command.
- Never merge, squash-merge, delete branches, or enable auto-merge.

## Preconditions

- `gh` CLI is installed and authenticated.
- You are on the PR branch.
- The sibling `land` skill is installed in the same scope because this skill reuses `land_watch.py` from that skill.
- If this skill is project-local, use `.codex/skills/land`; if this skill is global, use `$CODEX_HOME/skills/land` or `~/.codex/skills/land`.
- Run watcher commands from the PR repository working directory. The watcher script path comes from the installed `land` skill, but `gh` resolves repository context from the process cwd.

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
   If no PR exists on the current branch, say so and stop. If the PR state is `MERGED` or `CLOSED`, babysitting is terminal: disable/delete the matching cron automation, delete `.git/babysit-state.json`, and report `Stopping babysit — PR #<n> is <state>.` This immediate stop overrides the idle threshold and any pending Codex sign-off notification.
2. If the user asks to keep watching, continuously babysit, check back later, or monitor over time, create or update a Codex cron automation for this PR. Use the current repo cwd, include the PR number and branch in the automation prompt, tell it not to merge, and have it run this babysit workflow. Prefer updating an existing matching automation over creating a duplicate.

   For that continuous automation flow, stop after **3 consecutive runs** with **no new actionable feedback**:

   - Persist state in `.git/babysit-state.json` with shape `{"last_signature":"...","idle_count":0}`.
   - Compute `last_signature` from the PR feedback surface (for example: `updatedAt`, `reviewDecision`, latest comment/review IDs, `statusCheckRollup` conclusions, and the Codex 👍 count so a fresh sign-off resets the idle counter).
   - If the signature is unchanged vs the last run, increment `idle_count`; otherwise reset it to 0.
   - When `idle_count >= 3`, stop babysitting unless a Codex sign-off notification is still pending: if the Codex review bot has activity on the PR but the current head has not been marked as notified, keep running until the notification fires or the PR becomes terminal. If the bot has no activity, the three-cycle idle stop applies normally.
   - When the idle threshold applies, disable/delete the cron automation, delete `.git/babysit-state.json`, and report: `Stopping babysit — 3 cycles with no new feedback on PR #<n>.`
3. If the working tree has uncommitted changes, commit the intended scope and push before monitoring.
4. Check whether the PR is behind or conflicting with its base branch.
5. If behind or conflicting, merge the base branch, resolve conflicts, validate, commit, and push.
6. Run the shared watcher from the sibling `land` skill:
   ```sh
   python "$LAND_SKILL_DIR/land_watch.py"
   ```
   Resolve `LAND_SKILL_DIR` before running: prefer the current repo's `.codex/skills/land` when present, otherwise use `${CODEX_HOME:-$HOME/.codex}/skills/land` or `%USERPROFILE%\.codex\skills\land`. Run the command from the PR repository working directory so `gh` uses the right repo. Use `python3` instead of `python` when that is the available launcher.
   The watcher polls GitHub every 30 seconds by default. To reduce API traffic further, set `LAND_WATCH_POLL_SECONDS` to an integer from 30 to 300 seconds before launching it. Before reporting readiness, it synchronously refreshes feedback, CI, the PR head, and merge state until consecutive feedback and PR snapshots are unchanged.
7. If the watcher exits `2`, fetch top-level comments, inline review comments, review summaries, unresolved threads when available, latest checks, and bot feedback. Classify each item, address actionable feedback, commit, push, leave `[codex]` response comments for addressed or intentionally deferred feedback, and rerun the watcher.
8. If the watcher exits `3`, inspect failing checks with `GH_HOST="$PR_HOST" gh pr checks "$PR_NUMBER" -R "$PR_REPO"` and `GH_HOST="$PR_HOST" gh run view <run-id> -R "$PR_REPO" --log`, fix the failure when concrete, commit, push, leave a `[codex]` response if the failure was reported in PR feedback, and rerun the watcher.
9. If the watcher exits `4`, refresh local state from the remote branch and rerun the watcher.
10. If the watcher exits `5`, merge the base branch, resolve conflicts, validate, push, leave a `[codex]` response if a thread/comment reported the conflict, and rerun the watcher.
11. If the watcher exits `6`, refresh the PR state. For `MERGED` or `CLOSED`, disable/delete the matching cron automation, delete `.git/babysit-state.json`, and report the terminal stop without rerunning the watcher.
12. When the watcher succeeds, do not merge. Report the PR as ready and include:
    ```sh
    GH_HOST="$PR_HOST" gh pr merge "$PR_NUMBER" -R "$PR_REPO" --squash
    ```

## Review Handling

- Treat human review feedback as blocking until addressed or explicitly pushed back with rationale.
- Treat Codex review feedback as actionable when it raises a correctness, validation, or scope issue.
- Treat failed required checks as blocking feedback even if no human comment exists.
- After addressing a review thread, top-level comment, or bot feedback item, reply on GitHub with a concise `[codex]` comment that names the commit or rationale. Do not resolve review threads or submit a review unless the user explicitly asks.
- Use `[codex]` in GitHub comments so the watcher can distinguish acknowledgements from unresolved feedback.
- Do not over-expand PR scope. If a review asks for unrelated work, explain the deferral and suggest a follow-up.

## Watcher Semantics

The shared `land` watcher monitors feedback, checks, and PR head changes in parallel at a 30-second default polling cadence. It returns success only after the PR is conflict-free and a 10-minute feedback grace window completes with no outstanding feedback, followed by authoritative final feedback, CI, PR-head, and merge-state refreshes that converge on unchanged feedback and PR snapshots. CI checks and review feedback are monitored independently; when no CI checks are detected, the watcher still runs the feedback grace window while continuing to poll for checks.

A Codex review is not required to arrive. Absence of new actionable feedback for the full 10-minute post-green wait is acceptable.

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
