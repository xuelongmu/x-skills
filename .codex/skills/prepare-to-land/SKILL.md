---
name: prepare-to-land
description: Prepare a pull request for someone else to merge by reviewing and responding to feedback, resolving merge conflicts, fixing CI failures, and verifying merge readiness without merging, enabling auto-merge, or deleting branches. Use when asked to address PR feedback, make a PR merge-ready, resolve conflicts before handoff, or shepherd a PR without landing it.
---

# Prepare to Land

## Goals

- Leave the PR conflict-free, reviewed, validated, and ready for a human or another agent to merge.
- Review every relevant feedback surface and respond where the feedback appeared.
- Address actionable review feedback and CI failures without expanding scope unnecessarily.
- Never merge the PR, enable auto-merge, close the PR, or delete local or remote branches.

## Preconditions

- Ensure `gh` is installed and authenticated.
- Work from the PR branch in the repository working directory.
- Preserve unrelated local changes. Commit only changes belonging to this PR.
- Reuse the sibling `land` skill's `land_watch.py`. Resolve `LAND_SKILL_DIR` to the project-local `.codex/skills/land` when present, otherwise to the global `land` skill.

## Workflow

1. Locate the PR for the current branch and inspect its title, body, base branch, head branch, merge state, review decision, and checks.
2. Inspect the working tree and preserve unrelated changes. Validate and publish any intended in-scope changes before monitoring.
3. Fetch all feedback surfaces:
   - inline review comments and threads
   - review summaries and requested changes
   - top-level PR comments, including Codex review issue comments
   - failed or pending required checks
4. Classify each feedback item as `accept`, `clarify`, or `push back`, and as correctness, design, style, clarification, or scope.
5. Before changing code, reply where the feedback appeared with a concise `[codex]` acknowledgement and intended action:
   - Accept: state the fix you will make.
   - Clarify: ask the smallest blocking question and wait when the answer materially affects the change.
   - Push back: acknowledge the concern, give concrete rationale, and offer an alternative.
6. Implement accepted feedback. For correctness concerns, validate with a focused test, log, reproduction, or concrete reasoning.
7. Commit and push the fixes. Reply in the same thread with the result, validation, and commit SHA. Use a concise root-level `[codex]` summary after a batch of changes.
8. Fetch the latest base branch. If the PR is behind or conflicting, integrate the base branch using the repository's customary update strategy, resolve conflicts, validate the combined result, commit if needed, and push.
9. Run the shared watcher:

   ```sh
   python "$LAND_SKILL_DIR/land_watch.py"
   ```

   Use `python3` when that is the available launcher. Run it from the PR repository so `gh` resolves the correct PR.
10. Handle watcher results and rerun until successful or genuinely blocked:
    - `2`: inspect and address feedback.
    - `3`: inspect failed checks, fix concrete failures, validate, commit, and push.
    - `4`: refresh the local branch from the remote PR head.
    - `5`: update from the base branch and resolve conflicts or dirty merge state.
11. When the watcher succeeds, stop. Report readiness and remaining blockers. Do not execute or schedule any merge operation.

## Review Rules

- Confirm feedback is compatible with the user's intent before implementing it.
- Treat human requested changes and unresolved correctness concerns as blocking until addressed or explicitly declined with evidence.
- Reply inline to inline review comments; reply in the top-level issue discussion to top-level or Codex review comments.
- Prefix every GitHub comment written by the agent with `[codex]`.
- Use the numeric review comment ID with the REST `in_reply_to` field when replying inline.
- Do not make doc-only edits that claim behavior the code does not have.
- Defer unrelated work with a clear reason and a suggested follow-up.
- Do not resolve review threads or submit an approving review unless the user explicitly asks.

## Conflict and CI Rules

- Never discard either side of a conflict wholesale without understanding both changes.
- Run the repository's full required validation after conflict resolution and focused validation for every review fix.
- Treat required CI failures as blocking. Inspect logs and fix failures attributable to the PR.
- If a failure is plausibly flaky, rerun it and require a green result rather than ignoring it.
- If mergeability is `UNKNOWN`, wait and recheck.
- If the PR head changes remotely, refresh before making further edits.

## Hard Stop Before Merge

The following actions are forbidden, even when all gates are green:

- `gh pr merge` in any mode
- enabling or scheduling auto-merge
- merging through the GitHub UI or API
- closing the PR as a substitute for merging
- deleting branches
- asking another agent or automation to merge

Finish with:

```text
PR #<number>: <title>
Ready to merge: <yes/no>
Feedback handled: <summary>
Conflicts handled: <summary>
Validation: <checks run and results>
Blocking: <remaining blocker or "none">
Next action: Human or authorized landing workflow may merge the PR.
```
