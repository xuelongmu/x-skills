---
name: babysit
description: Keep an existing PR healthy by addressing CI, review feedback, and base conflicts. Use for a maintenance pass or ongoing monitoring without merging.
---

# Keep a PR healthy

Address actionable feedback, fix attributable CI failures, and synchronize the
base as needed. Never merge, enable auto-merge, or delete branches. Return the
PR URL, readiness, and any remaining blocker; a suggested merge command must use
the repository's chosen method.

Use the maintenance section of the shared
[PR workflow](../land/references/pr-workflow.md) and the
[watcher contract](../land/references/watcher.md). Both belong to the sibling
`land` skill, including `scripts/land_watch.py`. Install `land` alongside
`babysit` in the same scope; dependencies are not installed automatically.
Resolve resources relative to the active skill directory. If the sibling is
missing, use equivalent host capabilities where available; otherwise report
the missing dependency without claiming readiness.

## Ongoing monitoring

A one-pass request ends after handling the current work and assessing readiness.
For continuous monitoring, use the host's recurring facility, updating an
existing matching monitor instead of creating a duplicate. Bind it to the PR
URL and repository checkout, and preserve the user's duration and notification
preferences. Use one remediation owner if native autofix already handles events.

Keep watching through quiet cycles. Stop on merge, closure, cancellation, or the
user's requested deadline or completion condition. Notify on meaningful changes,
completion, failure, or required user action; stay quiet on unchanged status.
Deduplicate readiness notifications by PR head using monitor state. A bot
reaction alone is not proof that the current head passed review.

Prefer the recurring facility's own state. If local state is necessary, use a
PR-specific file under the path resolved by `git rev-parse --git-path`, which
also works in linked worktrees. Remove only the matching monitor and its owned
state on termination. Treat a closed, unmerged PR as terminal rather than ready.
