# x-skills

Portable workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex |
|---|---|---|---|
| publish | Commit intended changes, validate, push, and open a PR ready for review (draft only on request) | `/publish` | `publish` |
| publish-slack | Post the current PR to Slack as a draft message with its Vercel preview link | `/publish-slack [channel]` (default `#zerogen`) | — |
| babysit | Keep the PR ready without merging: fix CI, address review comments, sync the base branch, push-notify when Codex 👍s with CI green | `/loop 10m /babysit` | `babysit` |
| land | Open a PR for intended local work when needed, then keep it healthy and merge once checks and feedback gates pass | — | `land` |
| prompt-agent-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/prompt-agent-orchestrator <brief>` | `prompt-agent-orchestrator` |
| drive-agent-orchestrator | Operate Agent Orchestrator: preflight, spawn/supervise workers and orchestrators, monitor sessions | `/drive-agent-orchestrator` | `drive-agent-orchestrator` |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `/browser-evidence` | `browser-evidence` |
| steward-research | Organize research repositories for reproducibility and safe handoff | `/steward-research` | `steward-research` |
| google-developer-style | Draft, revise, or review clear, accessible developer documentation using distilled Google-style guidance | `/google-developer-style [documentation or path]` | `google-developer-style` |

- `babysit` never merges, enables auto-merge, or deletes branches — it prints the merge command when ready. Codex-only `land` can publish a missing PR and is the only skill that merges; Claude Code has no `land` implementation.
- Codex `babysit` reuses `land/land_watch.py`, so always install `land` alongside it. Codex has no `/loop`; a single run uses that watcher, and continuous monitoring uses a Codex cron automation.

## Setup

Use the Skills CLI to discover and install skills. It maintains the canonical
copy and any agent-specific links.

```bash
npx skills add xuelongmu/x-skills -g
npx skills add xuelongmu/x-skills --skill google-developer-style -g -a codex -a claude-code -y
npx skills update -g
```

Omit `-g` for a project-local install. Use `npx skills remove -g <skill>` to
uninstall a global skill, and restart the agent after an install or update.

On machines with an older manual installation, first inspect and remove only
this repository's named entries from the agent skill directories. Remove a
symlink or Windows junction itself—not the directory it targets. If an entry is
a copied directory, verify its contents before deleting it recursively. Then
reinstall it with `npx skills add` so future updates and removal are CLI-managed.

The PR watcher resolves from the installed `land` skill directory—project-local
first, then global—and must run from the PR repository's working directory so
`gh` selects the intended repository.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- Both babysit implementations bind feedback API calls to the hostname and repository selected by `gh pr view`, not whichever remote the checkout resolves or the CLI's default host. Codex carries the PR's GraphQL node ID and URL-derived API coordinates through its watcher; Claude derives the same coordinates and queries active threads through GraphQL. API subprocesses use `GH_HOST` so custom GitHub Enterprise ports are preserved without passing an invalid `host:port` value to `gh api --hostname`.
- The Codex sign-off ping polls the PR body's reactions endpoint (GitHub emits no webhook for reactions) and notifies once per ready-commit via a `codex-ok:<sha>` label.
- The shared Codex PR watcher polls GitHub every 30 seconds by default; set `LAND_WATCH_POLL_SECONDS` from 30 to 300 seconds when a repository needs a lower API request rate. The feedback grace window defaults to 900 seconds (15 minutes) and can be overridden for both hosts with `LAND_WATCH_FEEDBACK_GRACE_SECONDS` from 30 to 86400 seconds. Both hosts require final feedback and PR snapshots to converge unchanged, with CI revalidated between them, after that window.
- Continuous `babysit` stops immediately when its PR is merged or closed and removes its automation state. Otherwise it stops after three consecutive unchanged feedback cycles (about 30 minutes at the documented 10-minute schedule), except while a Codex sign-off notification is still pending.
- `publish-slack` sends as a draft so the user reviews before posting; Vercel bot comments live on the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`.
- `google-developer-style` lives once under `.agents/skills/`; install-time links expose the same source to Codex and Claude Code. It distills the guide's highest-impact decisions, while project-specific style and the live Google guide remain authoritative.
