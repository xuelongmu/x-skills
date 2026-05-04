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
   gh pr view --json number,title,url,headRefName,baseRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
   ```
2. If the user asks to keep watching, continuously babysit, check back later, or monitor over time, create or update a Codex cron automation for this PR. Use the current repo cwd, include the PR number and branch in the automation prompt, tell it not to merge, and have it run this babysit workflow. Prefer updating an existing matching automation over creating a duplicate.
3. If the working tree has uncommitted changes, commit the intended scope and push before monitoring.
4. Check whether the PR is behind or conflicting with its base branch.
5. If behind or conflicting, merge the base branch, resolve conflicts, validate, commit, and push.
6. Run the shared watcher from the sibling `land` skill:
   ```sh
   python "$LAND_SKILL_DIR/land_watch.py"
   ```
   Resolve `LAND_SKILL_DIR` before running: prefer the current repo's `.codex/skills/land` when present, otherwise use `${CODEX_HOME:-$HOME/.codex}/skills/land` or `%USERPROFILE%\.codex\skills\land`. Run the command from the PR repository working directory so `gh` uses the right repo. Use `python3` instead of `python` when that is the available launcher.
7. If the watcher exits `2`, fetch top-level comments, inline review comments, review summaries, unresolved threads when available, latest checks, and bot feedback. Classify each item, address actionable feedback, commit, push, leave `[codex]` response comments for addressed or intentionally deferred feedback, and rerun the watcher.
8. If the watcher exits `3`, inspect failing checks with `gh pr checks` and `gh run view --log`, fix the failure when concrete, commit, push, leave a `[codex]` response if the failure was reported in PR feedback, and rerun the watcher.
9. If the watcher exits `4`, refresh local state from the remote branch and rerun the watcher.
10. If the watcher exits `5`, merge the base branch, resolve conflicts, validate, push, leave a `[codex]` response if a thread/comment reported the conflict, and rerun the watcher.
11. When the watcher succeeds, do not merge. Report the PR as ready and include:
    ```sh
    gh pr merge <number> --squash
    ```

## Review Handling

- Treat human review feedback as blocking until addressed or explicitly pushed back with rationale.
- Treat Codex review feedback as actionable when it raises a correctness, validation, or scope issue.
- Treat failed required checks as blocking feedback even if no human comment exists.
- After addressing a review thread, top-level comment, or bot feedback item, reply on GitHub with a concise `[codex]` comment that names the commit or rationale. Do not resolve review threads or submit a review unless the user explicitly asks.
- Use `[codex]` in GitHub comments so the watcher can distinguish acknowledgements from unresolved feedback.
- Do not over-expand PR scope. If a review asks for unrelated work, explain the deferral and suggest a follow-up.

## Watcher Semantics

The shared `land` watcher monitors feedback, checks, and PR head changes in parallel. It returns success only after the PR is conflict-free, checks are green, and 10 minutes pass after green checks with no outstanding feedback.

A Codex review is not required to arrive. Absence of new actionable feedback for the full 10-minute post-green wait is acceptable.

Exit codes:

- `2`: review or bot feedback must be handled
- `3`: CI checks failed or never appeared
- `4`: PR head changed and local state must be refreshed
- `5`: PR has merge conflicts or a dirty merge state

## Output

```text
PR #<number>: <title>
Status: <what was handled this cycle>
Ready: <yes/no>
Merge: gh pr merge <number> --squash
Blocking: <remaining blocker or "none">
```
