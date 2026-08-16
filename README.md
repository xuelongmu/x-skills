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

- `babysit` never merges, enables auto-merge, or deletes branches — it prints the merge command when ready. `land` can publish a missing PR and is the only skill that merges.
- Codex `babysit` and `land` share `land/land_watch.py`, so on Codex always install `land` alongside `babysit`. Codex has no `/loop`; a single `babysit` run uses that watcher, and continuous monitoring uses a Codex cron automation.
- Claude Code has no bundled watcher script: both Claude `babysit` and Claude `land` poll GitHub inline through `gh` instead of `land_watch.py`. The gates are the same on both hosts — conflict-free, green checks, no outstanding feedback, converged final snapshots after the grace window, and no required Codex review unless the agent itself requested a re-review; only the polling mechanism differs.

## Setup

Clone this repo somewhere permanent, then **link** the skill directories into each tool's home directory — **junctions** on Windows (`New-Item -ItemType Junction`, no admin rights or Developer Mode needed), `ln -s` on macOS/Linux. A single `git pull` in the clone then updates every install on both platforms. The trade-off: the clone's current state is live (including a checked-out feature branch), and moving or deleting the clone breaks the installs — if you'd rather not keep a checkout, use the copy-based Codex installer at the end.

Replace `C:\path\to\x-skills` / `/path/to/x-skills` with your clone's location.

### Claude Code

**Windows** (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
foreach ($s in 'publish','babysit','land','prompt-agent-orchestrator','drive-agent-orchestrator','browser-evidence','steward-research') {
  New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\$s" -Target "C:\path\to\x-skills\.claude\skills\$s"
}
```

**macOS / Linux**:
```bash
mkdir -p ~/.claude/skills
for s in publish babysit land prompt-agent-orchestrator drive-agent-orchestrator browser-evidence steward-research; do
  ln -s "/path/to/x-skills/.claude/skills/$s" "$HOME/.claude/skills/$s"
done
```

### Codex

**Windows** (PowerShell):
```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
New-Item -ItemType Directory -Force -Path (Join-Path $codexHome "skills")
foreach ($s in 'publish','babysit','land','prompt-agent-orchestrator','drive-agent-orchestrator','browser-evidence','steward-research') {
  New-Item -ItemType Junction -Path (Join-Path $codexHome "skills\$s") -Target "C:\path\to\x-skills\.codex\skills\$s"
}
```

**macOS / Linux**:
```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for s in publish babysit land prompt-agent-orchestrator drive-agent-orchestrator browser-evidence steward-research; do
  ln -s "/path/to/x-skills/.codex/skills/$s" "${CODEX_HOME:-$HOME/.codex}/skills/$s"
done
```

Restart Codex after linking.

For a **project-local** install (skills committed to one repo so they travel with it), **copy** instead of linking — links back to your personal clone won't exist for teammates or CI checkouts. From the target repo root:

**Windows** (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path ".codex\skills"
foreach ($s in 'babysit','land') {
  Copy-Item -Recurse -Force "C:\path\to\x-skills\.codex\skills\$s" ".codex\skills\$s"
}
```

**macOS / Linux**:
```bash
mkdir -p .codex/skills
for s in babysit land; do
  cp -R "/path/to/x-skills/.codex/skills/$s" ".codex/skills/$s"
done
```

The watcher resolves from the installed `land` skill directory — project-local first, then global — and must run from the PR repository's working directory so `gh` picks up the right repo.

**No local checkout?** Ask Codex to install copies instead:

> Install the `publish`, `babysit`, `land`, `prompt-agent-orchestrator`, `drive-agent-orchestrator`, `browser-evidence`, and `steward-research`
> skills from `https://github.com/xuelongmu/x-skills`. Use the corresponding
> paths under `.codex/skills/`.

Copies don't track this repo — re-run the installer to pick up updates.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- Both babysit implementations bind feedback API calls to the hostname and repository selected by `gh pr view`, not whichever remote the checkout resolves or the CLI's default host. Codex carries the PR's GraphQL node ID and URL-derived API coordinates through its watcher; Claude derives the same coordinates and queries active threads through GraphQL. API subprocesses use `GH_HOST` so custom GitHub Enterprise ports are preserved without passing an invalid `host:port` value to `gh api --hostname`.
- The Codex sign-off ping polls the PR body's reactions endpoint (GitHub emits no webhook for reactions) and notifies once per ready-commit via a `codex-ok:<sha>` label.
- The shared Codex PR watcher polls GitHub every 30 seconds by default; set `LAND_WATCH_POLL_SECONDS` from 30 to 300 seconds when a repository needs a lower API request rate. The feedback grace window defaults to 900 seconds (15 minutes) and can be overridden for both hosts with `LAND_WATCH_FEEDBACK_GRACE_SECONDS` from 30 to 86400 seconds. Both hosts require final feedback and PR snapshots to converge unchanged, with CI revalidated between them, after that window.
- Continuous `babysit` stops immediately when its PR is merged or closed and removes its automation state. Otherwise it stops after three consecutive unchanged feedback cycles (about 30 minutes at the documented 10-minute schedule), except while a Codex sign-off notification is still pending.
- `land` merges with the repository's customary method (inferred from merge history when the user does not say), never enables auto-merge, and leaves branch deletion to the repository's auto-delete setting.
