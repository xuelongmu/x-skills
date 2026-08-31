# Skill source layout

This repository stores each cross-host capability once and follows the Agent
Skills specification for every `SKILL.md`.

## Storage contract

- `.agents/skills/<skill>` is the canonical source for behavior available in
  both Codex and Claude Code. Codex discovers this directory directly.
- `.claude/skills/<skill>` is reserved for a capability that this repository
  supports only in Claude Code. Currently, only `publish-slack` is host-only.
- `.codex/skills` is currently empty. Add a source there only when a future
  capability is genuinely Codex-only and cannot be expressed as portable
  instructions with capability-based tool selection.
- Checked-in links are not part of the source layout. The installer creates a
  symlink, or a Windows junction, for a host that does not discover the
  canonical location directly.

This matches `vercel-labs/skills` 1.5.23 at revision
[`435076e`](https://github.com/vercel-labs/skills/tree/435076e78988e1e6ec40d00b0b1d76bdbbc5419a):
[`installer.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/installer.ts)
uses `.agents/skills` and `~/.agents/skills` as the canonical project and
global locations and creates Windows junctions with absolute targets;
[`agents.ts`](https://github.com/vercel-labs/skills/blob/435076e78988e1e6ec40d00b0b1d76bdbbc5419a/src/agents.ts)
classifies Codex as universal and Claude Code as `.claude/skills`.

## Agent Skills compliance

Every source uses standard top-level frontmatter: `name`, `description`, and
only the optional fields defined by the Agent Skills specification. Host-only
fields such as Claude Code's `argument-hint` are not present in canonical
sources. OpenAI UI metadata remains in the optional `agents/openai.yaml` file.

Bundled code lives under `scripts/`. Instructions resolve scripts and other
resources relative to the active `SKILL.md`, never from a hard-coded host
installation path. The `land` watcher is therefore available at
`land/scripts/land_watch.py` through both the canonical Codex directory and the
Claude link to that directory.

Run the repository tests plus the official reference validator:

```bash
python -m unittest discover -s tests -v
skills-ref validate <skill-directory>
```

## Consolidation audit

| Skill | Decision | Reason |
|---|---|---|
| `publish` | canonical | Both implementations performed the same Git, validation, push, and ready-PR workflow; the shared source chooses an authenticated GitHub connector when suitable and otherwise uses `gh`. |
| `babysit` | canonical | Both implementations kept a PR healthy without merging. The shared source uses the host's recurring monitor and the bundled `land` watcher. |
| `land` | canonical | The merge workflow, `gh` operations, and Python watcher are host-neutral; the complete skill directory installs for both hosts. |
| `prompt-agent-orchestrator` | canonical | The readiness contract is shared. The prompt template remains a progressively loaded reference. |
| `drive-agent-orchestrator` | canonical | The instructions are host-neutral. The Claude-only autocomplete hint was removed to keep standard frontmatter. |
| `browser-evidence` | canonical | Browser selection is capability-based instead of naming a host-specific browser connector. |
| `steward-research` | canonical | The previous host copies were byte-identical. |
| `google-developer-style` | canonical | Introduced as a shared source in PR #23. |
| `publish-slack` | Claude only | The shipped workflow depends on Claude's Slack MCP tools. Codex support is intentionally unavailable until the repository has a tested portable Slack capability. |

Before this consolidation, the repository tracked 15 `SKILL.md` sources: one
canonical source and seven sources for each host. It now tracks nine: eight
canonical sources and one Claude-only source. Six duplicated cross-host pairs
were removed without removing a capability, and `land` became available to
Claude Code.

## Installation constraints

Install from the exact source subtrees with explicit agent targeting. Do not
install from the repository root with `--all`, because that can expose a
host-only source to an unsupported host.

Canonical installation has these invariants:

1. One real directory exists at `.agents/skills/<skill>` for project scope or
   `~/.agents/skills/<skill>` for global scope.
2. Codex uses that directory directly.
3. Claude Code receives `.claude/skills/<skill>` pointing to the same complete
   directory, including `scripts/`, `references/`, and `agents/`.
4. Updating a canonical skill preserves the canonical directory and Claude
   link topology.
5. Removing only Claude's link keeps the canonical directory while Codex still
   uses it. Removing the skill from all agents removes the canonical directory
   and its lock entry.

The Claude-only subtree uses CLI copy mode to avoid placing `publish-slack` in
the universal store. Refresh a complete installation by rerunning both `skills
add` commands from the README because generic update does not preserve that
copy-mode decision.

Run `python -m unittest discover -s tests -v` for the source and format audit.
Run `pwsh -File tests/test_skills_cli_windows.ps1 -RepositoryRoot <source>` on
Windows for an isolated lifecycle check. A GitHub shorthand with a fragment
ref, such as `owner/repo#feature-branch`, exercises remote update checking. URL
encode `/` as `%2F` when the branch name contains a slash.

## Migration checklist

1. If a source checkout lives directly inside an agent's managed skills
   directory, move it elsewhere before cleanup.
2. Run the scoped `npx skills remove` command from the README. The CLI deletes
   a link or junction without deleting its target, but deletes a real installed
   copy.
3. Run the two agent-targeted `npx skills add` commands in README order.
4. Restart Codex and Claude Code so they rescan skills.
5. Verify names and descriptions in each host, then exercise `land` from both
   hosts to confirm that the bundled watcher resolves from the installed skill
   directory.
