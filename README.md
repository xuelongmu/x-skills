# x-skills

Portable PR workflow skills for Claude Code and Codex.

- Claude Code commands live in `x/` and are symlinked into `~/.claude/commands/`.
- Codex skills live in `.codex/skills/` and can be copied or installed as skill directories.

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/x:pr` | Create a GitHub PR with auto-generated title, summary, and test plan | none |
| `/x:slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/x:babysit` | Address review comments, fix CI, wait 10 minutes after green checks, and report merge readiness without merging | none |
| Codex `babysit` | Codex-installable PR babysitter with bundled Python watcher | none |

## Usage

```
/x:pr                     # create PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/loop 5m /x:babysit       # keep PR ready without merging
```

## Setup

### Claude Code

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

### Codex

Install or copy the `.codex/skills/babysit/` directory as a Codex skill. The skill includes `scripts/land_watch.py`, based on Symphony's merged watcher, which monitors feedback, checks, and PR head changes, then waits 10 minutes after green checks before reporting readiness.

When installing from this repo with a Codex skill installer, use the skill path:

```
.codex/skills/babysit
```

## Design decisions

- `/x:pr` and `/x:slack-pr` are separate so each can be used independently
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:babysit` waits 10 minutes after green checks for late feedback before reporting ready
- `/x:babysit` never merges, enables auto-merge, or deletes the branch; it prints the merge command when ready
- Codex `babysit` is packaged as a real skill directory because Codex installers expect `SKILL.md`
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
