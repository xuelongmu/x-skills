---
name: babysit
description: Keep a pull request healthy without merging it; use when Codex needs to babysit, shepherd, monitor, address feedback, fix CI, or keep a PR ready for merge.
---

# Babysit

## Goals

- Keep the current branch PR conflict-free, reviewed, and green.
- Address actionable review feedback and CI failures.
- Wait 10 minutes after green checks for late feedback.
- Stop with a readiness report and merge command.
- Never merge, squash-merge, delete branches, or enable auto-merge.

## Preconditions

- `gh` CLI is installed and authenticated.
- You are on the PR branch.

## Steps

1. Locate the PR for the current branch:
   ```sh
   gh pr view --json number,title,url,headRefName,baseRefName,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
   ```
2. If the working tree has uncommitted changes, commit the intended scope and push before monitoring.
3. Check whether the PR is behind or conflicting with its base branch.
4. If behind or conflicting, merge the base branch, resolve conflicts, validate, commit, and push.
5. Run the bundled watcher from this skill directory:
   ```sh
   python scripts/land_watch.py
   ```
   Use `python3` instead of `python` when that is the available launcher.
6. If the watcher exits `2`, fetch top-level comments, inline review comments, review summaries, unresolved threads when available, latest checks, and bot feedback. Classify each item, address actionable feedback, commit, push, and rerun the watcher.
7. If the watcher exits `3`, inspect failing checks with `gh pr checks` and `gh run view --log`, fix the failure when concrete, commit, push, and rerun the watcher.
8. If the watcher exits `4`, refresh local state from the remote branch and rerun the watcher.
9. If the watcher exits `5`, merge the base branch, resolve conflicts, validate, push, and rerun the watcher.
10. When the watcher succeeds, do not merge. Report the PR as ready and include:
    ```sh
    gh pr merge <number> --squash
    ```

## Review Handling

- Treat human review feedback as blocking until addressed or explicitly pushed back with rationale.
- Treat Codex review feedback as actionable when it raises a correctness, validation, or scope issue.
- Treat failed required checks as blocking feedback even if no human comment exists.
- Use `[codex]` when writing GitHub comments so the watcher can distinguish acknowledgements from unresolved feedback.
- Do not over-expand PR scope. If a review asks for unrelated work, explain the deferral and suggest a follow-up.

## Watcher Semantics

The bundled watcher monitors feedback, checks, and PR head changes in parallel. It returns success only after the PR is conflict-free, checks are green, and 10 minutes pass after green checks with no outstanding feedback.

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
