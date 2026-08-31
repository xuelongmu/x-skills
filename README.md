# x-skills

Portable workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex |
|---|---|---|---|
| publish | Commit intended changes, validate, push, and open a PR ready for review (draft only on request) | `/publish` | `publish` |
| babysit | Keep the PR ready without merging: fix CI, address review comments, sync the base branch, push-notify when Codex 👍s with CI green | `/loop 10m /babysit` | `babysit` |
| land | Open a PR for intended local work when needed, then keep it healthy and merge once checks and feedback gates pass | `/land` | `land` |
| prompt-agent-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/prompt-agent-orchestrator <brief>` | `prompt-agent-orchestrator` |
| drive-agent-orchestrator | Operate Agent Orchestrator: preflight, spawn/supervise workers and orchestrators, monitor sessions | `/drive-agent-orchestrator` | `drive-agent-orchestrator` |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `/browser-evidence` | `browser-evidence` |
| steward-research | Organize research repositories for reproducibility and safe handoff | `/steward-research` | `steward-research` |
| google-developer-style | Draft, revise, or review clear, accessible developer documentation using distilled Google-style guidance | `/google-developer-style [documentation or path]` | `google-developer-style` |

- `babysit` never merges, enables auto-merge, or deletes branches — it prints the merge command when ready. `land` can publish a missing PR and is the only skill that merges.
- Codex `babysit` and `land` share `land/land_watch.py`, so on Codex always install `land` alongside `babysit`. Codex has no `/loop`; a single `babysit` run uses that watcher, and continuous monitoring uses a Codex cron automation.
- Claude Code has no bundled watcher script: both Claude `babysit` and Claude `land` poll GitHub inline through `gh` instead of `land_watch.py`. The gates are the same on both hosts — conflict-free, green checks, no outstanding feedback, converged final snapshots after the grace window, and no required Codex review unless the agent itself requested a re-review; only the polling mechanism differs.

## Setup

Use the [`npx skills`](https://github.com/vercel-labs/skills) CLI for all
installation, refresh, and removal operations. Run these commands in order for
a global installation:

```bash
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.agents/skills --skill '*' --global --agent codex claude-code --yes
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.codex/skills --skill '*' --global --agent codex --yes
npx skills add https://github.com/xuelongmu/x-skills/tree/main/.claude/skills --skill '*' --global --agent claude-code --copy --yes
```

The Claude command uses CLI copy mode so same-name Claude variants remain
independent from Codex variants in the canonical store. Do not install from the
repository root with `--all`: the CLI deduplicates discovered skills by name and
cannot select both variants. Omit `--global` for a project-local installation.
Restart each agent after installation.

To refresh a complete installation, re-run the three commands in the same
order. The CLI lock is keyed by skill name, so a single update cannot retain two
sources or copy modes for same-name host variants. If you installed only the
shared skill, this shortcut is safe:

```bash
npx skills update --global google-developer-style --yes
```

On a machine with an older manual installation, remove only this repository's
known skill names before running the install commands:

```bash
npx skills remove publish publish-slack babysit land prompt-agent-orchestrator drive-agent-orchestrator browser-evidence steward-research google-developer-style --global --agent codex claude-code --yes
```

The cleanup removes a symlink or Windows junction itself, not its external
target. It deletes a real copied install directory, so move any source checkout
stored directly inside an agent's skills directory before running it. Omit
`--global` when migrating a project-local installation.

The PR watcher resolves from the installed `land` skill directory—project-local
first, then global—and must run from the PR repository's working directory so
`gh` selects the intended repository.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- Both babysit implementations bind feedback API calls to the hostname and repository selected by `gh pr view`, not whichever remote the checkout resolves or the CLI's default host. Codex carries the PR's GraphQL node ID and URL-derived API coordinates through its watcher; Claude derives the same coordinates and queries active threads through GraphQL. API subprocesses use `GH_HOST` so custom GitHub Enterprise ports are preserved without passing an invalid `host:port` value to `gh api --hostname`.
- The Codex sign-off ping polls the PR body's reactions endpoint (GitHub emits no webhook for reactions) and notifies once per ready-commit via a `codex-ok:<sha>` label.
- The shared Codex PR watcher polls GitHub every 30 seconds by default; set `LAND_WATCH_POLL_SECONDS` from 30 to 300 seconds when a repository needs a lower API request rate. The feedback grace window defaults to 900 seconds (15 minutes) and can be overridden for both hosts with `LAND_WATCH_FEEDBACK_GRACE_SECONDS` from 30 to 86400 seconds. Both hosts require final feedback and PR snapshots to converge unchanged, with CI revalidated between them, after that window. Both `land` implementations also disable any auto-merge request they observe, so GitHub cannot merge the moment checks pass and skip that window; on Codex that is opt-in via `LAND_WATCH_DISABLE_AUTO_MERGE=1`, because `babysit` shares the watcher and must never mutate merge state.
- Continuous `babysit` stops immediately when its PR is merged or closed and removes its automation state. Otherwise it stops after three consecutive unchanged feedback cycles (about 30 minutes at the documented 10-minute schedule), except while a Codex sign-off notification is still pending.
- `land` merges with the repository's customary method (inferred from merge history when the user does not say), never enables auto-merge, and leaves branch deletion to the repository's auto-delete setting.
- `google-developer-style` lives once under `.agents/skills/`; install-time links expose the same source to Codex and Claude Code. It distills the guide's highest-impact decisions, while project-specific style and the live Google guide remain authoritative.
