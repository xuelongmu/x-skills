# x-skills

Portable workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex | Source |
|---|---|---|---|---|
| publish | Commit intended changes, validate, push, and open a PR ready for review (draft only on request) | `/publish` | `publish` | canonical |
| babysit | Keep the PR ready without merging: fix CI, address review comments, and sync the base branch | `/babysit` | `babysit` | canonical |
| land | Open or share a PR, keep it healthy, and merge once checks and feedback gates pass | `/land` | `land` | canonical |
| prompt-agent-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/prompt-agent-orchestrator <brief>` | `prompt-agent-orchestrator` | canonical |
| drive-agent-orchestrator | Operate Agent Orchestrator: preflight, spawn/supervise workers and orchestrators, monitor sessions | `/drive-agent-orchestrator` | `drive-agent-orchestrator` | canonical |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `/browser-evidence` | `browser-evidence` | canonical |
| steward-research | Organize research repositories for reproducibility and safe handoff | `/steward-research` | `steward-research` | canonical |
| code-simplifier | Review or simplify an in-scope ZeroGen Platform diff without changing accepted behavior | `/code-simplifier` | `code-simplifier` | canonical |
| google-developer-style | Draft, revise, or review clear, accessible developer documentation using distilled Google-style guidance | `/google-developer-style [documentation or path]` | `google-developer-style` | canonical |

- `babysit` never merges, enables auto-merge, or deletes branches. `land` can
  publish a missing PR and is the only skill that merges.
- `babysit` reuses `land/scripts/land_watch.py`. For continuous monitoring, it
  uses the recurring monitor or loop mechanism available in the current host.
- `land` includes the former `publish-slack` workflow. Ask it to share the PR in
  Slack to create a draft with the Vercel preview; ask explicitly to send when
  a draft is not desired.

## Setup

Use the [`npx skills`](https://github.com/vercel-labs/skills) CLI for all
installation, refresh, and removal operations. The repository has one populated
source subtree:

- `.agents/skills` contains host-neutral sources. The CLI stores one canonical
  copy in `.agents/skills` (project) or `~/.agents/skills` (global). Codex reads
  it directly; Claude Code receives a symlink or, on Windows, a junction.

### Install

Run this command for a global installation:

```bash
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.agents/skills --skill '*' --global --agent codex claude-code --yes
```

Omit `--global` for a project-local installation. Restart each agent after
installation.

### Refresh

A complete refresh has two steps. The update command refreshes installed skills
and detects skills deleted upstream. It reports newly available skills but does
not install them.

1. Update the installed global skills:

   ```bash
   npx skills update --global
   ```

   When prompted, confirm removal of skills deleted upstream. Do not add
   `--yes` when you want this cleanup: non-interactive updates report deleted
   skills but leave them installed.

2. Re-run the repository installation to discover and install newly added
   skills:

   ```bash
   npx skills add https://github.com/xuelongmu/x-skills/tree/main/.agents/skills --skill '*' --global --agent codex claude-code --yes
   ```

For a project-local refresh, use `--project` instead of `--global` in the first
command and omit `--global` from the second command. Restart each agent after
the refresh.

### Remove or migrate a legacy installation

Remove only this repository's known skill names:

```bash
npx skills remove publish publish-slack babysit land prompt-agent-orchestrator drive-agent-orchestrator browser-evidence steward-research code-simplifier google-developer-style --global --agent codex claude-code --yes
```

This command is the cross-platform migration cleanup before reinstalling. It
removes entries only from CLI-managed agent locations. When an entry is a
symlink or Windows junction, the link is deleted and its external target stays
intact. When an entry is a real copied directory, that installed copy is
deleted. If an old source checkout itself was placed directly inside an agent
skills directory instead of being linked or copied there, move that checkout
outside the managed directory before running cleanup so it is not mistaken for
an installed copy. Then run the install command above. The cleanup list includes
the retired `publish-slack` name so legacy Claude installations are removed.

Omit `--global` to remove a project-local installation. Omit `--agent` only
when intentionally cleaning the named skills from every agent supported by the
CLI.

The `land` watcher is bundled at `scripts/land_watch.py`. Skills resolve bundled
resources relative to the active `SKILL.md`; run watcher commands from the PR
repository so `gh` resolves the correct repository.

See [the skill layout audit](docs/skill-layout.md) for migration scope,
intentional exceptions, CLI constraints, and duplication counts.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- `babysit` binds feedback API calls to the hostname and repository selected by
  `gh pr view`, not whichever remote the checkout resolves or the CLI's default
  host. API subprocesses use `GH_HOST` so custom GitHub Enterprise ports are
  preserved without passing an invalid `host:port` value to `gh api --hostname`.
- The shared PR watcher polls GitHub every 30 seconds by default; set
  `LAND_WATCH_POLL_SECONDS` from 30 to 300 seconds when a repository needs a
  lower API request rate. The feedback grace window defaults to 900 seconds
  (15 minutes) and can be overridden with
  `LAND_WATCH_FEEDBACK_GRACE_SECONDS` from 30 to 86400 seconds.
- Continuous `babysit` stops immediately when its PR is merged or closed and
  removes its monitor state. Otherwise, it stops after three consecutive
  unchanged feedback cycles. On Claude surfaces with the sign-off notification
  adapter, Codex activity plus a missing `codex-ok:<head-sha>` sentinel keeps
  the monitor running until the pending sign-off/green-CI notification fires or
  the PR reaches a terminal state.
- `land` uses a host's native per-PR autofix control when available. On Claude
  surfaces, **Auto-fix CI & address comments** can provide wake-ups and fixes,
  but the shared watcher and final synchronous refresh remain the merge gates;
  **Auto-merge when ready** stays disabled.
- `land` can share a PR through any authenticated Slack capability. It creates
  a draft by default and reads Vercel bot comments from the **issues** endpoint
  (`/issues/{n}/comments`), not `/pulls/{n}/comments`.
- `code-simplifier` reads relevant Codex task history when the active host
  exposes task tools. Other hosts use history from the conversation or an
  export, without a separate skill implementation.
- All cross-host capabilities live once under `.agents/skills/`; CLI
  install-time links expose the same complete skill directory—including
  scripts, references, and OpenAI metadata—to Codex and Claude Code. The Google
  style skill distills the guide's highest-impact decisions, while
  project-specific style and the live Google guide remain authoritative.
