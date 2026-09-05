# Skill source layout

All sixteen skills live once under `.agents/skills/<skill>/`. Codex discovers
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
| evaluate-skill | Canonical scenario design, controlled comparison, and interpretation. Bundled decision fixtures and a standard-library packet helper are portable; host isolation and native loading must be established per run. No live runner or host-specific variant is supplied. |
| prompt-agent-orchestrator, drive-agent-orchestrator | Prompt authoring and live AO operation remain separate. AO-specific contracts justify detailed guidance. |
| orchestrate | One harness-independent workflow, adapting to blocking/background execution, context and workspace isolation, and resumable or one-shot workers. Optional Codex UI metadata contains no execution behavior; no separate host variants are needed. Cross-harness runtime validation remains outstanding. |
| google-developer-style | A deliberate house style shared across hosts, with CC BY 4.0 attribution. |
| show-me | Visual guidance and evidence labeling; the agent chooses valuable formats and detail. Callers retain scope and authority; the host supplies rendering capabilities. |

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
- `evaluate-skill/fixtures/` owns the repeatable decision cases, with agent inputs
  and evaluator criteria in separate files. `scripts/fixture_packet.py` validates
  cases and emits only released inputs relative to the installed skill directory.
  The evaluator installation must be inaccessible to the tested agent; the helper
  is not an isolation boundary. Larger manual scenarios remain in
  [skill evaluation](skill-evaluation.md), which links migrated cases to that
  authority instead of duplicating their facts.
- `browser-evidence/scripts/launch-chrome.ps1` and `launch-chrome.sh` contain
  the former inline fallback launchers. Browser fallbacks explain use and cleanup.
- Architecture decision surfaces, consequence analysis, review lenses, learning
  destination routing, and review complexity references are optional detail.
  Duplicate project-invariant catalogs and mandatory report templates were removed.
- `show-me` is an optional sibling for architecture, review, and learning skills,
  not a bundled reference or required dependency. Callers explain directly when
  it is absent; visual selection rules live only in `show-me`.

Resolve all resources relative to the active skill directory. Run the watcher
from the target PR repository so its checkout context is correct. Store
executable helpers in `scripts/` and product metadata in `agents/openai.yaml`.
Every `SKILL.md` uses only Agent Skills standard frontmatter.

## Validation

Repository tests cover skill metadata, source layout, bundled-resource links, and
watcher behavior. Installation, updates, host links, and removal belong to
`npx skills`; this repository does not maintain an installer lifecycle test.
Review installation and migration guidance for accuracy without locking its
wording or command formatting in tests.

With Python 3.12 or later, Git, and `uv` available, run all checks from the
repository root. `uv` provides the test dependencies in an isolated environment:

```bash
uv run --no-project --with-requirements tests/requirements.txt python -B -m unittest discover -s tests -v
```

The layout audit discovers skill directories without a separate name inventory.
It calls the upstream [Agent Skills reference validator](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref),
pinned in `tests/requirements.txt`, for frontmatter and naming rules. Upstream
labels the library as a reference implementation for demonstration purposes;
review coverage when updating its revision. Small local checks cover YAML field
types that it does not enforce, canonical source ownership, and Codex
`agents/openai.yaml` metadata. PyYAML handles field types and Codex metadata.

To run only the upstream validator for one skill:

```bash
uv run --no-project --with-requirements tests/requirements.txt skills-ref validate .agents/skills/publish
```

This standalone command does not run the local checks described above.

The resource audit checks relative links, including sibling links under a relocated
installation. It does not enforce prose, report headings, or a fixed process.
The watcher tests retain executable coverage of feedback, CI, selected-host
identity, changed heads, and terminal states.
The evaluation helper tests cover packet separation, event release, invalid inputs,
relocation, and selected fixture code facts. They do not run or grade models.
Manual simulated decisions are supported on skill-capable hosts with adequate
isolation; hosts that cannot isolate the catalog or rubric cannot support the
corresponding condition. Native discovery and execution remain unvalidated across
hosts. Use only `npx skills` for distribution as described above; constructing an
evaluation context must not alter a user's installed skills or global settings.

After changing launcher code, validate shell syntax and exercise the launcher on
its supported platform in task-local scratch space, verifying endpoint ownership
and cleanup. A syntax check on a different OS is not runtime coverage.

Use the [evaluation scenarios](skill-evaluation.md) for instruction behavior.
Compare completion, scope, unnecessary questions and checks, and justified
boundaries. Do not claim cross-model validation from phrase assertions.
