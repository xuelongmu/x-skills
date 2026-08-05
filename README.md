# x-skills

Portable PR workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex |
|---|---|---|---|
| publish | Commit intended changes, validate, push, and open a PR ready for review (draft only on request) | `/x:publish` | `publish` |
| slack-pr | Post the current PR to Slack as a draft message with its Vercel preview link | `/x:slack-pr [channel]` (default `#zerogen`) | — |
| babysit | Keep the PR ready without merging: fix CI, address review comments, sync the base branch, push-notify when Codex 👍s with CI green | `/loop 5m /x:babysit` | `babysit` |
| land | Keep the PR healthy and merge it once checks and feedback gates pass | — | `land` |
| author-ao-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/x:author-ao-orchestrator <brief>` | `author-ao-orchestrator` |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `browser-evidence` | `browser-evidence` |

- `babysit` never merges, enables auto-merge, or deletes branches — it prints the merge command when ready. `land` is the only skill that merges.
- Codex `babysit` reuses `land/land_watch.py`, so always install `land` alongside it. Codex has no `/loop`; a single run uses that watcher, and continuous monitoring uses a Codex cron automation.

## Setup

Clone this repo somewhere permanent, then **link** the skill directories into each tool's home directory — **junctions** on Windows (`New-Item -ItemType Junction`, no admin rights or Developer Mode needed), `ln -s` on macOS/Linux. A single `git pull` in the clone then updates every install on both platforms. The trade-off: the clone's current state is live (including a checked-out feature branch), and moving or deleting the clone breaks the installs — if you'd rather not keep a checkout, use the copy-based Codex installer at the end.

Replace `C:\path\to\x-skills` / `/path/to/x-skills` with your clone's location.

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

### Codex

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

> Install the `publish`, `babysit`, `land`, `author-ao-orchestrator`, and `browser-evidence`
> skills from `https://github.com/xuelongmu/x-skills`. Use the corresponding
> paths under `.codex/skills/`.

Copies don't track this repo — re-run the installer to pick up updates.

## Design notes

Each skill file documents its own behavior; these are the cross-cutting choices:

- `babysit` uses `git merge` (not rebase) to avoid force pushes, and replies on review threads after addressing feedback.
- The Codex sign-off ping polls the PR body's reactions endpoint (GitHub emits no webhook for reactions) and notifies once per ready-commit via a `codex-ok:<sha>` label.
- `slack-pr` sends as a draft so the user reviews before posting; Vercel bot comments live on the **issues** endpoint (`/issues/{n}/comments`), not `/pulls/{n}/comments`.
