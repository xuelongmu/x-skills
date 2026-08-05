---
name: drive-agent-orchestrator
description: Drive the Agent Orchestrator (AO) when it is installed on this machine: preflight the daemon, register projects, spawn and supervise workers and orchestrators, and monitor sessions without duplicating AO's own supervision. Operating AO only — for authoring coordinator prompts, use prompt-agent-orchestrator.
argument-hint: "[project path, task, or session to drive]"
---

# Drive the Agent Orchestrator

You are driving AO, a daemon that runs and supervises coding-agent sessions.
Your job is operation: preflight, register, spawn, message, monitor, escalate.
Authoring the project-specific coordinator prompt (charter) is a separate task —
use the `prompt-agent-orchestrator` skill for that and treat its output as input
here.

Verified against AO v0.10.3-source. Re-verify commands if `ao --version`
reports something newer.

## Step 1: Detect and preflight

Run `ao status` and `ao doctor` before anything else.

- The canonical entry point is the Go binary. On Windows, `ao doctor` fails
  when a legacy npm/Node shim shadows the binary on PATH — resolve which `ao`
  you are invoking before diagnosing anything else.
- The desktop app owns the daemon; do not try to start or restart the daemon
  yourself.
- The daemon serves loopback HTTP on port 3001. The handshake file is
  `~/.ao/running.json`; state lives under `~/.ao/data`.

Never proceed on a failing `ao doctor`. Report the exact failure to the user
and stop.

## Step 2: Projects

```
ao project add --path <repo> [--name N --worker-agent claude-code --orchestrator-agent claude-code]
ao project ls
ao project get <id>
ao project set-config <id> ...
```

Per-project orchestration policy:

```
ao project orchestration get|set|pause|resume
```

- **Mission** is the bounded default.
- **Charter** runs periodic check-ins when exactly one orchestrator is idle.

## Step 3: Workers

Spawn:

```
ao spawn --workspace worktree --issue <ID> --prompt <task>
```

- `worktree` is the only workspace kind that supports `--branch` and PR
  observation — use it for anything that will open a PR.
- `--depends-on <session>` queues a sealed handoff: max 32 dependencies, no
  cycles, incompatible with `--claim-pr`.
- `--claim-pr <number>` adopts an existing PR instead of creating one.

Manage:

```
ao session ls|get|kill|restore|rename
ao session cleanup -y
ao send --session <id> --message <text>
```

`ao session cleanup` skips dirty worktrees; never force-delete one.

## Step 4: Orchestrators

The CLI has **no** orchestrator spawn command. Spawn via the daemon API:

```
POST http://127.0.0.1:3001/api/v1/orchestrators
{"projectId":"<id>","clean":false}
```

The response contains the orchestrator session id. List with
`ao orchestrator ls`. AO injects the generic orchestrator role itself — you
only deliver the project-specific charter as a message (see the long-message
workaround below).

## Known quirks and workarounds

- `ao send` rejects long messages (MESSAGE_TOO_LONG). Workaround: write the
  charter to a stable local file (e.g. `~/.ao/charters/<name>.md`) and send a
  short kickoff message pointing at the absolute path.
- `ao session ls` can intermittently return empty/partial under daemon load —
  treat an empty listing as unknown, not as "no sessions"; re-poll before
  acting.
- `ao session cleanup` prompts interactively; always pass `-y` in
  non-interactive shells.
- Watch for the unregistered-worker failure mode: an AO-launched agent process
  with no `--session-id` is invisible to `ao session ls` and can write into a
  registered session's worktree. If a worker reports a concurrent writer,
  inventory `claude.exe`/agent processes and reconcile before letting any PR
  proceed.

## What AO already supervises — do not duplicate it

AO's SCM observer routes CI failures, review comments, merge conflicts, and
stacked-parent head changes to the owning worker automatically. A 10-minute
heartbeat escalates stalled failing PRs (~30 min). Merges go through AO's
fail-closed squash merge pinned to the exact observed head.

Your job as driver: watch for `needs_input`/blocked states and terminal
milestones. Do **not** relay review comments, retrigger CI, or merge by hand.

## Monitoring pattern

Poll `ao session ls`, the issue tracker, and `gh pr list` on a 90–120 second
cadence. Diff normalized snapshots (strip age counters and other
always-changing fields) and report only real transitions. Escalate
`needs_input` to the user immediately.

## Boundaries

You are coordination-only. Respect the target repository's own workflow —
plan gates, human-review labels, spend guardrails. This skill drives AO; it
does not override repository policy, and it never merges outside AO's merge
path.
