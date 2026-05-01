# x-skills

Portable Claude Code custom skills. Symlinked into `~/.claude/commands/`.

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/x:pr` | Create a GitHub PR with auto-generated title, summary, and test plan | none |
| `/x:slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/x:babysit` | Address review comments, fix CI, wait 10 minutes after green checks, and report merge readiness without merging | none |

## Usage

```
/x:pr                     # create PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/loop 5m /x:babysit       # keep PR ready without merging
```

## Setup

Clone this repo, then symlink the `x/` subfolder into your Claude Code commands directory:

**Windows** (admin PowerShell):
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\commands\x" -Target "C:\path\to\x-skills\x"
```

**macOS / Linux**:
```bash
ln -s /path/to/x-skills/x ~/.claude/commands/x
```

After linking, the `/x:*` commands are available in any Claude Code session.

## Design decisions

- `/x:pr` and `/x:slack-pr` are separate so each can be used independently
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:babysit` waits 10 minutes after green checks for late feedback before reporting ready
- `/x:babysit` never merges, enables auto-merge, or deletes the branch; it prints the merge command when ready
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
