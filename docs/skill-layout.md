# Skill source layout

This repository stores each cross-host capability once and follows the Agent
Skills specification for every `SKILL.md`.

## Storage contract

- `.agents/skills/<skill>` is the canonical source for behavior available in
  both Codex and Claude Code. Codex discovers this directory directly.
- `.codex/skills` and `.claude/skills` are currently empty. Add a source there
  only when a future capability is genuinely host-only and cannot be expressed
  as portable instructions with capability-based tool selection.
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
uvx --from skills-ref agentskills validate <skill-directory>
```

## Consolidation audit

| Skill | Decision | Reason |
|---|---|---|
| `publish` | canonical | Both implementations performed the same Git, validation, push, and ready-PR workflow; the shared source chooses an authenticated GitHub connector when suitable and otherwise uses `gh`. |
| `babysit` | canonical | Both implementations kept a PR healthy without merging. The shared source uses the host's recurring monitor and the bundled `land` watcher. |
| `land` | canonical | The merge workflow, `gh` operations, Python watcher, optional Slack sharing, and native-autofix coordination are expressed through host capabilities; the complete skill directory installs for both hosts. |
| `prompt-agent-orchestrator` | canonical | The readiness contract is shared. The prompt template remains a progressively loaded reference. |
| `drive-agent-orchestrator` | canonical | The instructions are host-neutral. The Claude-only autocomplete hint was removed to keep standard frontmatter. |
| `browser-evidence` | canonical | Browser selection is capability-based instead of naming a host-specific browser connector. |
| `steward-research` | canonical | The previous host copies were byte-identical. |
| `code-meta-reviewer` | canonical | The meta-review and simplification workflow is shared; Codex task-history lookup is selected only when the active host exposes that capability. |
| `capture-learning` | canonical | Evidence gates and destination routing are host-neutral. The skill discovers repository authorities and loads its routing reference only after a candidate qualifies. |
| `review-change` | canonical | Intent recovery, review-only safety, verification audit, and diff-routed risk lenses do not depend on host-specific tools; optional local or external reviewers are capability- and authorization-gated. |
| `google-developer-style` | canonical | Introduced as a shared source in PR #23. |
| `publish-slack` | folded into `land` | PR sharing and Vercel preview lookup are host-neutral. `land` uses any authenticated Slack capability, drafts by default, and sends only on explicit request. |

Before this consolidation, the repository tracked 15 `SKILL.md` sources: one
canonical source plus seven sources for each host. The migration removed six
duplicated cross-host pairs, folded the former Claude-only `publish-slack`
workflow into `land`, and made `land` available to Claude Code. The repository
now tracks eleven canonical sources, including the subsequently added
`code-meta-reviewer`, `capture-learning`, and `review-change`, without
reintroducing host copies. The consolidation still removes seven duplicated
sources without removing a workflow.

## Installation constraints

Install from the repository shorthand. The CLI discovers canonical skills under
`.agents/skills` and lets the user select skills, supported agents, and
installation scope.

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

Use `npx skills@latest update` for refreshes. It updates the complete selected
scope, interactively offers to remove skills deleted upstream, and reports newly
available skills without installing them. If the command reports a new skill,
rerun the installer from the README to opt into it. Use the interactive `remove`
command for repository-specific cleanup.

Claude's per-PR **Auto-fix CI & address comments** control is a native event and
remediation channel for `land`, not a distinct source. When enabled, it avoids a
redundant recurring babysit loop, while the bundled watcher and synchronous
final refresh remain authoritative. `land` does not enable Claude's separate
**Auto-merge when ready** control.

## Host-only interfaces retained in canonical skills

The audit found no meaningfully different skill implementations, but it did
find host-only invocation surfaces that the shared instructions must preserve:

| Host | Interface | Canonical handling |
|---|---|---|
| Codex | `browser:control-in-app-browser` | `browser-evidence` conditionally loads the signed-in browser-control skill before offering an unauthenticated fallback. |
| Claude Code | Slash-command invocations such as `/land` and `/babysit` | Documentation shows Claude's invocation syntax while the installed `SKILL.md` remains shared. |
| Claude Code | `ToolSearch`, `AskUserQuestion`, and `mcp__claude-in-chrome__*` browser tools | `browser-evidence` conditionally loads deferred connector schemas, asks the user to select a connected browser, and follows the connector recovery flow. |
| Claude Code | `/loop`, `CronList`, `CronDelete`, and `PushNotification` | `babysit` conditionally preserves recurring-loop cleanup, the once-per-head Codex sign-off notification, and Claude's `reviewDecision == APPROVED` readiness gate. |
| Claude Code | `ToolSearch` and `mcp__claude_ai_Slack__*` connector tools | `land` conditionally loads deferred Slack schemas before channel lookup, drafting, or an explicitly authorized send. |
| Claude Code | **Auto-fix CI & address comments** | `land` treats it as optional dispatch and remediation; the shared watcher still owns final readiness. |
| Claude Code | `reviewDecision` approval gate | `land` refreshes the selected PR immediately before merging and requires `APPROVED`; watcher success alone cannot bypass human approval. |
| Codex desktop | Task listing and task-history readers | `code-meta-reviewer` reads only pertinent tasks associated with the target repository or workstream when those tools are available; other hosts use history supplied in the conversation or as an export. |

These adapters do not change the underlying workflow or justify duplicated
skill sources. If a future host-specific interface changes the actual tools,
authorization boundary, or lifecycle semantics rather than merely dispatching
the same workflow, add a host-specific source and record the exception here.

Run `python -m unittest discover -s tests -v` for the source and format audit.
Run `pwsh -File tests/test_skills_cli_windows.ps1 -RepositoryRoot <source>` on
Windows for an isolated lifecycle check. A GitHub shorthand with a fragment
ref, such as `owner/repo#feature-branch`, exercises remote update checking. URL
encode `/` as `%2F` when the branch name contains a slash.

## Migration checklist

1. If a source checkout lives directly inside an agent's managed skills
   directory, move it elsewhere before cleanup.
2. Run the interactive `npx skills@latest remove` command from the README and
   select this repository's entries. The CLI handles managed copies and links
   without deleting link targets.
3. Reinstall with the command in the README, then restart Codex and Claude Code.
4. Verify names and descriptions in each host. Confirm that
   `capture-learning` and `review-change` can load their bundled references, then
   exercise `land` from both hosts to confirm that the watcher resolves from the
   installed skill directory. On a Claude surface, verify that native autofix
   events re-enter the same workflow without bypassing final checks.
