# x-skills

Portable workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex | Source |
|---|---|---|---|---|
| publish | Commit intended changes, validate, push, and open a PR ready for review (draft only on request) | `/publish` | `publish` | host variants |
| publish-slack | Post the current PR to Slack as a draft message with its Vercel preview link | `/publish-slack [channel]` (default `#zerogen`) | — | Claude only |
| babysit | Keep the PR ready without merging: fix CI, address review comments, sync the base branch, push-notify when Codex 👍s with CI green | `/loop 10m /babysit` | `babysit` | host variants |
| land | Open a PR for intended local work when needed, then keep it healthy and merge once checks and feedback gates pass | — | `land` | Codex only |
| prompt-agent-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/prompt-agent-orchestrator <brief>` | `prompt-agent-orchestrator` | host variants |
| drive-agent-orchestrator | Operate Agent Orchestrator: preflight, spawn/supervise workers and orchestrators, monitor sessions | `/drive-agent-orchestrator` | `drive-agent-orchestrator` | canonical |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `/browser-evidence` | `browser-evidence` | host variants |
| steward-research | Organize research repositories for reproducibility and safe handoff | `/steward-research` | `steward-research` | canonical |
| google-developer-style | Draft, revise, or review clear, accessible developer documentation using distilled Google-style guidance | `/google-developer-style [documentation or path]` | `google-developer-style` | canonical |

- `babysit` never merges, enables auto-merge, or deletes branches — it prints the merge command when ready. Codex-only `land` can publish a missing PR and is the only skill that merges; Claude Code has no `land` implementation.
- Codex `babysit` reuses `land/land_watch.py`, so always install `land` alongside it. Codex has no `/loop`; a single run uses that watcher, and continuous monitoring uses a Codex cron automation.

## Setup

Use the [`npx skills`](https://github.com/vercel-labs/skills) CLI for all
installation, refresh, and removal operations. The repository has three source
subtrees:

- `.agents/skills` contains host-neutral sources. The CLI stores one canonical
  copy in `.agents/skills` (project) or `~/.agents/skills` (global). Codex reads
  it directly; Claude Code receives a symlink or, on Windows, a junction.
- `.codex/skills` contains Codex variants and Codex-only skills.
- `.claude/skills` contains Claude variants and Claude-only skills.

### Install

Run these commands in order for a global installation:

```bash
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.agents/skills --skill '*' --global --agent codex claude-code --yes
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.codex/skills --skill '*' --global --agent codex --yes
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.claude/skills --skill '*' --global --agent claude-code --copy --yes
```

The Claude command uses CLI copy mode so same-name Claude variants remain
independent from Codex variants in the canonical store. Omit `--global` for a
project-local installation. Restart each agent after installation.

Do not install from the repository root with `--all`. The CLI deduplicates
discovered skills by name, so a root scan cannot select both host-specific
variants of a same-name skill.

### Refresh

Re-run the three install commands in the same order. This is the supported
refresh path for a complete installation because the CLI lock is keyed by
skill name and does not retain two sources or copy modes for same-name host
variants. For an installation containing only canonical skills, this shortcut
is also safe:

```bash
npx skills update --global drive-agent-orchestrator steward-research google-developer-style --yes
```

### Remove or migrate a legacy installation

Remove only this repository's known skill names:

```bash
npx skills remove publish publish-slack babysit land prompt-agent-orchestrator drive-agent-orchestrator browser-evidence steward-research google-developer-style --global --agent codex claude-code --yes
```

This command is the cross-platform migration cleanup before reinstalling. It
removes entries only from CLI-managed agent locations. When an entry is a
symlink or Windows junction, the link is deleted and its external target stays
intact. When an entry is a real copied directory, that installed copy is
deleted. If an old source checkout itself was placed directly inside an agent
skills directory instead of being linked or copied there, move that checkout
outside the managed directory before running cleanup so it is not mistaken for
an installed copy. Then run the three install commands above.

Omit `--global` to remove a project-local installation. Omit `--agent` only
when intentionally cleaning the named skills from every agent supported by the
CLI.

The `land` watcher remains bundled with the Codex skill. Run watcher commands
from the PR repository so `gh` resolves the correct repository.

See [the skill layout audit](docs/skill-layout.md) for migration scope,
intentional exceptions, CLI constraints, and duplication counts.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- Both babysit implementations bind feedback API calls to the hostname and repository selected by `gh pr view`, not whichever remote the checkout resolves or the CLI's default host. Codex carries the PR's GraphQL node ID and URL-derived API coordinates through its watcher; Claude derives the same coordinates and queries active threads through GraphQL. API subprocesses use `GH_HOST` so custom GitHub Enterprise ports are preserved without passing an invalid `host:port` value to `gh api --hostname`.
- The Codex sign-off ping polls the PR body's reactions endpoint (GitHub emits no webhook for reactions) and notifies once per ready-commit via a `codex-ok:<sha>` label.
- The shared Codex PR watcher polls GitHub every 30 seconds by default; set `LAND_WATCH_POLL_SECONDS` from 30 to 300 seconds when a repository needs a lower API request rate. The feedback grace window defaults to 900 seconds (15 minutes) and can be overridden for both hosts with `LAND_WATCH_FEEDBACK_GRACE_SECONDS` from 30 to 86400 seconds. Both hosts require final feedback and PR snapshots to converge unchanged, with CI revalidated between them, after that window.
- Continuous `babysit` stops immediately when its PR is merged or closed and removes its automation state. Otherwise it stops after three consecutive unchanged feedback cycles (about 30 minutes at the documented 10-minute schedule), except while a Codex sign-off notification is still pending.
- `publish-slack` sends as a draft so the user reviews before posting; Vercel bot comments live on the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`.
- `drive-agent-orchestrator`, `steward-research`, and `google-developer-style` live once under `.agents/skills/`; CLI install-time links expose the same source to Codex and Claude Code. The Google style skill distills the guide's highest-impact decisions, while project-specific style and the live Google guide remain authoritative.
