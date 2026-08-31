# Skill source layout

This repository uses one canonical source for host-neutral skills and keeps
real host variants separate.

## Storage contract

- `.agents/skills/<skill>` is the canonical source for instructions that work
  unchanged in Codex and Claude Code. Codex discovers this directory directly.
- `.codex/skills/<skill>` contains Codex-specific instructions or Codex-only
  skills.
- `.claude/skills/<skill>` contains Claude-specific instructions or Claude-only
  skills.
- A canonical directory can contain metadata for both hosts. For example,
  `agents/openai.yaml` is ignored by Claude, and Claude's `argument-hint`
  frontmatter is ignored by Codex. Metadata alone does not require duplicate
  instruction sources.
- Checked-in links are not part of the source layout. Installers create links
  from hosts that do not read `.agents/skills` natively. On Windows, the
  `skills` CLI uses directory junctions; on macOS and Linux, it uses symlinks.

This matches `vercel-labs/skills` 1.5.23 at revision
[`435076e`](https://github.com/vercel-labs/skills/tree/435076e78988e1e6ec40d00b0b1d76bdbbc5419a):
[`installer.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/installer.ts)
uses `.agents/skills` and `~/.agents/skills` as the canonical project and
global locations and creates Windows junctions with absolute targets;
[`agents.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/agents.ts)
classifies Codex as universal and Claude Code as `.claude/skills`; and
[`skills.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/skills.ts)
deduplicates discovered sources by frontmatter name.

## Duplication audit

| Skill | Decision | Reason |
|---|---|---|
| `drive-agent-orchestrator` | canonical | Instructions were identical. The Claude-only `argument-hint` and Codex `agents/openai.yaml` can coexist in one source. |
| `steward-research` | canonical | The two `SKILL.md` files were byte-identical; only Codex supplied optional UI metadata. |
| `google-developer-style` | canonical | Introduced as a shared source in PR #23. |
| `publish` | keep variants | Claude specifies its allowed tools and shell-first procedure; Codex prefers its connected GitHub app when available and has different write-safety rules. |
| `babysit` | keep variants | Claude owns `/loop`, cron deletion, state files, and push notification behavior. Codex reuses `land/land_watch.py` and Codex automations. |
| `browser-evidence` | keep variants | Claude uses Claude-in-Chrome connection selection. Codex uses its browser connectors and bundled browser-control environment. |
| `prompt-agent-orchestrator` | keep variants | Claude uses `$ARGUMENTS`, a host-specific output template, and different capability checks; Codex uses a separate reference template and Codex-oriented workflow. |
| `land` | Codex only | Codex watcher and landing workflow; no equivalent source is shipped for Claude Code. |
| `publish-slack` | Claude only | Claude-specific Slack draft workflow; no Codex source is shipped. |

The migration removes two duplicated host pairs: four host directories become
two canonical directories. The tracked instruction count drops by two
`SKILL.md` files while preserving all host metadata and every intentional
variant. Together with PR #23, three skills now use canonical storage.

## Installation constraints

The Skills CLI discovers common skill containers in priority order and
deduplicates by the frontmatter `name`. A repository-wide `--all` operation can
therefore choose only one source when `.codex/skills` and `.claude/skills`
contain same-name variants.

The installed canonical store and lock file are also keyed by skill name. Two
same-name host variants cannot be independently tracked in that store. Install
from the exact `.agents/skills`, `.codex/skills`, and `.claude/skills` source
subtrees with explicit CLI agent targeting. Use `--copy` for the Claude
subtree so a Claude variant remains independent from the same-name Codex
variant. Refresh a complete installation by re-running the three `skills add`
commands in README order; the generic `skills update` command does not preserve
two sources or copy modes for one name.

For canonical skills, installation has these invariants:

1. One real directory exists at `.agents/skills/<skill>` (project) or
   `~/.agents/skills/<skill>` (global).
2. Codex uses that directory directly and does not need a `.codex/skills` link.
3. Claude Code receives `.claude/skills/<skill>` pointing to the canonical
   directory.
4. A canonical-only `skills update` preserves the canonical directory plus
   Claude link topology.
5. Removing only Claude's link keeps the canonical directory while Codex still
   uses it. Removing the skill from all agents removes the canonical directory
   and its lock entry. This is the subset-removal contract implemented in
   [`remove.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/remove.ts).

Run `python -m unittest discover -s tests -v` for the repository layout audit.
Run `pwsh -File tests/test_skills_cli_windows.ps1 -RepositoryRoot <source>` on
Windows for an isolated CLI lifecycle check. A GitHub shorthand with a fragment
ref, such as `owner/repo#feature-branch`, exercises remote update checking. URL
encode `/` as `%2F` when the branch name contains a slash. A local repository
path exercises discovery, agent-targeted installation, junction and copy
placement, and removal but is not remotely updatable.

## Migration checklist

1. If a source checkout lives directly inside an agent's managed skills
   directory, move it elsewhere before cleanup.
2. Run the scoped `npx skills remove` command from the README. The CLI deletes
   a link or junction without deleting its target, but deletes a real installed
   copy.
3. Run the three agent-targeted `npx skills add` commands in README order.
4. Restart Codex and Claude Code so they rescan skills.
5. Verify names and descriptions in each host, then exercise one canonical
   skill from both hosts.
