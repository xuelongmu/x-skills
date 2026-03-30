# x-skills

Portable Claude Code custom skills. Symlinked into `~/.claude/commands/`.

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/x:pr` | Create a GitHub PR with auto-generated title, summary, and test plan | none |
| `/x:slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/x:babysit` | Auto-rebase, address review comments, fix CI — shepherd PR to merge | none |

## Usage

```
/x:pr                     # create PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/loop 5m /x:babysit       # shepherd PR to merge on autopilot
```

## Setup

Symlink the `x/` subfolder into Claude Code commands (admin PowerShell):

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\x" -Target "D:\x-skills\x"
```

## Design decisions

- `/x:pr` and `/x:slack-pr` are separate so each can be used independently
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
