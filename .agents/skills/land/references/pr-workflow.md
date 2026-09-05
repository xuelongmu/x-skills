# Shared PR operations

Read publication for a missing PR or a requested update; read maintenance when
checks, feedback, or base state require work. The entrypoint decides whether to
stop at publication, maintain readiness, or merge.

## Identity and scope

Establish the intended files and branch range from the request, repository
instructions, status, diffs, and intended untracked file contents. Exclude
unrelated work when its ownership is clear; ask only about unresolved scope.

Select the push remote, GitHub hostname, head repository and branch, and target
base repository and branch. Preserve an explicit base; otherwise discover the
repository default. Fork head and base repositories may differ. Carry the
selected PR URL and coordinates through every subsequent operation, including
failed-run lookup. Never assume `origin`, `main`, or `github.com`.

Use local Git for checkout operations. Prefer an authenticated GitHub connector
when it can explicitly target those coordinates; otherwise use `gh`. Check
authentication only for the selected host. For API calls, set `GH_HOST` to the
selected hostname, including a custom port, rather than allowing an ambient
default. For CLI PR operations, supply the selected PR and repository.

## Publication

Create a focused branch if detached or on the target base. Otherwise retain the
current branch unless the request requires a different one. Refresh the target
base ref, and inspect both `git log <base-ref>..HEAD` and
`git diff <base-ref>...HEAD` so existing commits are included in the scope review.

Find an existing PR for the selected head before creating one. Update it when
the request authorizes that change; do not create a duplicate or alter an
unrelated PR. Preserve its readiness state unless a change is requested.

Stage only intended changes and validate the state that will ship. Reuse relevant
passing evidence if that state has not changed. When unrelated unstaged changes
affect validation, materialize the index in an isolated temporary worktree;
do not stash the user's work or claim tests of a mixed tree cover the commit.
Fix attributable failures within scope and rerun affected checks. Commit the
validated changes, or reuse unpublished commits when the index is empty.

Push to the verified remote and head branch with upstream tracking. Never
discard collaborator commits. A history rewrite needs authorization for that
branch; when authorized, use `--force-with-lease`, never plain `--force`.

Prepare a title and body explaining the complete change, why it matters, and
validation or material limitations. Recheck for an open PR after pushing. For a
new PR, explicitly select base/head repositories and branches and create it
ready for review unless a draft was requested. Use a structured connector body
or a temporary UTF-8 file with `--body-file` to preserve Markdown newlines.

CLI creation: use `gh pr create --repo <host/owner/repo> --base <base>
--head <branch> --title <title> --body-file <file>`. For a user-owned fork,
`--head <owner>:<branch>` works. The organization-owned fork form is unsupported
by that CLI option: use a connector or REST creation with explicit base/head
coordinates and `head_repo` when required for same-organization forks. In a
POSIX shell, route REST calls with `GH_HOST="<host>" gh api ...`; in PowerShell,
set the process environment equivalently.

## Maintenance

Follow repository guidance for base synchronization. Do not infer a branch-sync
policy from enabled PR merge methods. If no preference exists, merge the verified
base ref to preserve shared history; rebase when requested or established policy
authorizes rewriting this branch. Validate the resulting change before pushing.

Read failing-check logs from the repository that owns the check run. Confirm the
cause before changing code or regenerating a lockfile. Rerun a plausibly transient
failure within a bounded retry window; persistent failures are blockers, not
permission to merge. When CI or native autofix changes the head, fetch and inspect
it, validate affected behavior, and restart the watcher. If the update did not
trigger checks, use the repository's authorized CI trigger instead of adding a
meaningless commit.

Treat review feedback as evidence to assess against intent and current code.
Fix applicable issues; explain unsupported or out-of-scope requests. Escalate a
material product decision while continuing independent authorized work.

When GitHub replies are authorized, batch a concise acknowledgement after fixes
with the commit and evidence, or a reason for deferral. Use `[agent]` so the
watcher recognizes it; legacy `[codex]` remains accepted. Reply inline to inline
comments and in the issue discussion for top-level comments. Resolve threads
according to repository policy and the user's authorization. If required replies
or resolution are not authorized, report the remaining gate rather than implying
completion. A reply records disposition; it does not make an unfixed issue safe.

Inline comments use `/repos/{owner}/{repo}/pulls/{number}/comments`; top-level
discussion uses `/issues/{number}/comments`. An inline reply needs the numeric
comment ID in `in_reply_to`, not its GraphQL node ID. Read feedback across inline
threads, review summaries, top-level discussion, and bots. Request another review
only when required or useful for a changed head; follow its completion policy.
