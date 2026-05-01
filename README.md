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
| Codex `babysit` | Codex-installable PR babysitter that reuses the `land` watcher | none |
| Codex `land` | Codex-installable PR lander with the shared watcher, CI handling, and squash-merge flow | none |

## Usage

### Claude Code

```
/x:pr                     # create PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/loop 5m /x:babysit       # keep PR ready without merging (Claude Code only)
```

### Codex

Use the `babysit` skill directly when you want Codex to keep the current PR ready without merging. Use the `land` skill when you want Codex to keep the PR healthy and merge it once checks and feedback gates pass. Codex does not support Claude Code `/loop` semantics; the shared watcher blocks while it monitors checks, feedback, PR head changes, and the 10-minute post-green wait.

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

Recommended: ask Codex to install the `babysit` and `land` skills from this repo:

> Install the `babysit` and `land` skills from `https://github.com/xuelongmu/x-skills`. Use skill paths `.codex/skills/land` and `.codex/skills/babysit`.

Codex's skill installer copies GitHub skill directories into `${CODEX_HOME:-$HOME/.codex}/skills`, so this does not require a persistent local checkout or symlinks. Install both skills together because `babysit` reuses `land/land_watch.py`.

When installing from this repo with a Codex skill installer, use these skill paths:

```
.codex/skills/babysit
.codex/skills/land
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

- `/x:pr` and `/x:slack-pr` are separate so each can be used independently
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:babysit` waits 10 minutes after green checks for late feedback before reporting ready
- `/x:babysit` never merges, enables auto-merge, or deletes the branch; it prints the merge command when ready
- Codex `babysit` is packaged as a real skill directory because Codex installers expect `SKILL.md`
- Codex `babysit` does not rely on `/loop`; it reuses the `land` Python watcher for the monitoring wait
- Codex `land` owns the shared watcher and does merge after the same feedback/check gates pass
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
