# x-skills

Portable PR workflow skills for Claude Code and Codex.

- Claude Code commands live in `x/` and are symlinked into `~/.claude/commands/`.
- Codex skills live in `.codex/skills/` and can be copied or installed as skill directories.

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/x:publish` | Commit intended changes, validate, push, and open a PR ready for review | none |
| `/x:slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/x:babysit` | Address review comments, fix CI, wait 10 minutes after green checks, and report merge readiness without merging | none |
| `/x:codex-watch` | Push-notify when Codex 👍s the PR body and CI is green — you merge it yourself | none |
| `/x:author-ao-orchestrator` | Draft and validate multi-issue Agent Orchestrator project prompts | project brief, issue range, or draft prompt |
| Codex `babysit` | Codex-installable PR babysitter that reuses the `land` watcher | none |
| Codex `land` | Codex-installable PR lander with the shared watcher, CI handling, and the repository's customary merge flow | none |
| Codex `publish` | Commit, validate, push, and open a ready-for-review PR | none |
| Codex `author-ao-orchestrator` | Draft and validate multi-issue Agent Orchestrator project prompts | project brief or draft prompt |

## Usage

### Claude Code

```
/x:publish                # commit, push, and open a ready PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/x:author-ao-orchestrator <project brief, issues, or draft>
/loop 5m /x:babysit       # keep PR ready without merging (Claude Code only)
/loop 5m /x:codex-watch   # ping me when Codex approves; I'll merge myself
```

### Codex

Use `publish` to commit, push, and open a PR ready for review. Use `babysit` for a single merge-readiness pass without merging, or ask Codex to keep babysitting when you want continuous monitoring. Use `land` when you want Codex to keep the PR healthy and merge it once checks and feedback gates pass. Codex does not support Claude Code `/loop` semantics; a single babysit run uses the shared watcher for checks, feedback, PR head changes, and the 10-minute post-green wait. For continuous babysitting across turns, ask Codex to create or update a cron automation for the PR.

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

Recommended: ask Codex to install the skills you need from this repo:

> Install the `publish`, `babysit`, `land`, and `author-ao-orchestrator` skills from `https://github.com/xuelongmu/x-skills`. Use the corresponding paths under `.codex/skills/`.

Codex's skill installer copies GitHub skill directories into `${CODEX_HOME:-$HOME/.codex}/skills`, so this does not require a persistent local checkout or symlinks. When installing `babysit`, install `land` with it because `babysit` reuses `land/land_watch.py`; `author-ao-orchestrator` is independent.

When installing from this repo with a Codex skill installer, use these skill paths:

```
.codex/skills/babysit
.codex/skills/land
.codex/skills/publish
.codex/skills/author-ao-orchestrator
```

Install modes:

- Recommended global install: copy into `${CODEX_HOME:-$HOME/.codex}/skills/` via Codex's skill installer so the skills are available in any repo.
- Optional project-local install: copy into `<repo>/.codex/skills/` when the skills should travel with one repo.
- Development only: symlink from this repo into home or project `.codex/skills` while editing the skills.

The watcher script path should resolve from the installed `land` skill directory. Prefer project-local `<repo>/.codex/skills/land` when present; otherwise use the home/global `land` skill. Run the watcher command from the target PR repository working directory. `gh` resolves `{owner}`, `{repo}`, PRs, and checks from that cwd.

For project-local copy installs, copy both skill directories from this repo into the target repo:

**Windows** (PowerShell from the target repo root):
```powershell
New-Item -ItemType Directory -Force -Path ".codex\skills"
Copy-Item -Recurse -Force "C:\path\to\x-skills\.codex\skills\babysit" ".codex\skills\babysit"
Copy-Item -Recurse -Force "C:\path\to\x-skills\.codex\skills\land" ".codex\skills\land"
```

**macOS / Linux** (from the target repo root):
```bash
mkdir -p .codex/skills
cp -R /path/to/x-skills/.codex/skills/babysit .codex/skills/babysit
cp -R /path/to/x-skills/.codex/skills/land .codex/skills/land
```

For local skill development, symlink the skill directories instead of copying them.

Home/global symlinks:

**Windows** (admin PowerShell):
```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
New-Item -ItemType Directory -Force -Path (Join-Path $codexHome "skills")
New-Item -ItemType SymbolicLink -Path (Join-Path $codexHome "skills\babysit") -Target "C:\path\to\x-skills\.codex\skills\babysit"
New-Item -ItemType SymbolicLink -Path (Join-Path $codexHome "skills\land") -Target "C:\path\to\x-skills\.codex\skills\land"
```

**macOS / Linux**:
```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s /path/to/x-skills/.codex/skills/babysit "${CODEX_HOME:-$HOME/.codex}/skills/babysit"
ln -s /path/to/x-skills/.codex/skills/land "${CODEX_HOME:-$HOME/.codex}/skills/land"
```

Project-local symlinks from the target repo root:

**Windows** (admin PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path ".codex\skills"
New-Item -ItemType SymbolicLink -Path ".codex\skills\babysit" -Target "C:\path\to\x-skills\.codex\skills\babysit"
New-Item -ItemType SymbolicLink -Path ".codex\skills\land" -Target "C:\path\to\x-skills\.codex\skills\land"
```

**macOS / Linux**:
```bash
mkdir -p .codex/skills
ln -s /path/to/x-skills/.codex/skills/babysit .codex/skills/babysit
ln -s /path/to/x-skills/.codex/skills/land .codex/skills/land
```

Restart Codex after installing or linking the skill.

## Design decisions

- `/x:publish` and `/x:slack-pr` are separate so each can be used independently
- `/x:publish` performs the full commit-to-PR flow and opens ready for review unless a draft is explicitly requested
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:babysit` waits 10 minutes after green checks for late feedback before reporting ready
- `/x:babysit` never merges, enables auto-merge, or deletes the branch; it prints the merge command when ready
- `/x:author-ao-orchestrator` is authoring-only and does not mutate live project state unless separately requested
- Codex `babysit` is packaged as a real skill directory because Codex installers expect `SKILL.md`
- Codex `babysit` does not rely on `/loop`; it reuses the `land` Python watcher for the monitoring wait, and uses Codex cron automation when the user asks for continuous monitoring
- Codex `babysit` should leave `[codex]` GitHub replies after addressing or explicitly deferring feedback, but should not resolve review threads unless asked
- Codex `land` owns the shared watcher and uses the codebase's customary merge method after the same feedback/check gates pass
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
- `/x:codex-watch` keys off the 👍 **reaction** on the PR body (the issues reactions endpoint), since GitHub emits no webhook for reactions — so it polls on a loop
- `/x:codex-watch` notifies once per ready-commit via a `codex-ok:<sha>` label and never merges, leaving the merge to the human
