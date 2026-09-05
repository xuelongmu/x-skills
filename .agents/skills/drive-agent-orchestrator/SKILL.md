---
name: drive-agent-orchestrator
description: Operate an installed Agent Orchestrator daemon, projects, workers, and coordinators without duplicating AO supervision.
---

# Drive Agent Orchestrator

Drive AO as the external operator: preflight, register, spawn, message, monitor,
and escalate. Use a supplied project charter as input. When prompt authoring is
also requested, `prompt-agent-orchestrator` can help if available.

Verified against AO v0.10.3 source through revision `08791937`. Treat
`ao --help` and the live daemon API as authoritative when the installed build
differs.

## Step 1: Detect and preflight

Establish the installed version and daemon health with `ao version --json`,
`ao status`, and `ao doctor`; reuse current preflight evidence within the session.

- Resolve which `ao` is running before diagnosing failures. On Windows, a
  legacy npm/Node shim can shadow the canonical Go binary and fail `ao doctor`.
- If `ao status` reports stopped or stale, start AO with `ao start`. A desktop
  install opens the app and exits; a source checkout runs the blocking dev
  harness, so launch it as a detached background process.
- Read the live loopback port from `ao status` or `~/.ao/running.json` before
  calling the API. The default is 3001 and state lives under `~/.ao/data`.

Resolve preflight failures that prevent the requested operation. Report a
remaining blocker without abandoning independent inspection or preparation.

## Step 2: Projects

```text
ao project add --path <repo> [--name N --worker-agent <harness> --orchestrator-agent <harness>]
ao project ls
ao project get <id>
ao project set-config <id> ...
```

After the daemon is running, use `ao agent ls` to confirm that each selected
harness is installed and authenticated. AO supports `claude-code`, `codex`, and
the other harnesses reported by `ao spawn --help`; choose worker and
orchestrator harnesses from the task's requirements rather than from the host
driving AO.

Manage per-project orchestration policy with:

```text
ao project orchestration get|set|pause|resume
```

- Use Mission as the bounded default.
- Use Charter for periodic check-ins when exactly one orchestrator is idle.

## Step 3: Workers

Spawn with:

```text
ao spawn --project <id> --workspace worktree --issue <ID> --prompt <task>
```

Pass `--project` explicitly. It resolves implicitly only from `AO_PROJECT_ID` or
when the current directory is a registered repository.

- Use `worktree` for work that will open a PR; it is the only workspace kind
  supporting `--branch` and PR observation.
- Use `--depends-on <session>` for a sealed handoff. It accepts at most 32
  acyclic dependencies and is incompatible with `--claim-pr`.
- Use `--claim-pr <number>` to adopt an existing PR.

Manage sessions with:

```text
ao session ls|get|kill|restore|rename
ao session cleanup -y
ao send --session <id> --message <text>
```

`ao session cleanup` skips dirty worktrees. Never force-delete one.

## Step 4: Orchestrators

The CLI has no orchestrator spawn command. Spawn through the daemon API:

```text
POST http://127.0.0.1:<port>/api/v1/orchestrators
{"projectId":"<id>","clean":false}
```

Use the live port reported during preflight. The response contains the
orchestrator session id; list it with `ao orchestrator ls`. AO injects the
generic orchestrator role, so deliver only the project-specific charter.

## Known quirks and workarounds

- `ao send` rejects messages above the daemon limit with `MESSAGE_TOO_LONG`.
  Write a long charter to a stable local file such as
  `~/.ao/charters/<name>.md`, then send a short kickoff pointing to its absolute
  path.
- Treat an empty or partial `ao session ls` result under daemon load as unknown;
  re-poll before acting.
- Pass `-y` to `ao session cleanup` in non-interactive shells.
- Builds before source revision `08791937` can leave an AO-launched agent
  process without a committed session registration. If a worker reports a
  concurrent writer on an older or unknown build, inventory AO-owned agent
  processes across the configured harnesses and reconcile them before letting
  any PR proceed. Newer builds reap these unregistered runtimes during daemon
  reconciliation; still investigate an observed concurrent writer rather than
  assuming it is safe.

## Avoid duplicate supervision

AO's SCM observer routes CI failures, review comments, merge conflicts, and
stacked-parent head changes to the owning worker. Its 10-minute heartbeat
escalates stalled failing PRs after roughly 30 minutes. A session paused in
`waiting_input` or `needs_input` may not receive these nudges; inspect its PR and
route or escalate fresh failures, feedback, and conflicts.

Watch for blocked states and terminal milestones. Do not relay feedback,
retrigger CI, or merge by hand when AO already owns that action. AO merges
through its fail-closed squash path pinned to the observed head. If a ready PR
remains unmerged past AO's escalation window, report a suspect merge path
instead of bypassing it.

## Monitor

Use the host's recurring monitor or wait mechanism when available. Otherwise,
poll `ao session ls -a` (plain `ls` hides orchestrator sessions), the issue
tracker, and `gh pr list -R <owner>/<repo>` on a 90–120 second cadence. Scope
GitHub explicitly because bare `gh pr list` uses the current repository. Diff
normalized snapshots, omit always-changing age counters, report only real
transitions, and escalate `needs_input` immediately.

## Boundaries

Stay coordination-only. Respect the target repository's plan gates, human
review rules, spend guardrails, and destructive-operation policy. Never use this
skill to override repository policy or merge outside AO's merge path.
