---
name: land
description: Publish a missing PR, address CI and review feedback, and merge when the repository's gates pass. Use when asked to land or merge work. Also supports requested PR sharing to Slack without merging.
---

# Land a pull request

Carry the requested work through merge, including publication when needed.
A request only to share a PR uses [Slack sharing](references/slack.md) and ends
there. A draft request ends at publication until the user authorizes readiness
and landing. Reuse authorization already established in the conversation.

Read the relevant sections of the shared [PR workflow](references/pr-workflow.md)
for publication, base synchronization, and CI or feedback fixes. This skill owns
those operations for `publish` and `babysit` too.

## Merge gates

Use the bundled [watcher](references/watcher.md) to monitor checks, feedback, and
head changes. If an authenticated connector is available without `gh`, perform
equivalent polling and final checks through it. Missing tooling never waives a
merge gate.

Before merging, require:

- the intended remote head, with local validation still applicable;
- passing checks, no outstanding actionable feedback, and the completed
  feedback grace window;
- conflict-free, up-to-date merge state and the repository's required approvals;
- the repository's customary enabled merge method, discovered from explicit
  guidance or recent history.

The watcher returns `LAND_WATCH_VALIDATED_HEAD=<sha>`. Pass that exact SHA to
`gh pr merge --match-head-commit <sha>` with the selected `--merge`, `--rebase`,
or `--squash` method. A connector must provide equivalent expected-head
protection; otherwise use the CLI. Do not substitute a newly queried head for
the validated one. Re-enter validation when the head changes.

Approval requirements come from the repository and user, consistently across
hosts. Refresh required approval state immediately before merging. Do not enable
auto-merge as a shortcut around these gates. Delete branches only when requested
or required by repository policy; do not assume automatic deletion is enabled.

When the host provides native per-PR autofix, use it within the current
authorization instead of adding duplicate remediation loops. It supplies events
and fixes; the watcher and final merge gates remain authoritative.

Continue until merged or a concrete blocker needs user action. An externally
merged PR is successful completion; a PR closed without merge is terminal and
must be reported as unmerged. Return the PR URL, result, and material remaining
limitations without a transcript of each check.
