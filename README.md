# x-skills

Portable PR workflow skills for Claude Code and Codex.

- Claude Code commands live in `x/` and are linked into `~/.claude/commands/`.
- Claude Code skills live in `.claude/skills/` and are linked into `~/.claude/skills/`.
- Codex skills live in `.codex/skills/` and are linked into `${CODEX_HOME:-$HOME/.codex}/skills/` (or copied via Codex's skill installer if you don't keep a local checkout).

## Skills

| Skill | Purpose | Args |
|---|---|---|
| `/x:publish` | Commit intended changes, validate, push, and open a PR ready for review | none |
| `/x:slack-pr` | Post existing PR to Slack with Vercel preview link | `[channel]` (default: `#zerogen`) |
| `/x:babysit` | Address review comments, fix CI, wait 10 minutes after green checks, push-notify when Codex 👍s the PR body with CI green, and report merge readiness without merging | none |
| `/x:author-ao-orchestrator` | Draft and validate multi-issue Agent Orchestrator project prompts | project brief, issue range, or draft prompt |
| Claude `browser-evidence` | Verify browser flows and capture trustworthy UI evidence | flow or claim to verify |
| Codex `babysit` | Codex-installable PR babysitter that reuses the `land` watcher | none |
| Codex `land` | Codex-installable PR lander with the shared watcher, CI handling, and the repository's customary merge flow | none |
| Codex `publish` | Commit, validate, push, and open a ready-for-review PR | none |
| Codex `author-ao-orchestrator` | Draft and validate multi-issue Agent Orchestrator project prompts | project brief or draft prompt |
| Codex `browser-evidence` | Verify browser flows and capture trustworthy UI evidence | flow or claim to verify |

## Usage

### Claude Code

```
/x:publish                # commit, push, and open a ready PR
/x:slack-pr               # share to #zerogen with Vercel preview
/x:slack-pr frontend      # share to #frontend instead
/x:author-ao-orchestrator <project brief, issues, or draft>
/loop 5m /x:babysit       # keep PR ready without merging; pings when Codex approves (Claude Code only)
```

Use the `browser-evidence` skill when you want Claude Code to drive a running
app, verify a flow, and capture screenshots or other browser-visible evidence.

### Codex

Use `publish` to commit, push, and open a PR ready for review. Use `babysit` for a single merge-readiness pass without merging, or ask Codex to keep babysitting when you want continuous monitoring. Use `land` when you want Codex to keep the PR healthy and merge it once checks and feedback gates pass. Codex does not support Claude Code `/loop` semantics; a single babysit run uses the shared watcher for checks, feedback, PR head changes, and the 10-minute post-green wait. For continuous babysitting across turns, ask Codex to create or update a cron automation for the PR.

## Setup

Both platforms install the same way: clone this repo somewhere permanent, then **link** the skill directories into the tool's home directory. Because the installs are links, a single `git pull` in the clone updates every installed skill on both platforms at once — no re-copying.

- **Windows**: use **junctions** (`New-Item -ItemType Junction`). They behave like directory symlinks but require no admin rights or Developer Mode.
- **macOS / Linux**: use `ln -s`.

The trade-off: whatever state the clone is in becomes live immediately (including a checked-out feature branch), and moving or deleting the clone breaks the installs. If you don't want to keep a local checkout, use the copy-based Codex installer described at the end instead.

Replace `C:\path\to\x-skills` / `/path/to/x-skills` with your clone's location in the commands below.

### Claude Code

**Windows** (PowerShell):
```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\commands\x" -Target "C:\path\to\x-skills\x"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\browser-evidence" -Target "C:\path\to\x-skills\.claude\skills\browser-evidence"
```

**macOS / Linux**:
```bash
ln -s /path/to/x-skills/x ~/.claude/commands/x
mkdir -p ~/.claude/skills
ln -s /path/to/x-skills/.claude/skills/browser-evidence ~/.claude/skills/browser-evidence
```

After linking, the `/x:*` commands and the `browser-evidence` skill are available in any Claude Code session.

### Codex

Link every skill directory into the global Codex skills directory. Always install `land` alongside `babysit` because `babysit` reuses `land/land_watch.py`.

**Windows** (PowerShell):
```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
New-Item -ItemType Directory -Force -Path (Join-Path $codexHome "skills")
foreach ($s in 'publish','babysit','land','author-ao-orchestrator','browser-evidence') {
  New-Item -ItemType Junction -Path (Join-Path $codexHome "skills\$s") -Target "C:\path\to\x-skills\.codex\skills\$s"
}
```

**macOS / Linux**:
```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for s in publish babysit land author-ao-orchestrator browser-evidence; do
  ln -s "/path/to/x-skills/.codex/skills/$s" "${CODEX_HOME:-$HOME/.codex}/skills/$s"
done
```

Restart Codex after linking.

For a **project-local** install (skills that travel with one repo), run the same commands from the target repo root with `.codex\skills\<name>` / `.codex/skills/<name>` as the link path. The watcher script resolves from the installed `land` skill directory — project-local `<repo>/.codex/skills/land` is preferred when present, otherwise the global one. Run watcher commands from the PR repository's working directory; `gh` resolves `{owner}`, `{repo}`, PRs, and checks from that cwd.

**No local checkout?** Ask Codex to install copies instead:

> Install the `publish`, `babysit`, `land`, `author-ao-orchestrator`, and `browser-evidence`
> skills from `https://github.com/xuelongmu/x-skills`. Use the corresponding
> paths under `.codex/skills/`.

Codex's skill installer copies the GitHub skill directories into `${CODEX_HOME:-$HOME/.codex}/skills`. Copies don't track this repo — re-run the installer to pick up updates.

## Design decisions

- `/x:publish` and `/x:slack-pr` are separate so each can be used independently
- `/x:publish` performs the full commit-to-PR flow and opens ready for review unless a draft is explicitly requested
- `/x:babysit` uses `git merge` (not rebase) to avoid force pushes
- `/x:babysit` replies to review comments after addressing them
- `/x:babysit` waits 10 minutes after green checks for late feedback before reporting ready
- `/x:babysit` never merges, enables auto-merge, or deletes the branch; it prints the merge command when ready
- `/x:babysit` push-notifies once per ready-commit when Codex 👍s the PR body and CI is green, using a `codex-ok:<sha>` label as the notify-once sentinel; it polls the issues reactions endpoint because GitHub emits no webhook for reactions
- `/x:author-ao-orchestrator` is authoring-only and does not mutate live project state unless separately requested
- Codex `babysit` is packaged as a real skill directory because Codex installers expect `SKILL.md`
- Codex `babysit` does not rely on `/loop`; it reuses the `land` Python watcher for the monitoring wait, and uses Codex cron automation when the user asks for continuous monitoring
- Codex `babysit` should leave `[codex]` GitHub replies after addressing or explicitly deferring feedback, but should not resolve review threads unless asked
- Codex `land` owns the shared watcher and uses the codebase's customary merge method after the same feedback/check gates pass
- `/x:slack-pr` sends as a draft so user can review before posting
- Vercel bot comments use the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`
