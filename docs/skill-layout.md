# Skill source layout

All thirteen skills live once under `.agents/skills/<skill>/`. Codex discovers
that tree directly; the `npx skills` installer exposes complete directories to
Claude Code through symlinks or Windows junctions. There are no checked-in host
links or duplicated implementations.

## Storage and installation contract

Use `npx skills` for installation, refresh, migration, and removal, following the
[README](../README.md). The update command updates the complete selected scope,
including other sources; it reports new skills without installing them and
offers removal of upstream deletions.

The canonical directory is `.agents/skills` for project scope or
`~/.agents/skills` for global scope. Host links must include references, scripts,
and metadata. Removing only one host's link must preserve a canonical copy still
used by another host.

This topology was checked against `vercel-labs/skills` 1.5.23 at
[revision 435076e](https://github.com/vercel-labs/skills/tree/435076e78988e1e6ec40d00b0b1d76bdbbc5419a).
The installer does not automatically resolve sibling dependencies: select
`land` in the same scope when installing `publish` or `babysit`.

## Ownership audit

| Skills | Canonical ownership |
| --- | --- |
| publish, babysit, land | Three user intents; shared PR operations and watcher contract belong to land. Only landing authorizes merge. |
| browser-evidence | Evidence criteria are portable; the active host owns browser selection and tool protocols. Platform launchers are optional scripts. |
| review-change, review-complexity | Change readiness and overengineering remain separate capabilities; specialist references are conditional. |
| design-architecture, review-architecture | Design generation and assessment remain separate. Optional sibling routing has a direct-analysis fallback. |
| capture-learning, steward-research | Verified reusable knowledge and reproducible research have distinct destinations and evidence requirements. |
| prompt-agent-orchestrator, drive-agent-orchestrator | Prompt authoring and live AO operation remain separate. AO-specific contracts justify detailed guidance. |
| google-developer-style | A deliberate house style shared across hosts, with CC BY 4.0 attribution. |

`.codex/skills` and `.claude/skills` are empty. Add a real host-specific variant
only when instructions or lifecycle meaningfully differ. Capability selection
alone does not require another implementation. Host-specific review approval
policies, browser tool-name catalogs, and sign-off labels are no longer embedded
in portable workflows. Any unavailable capability must be reported accurately;
it does not waive required evidence or authorization.

## Bundled resources

- `land/references/pr-workflow.md` owns publication and maintenance mechanics.
  `publish` and `babysit` link to it relative to their active directories.
- `land/scripts/land_watch.py` remains the deterministic PR watcher.
  `land/references/watcher.md` defines its invocation and readiness contract.
- `land/references/slack.md` loads only for requested PR sharing.
- `browser-evidence/scripts/launch-chrome.ps1` and `launch-chrome.sh` contain
  the former inline fallback launchers. Browser fallbacks explain use and cleanup.
- Architecture decision surfaces, consequence analysis, review lenses, learning
  destination routing, and review complexity references are optional detail.
  Duplicate project-invariant catalogs and mandatory report templates were removed.

Resolve all resources relative to the active skill directory. Run the watcher
from the target PR repository so its checkout context is correct. Store
executable helpers in `scripts/` and product metadata in `agents/openai.yaml`.
Every `SKILL.md` uses only Agent Skills standard frontmatter.

## Validation

Repository tests cover skill metadata, inventory, bundled-resource links, and
watcher behavior. Installation, updates, host links, and removal belong to
`npx skills`; this repository does not maintain an installer lifecycle test.
Review installation and migration guidance for accuracy without locking its
wording or command formatting in tests.

Run structural, resource, and watcher checks:

```bash
python -B -m unittest discover -s tests -v
uvx --from skills-ref agentskills validate <skill-directory>
```

The resource audit checks relative links, including sibling links under a relocated
installation. It does not enforce prose, report headings, or a fixed process.
The watcher tests retain executable coverage of feedback, CI, selected-host
identity, changed heads, and terminal states.

After changing launcher code, validate shell syntax and exercise the launcher on
its supported platform in task-local scratch space, verifying endpoint ownership
and cleanup. A syntax check on a different OS is not runtime coverage.

Use the [evaluation scenarios](skill-evaluation.md) for instruction behavior.
Compare completion, scope, unnecessary questions and checks, and justified
boundaries. Do not claim cross-model validation from phrase assertions.
