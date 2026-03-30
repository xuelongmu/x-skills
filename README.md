# xm-skills

Portable Claude Code custom skills. Symlinked into `~/.claude/commands/`.

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/pr` | Create a GitHub PR with auto-generated title, summary, and test plan | none |
| `/slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/babysit` | Auto-rebase, address review comments, fix CI — shepherd PR to merge | none |

## Usage

```
/pr                     # create PR
/slack-pr               # share to #zerogen with Vercel preview
/slack-pr frontend      # share to #frontend instead
/loop 5m /babysit       # shepherd PR to merge on autopilot
```

## Setup

Symlink this repo into Claude Code commands:

```powershell
# Remove existing commands (if any)
Remove-Item "$env:USERPROFILE\.claude\commands\babysit.md" -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.claude\commands\pr.md" -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.claude\commands\slack-pr.md" -ErrorAction SilentlyContinue

# Symlink each skill
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\babysit.md" -Target "D:\xm-skills\babysit.md"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\pr.md" -Target "D:\xm-skills\pr.md"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\slack-pr.md" -Target "D:\xm-skills\slack-pr.md"
```

## Design decisions

- `/pr` and `/slack-pr` are separate so each can be used independently
- `/babysit` uses `git merge` (not rebase) to avoid force pushes
- `/babysit` replies to review comments after addressing them
- `/slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
