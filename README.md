# x-skills

Portable workflow skills for Claude Code and Codex.

## Skills

| Skill | What it does | Claude Code | Codex | Source |
|---|---|---|---|---|
| publish | Publish intended changes to a new or existing PR | `/publish` | `publish` | canonical |
| babysit | Keep the PR ready without merging: fix CI, address review comments, and sync the base branch | `/babysit` | `babysit` | canonical |
| land | Open or share a PR, keep it healthy, and merge once checks and feedback gates pass | `/land` | `land` | canonical |
| orchestrate | Lead delegated work through bounded milestones, selective updates, and human review checkpoints | `/orchestrate` | `orchestrate` | canonical |
| prompt-agent-orchestrator | Draft and validate multi-issue Agent Orchestrator project prompts | `/prompt-agent-orchestrator <brief>` | `prompt-agent-orchestrator` | canonical |
| drive-agent-orchestrator | Operate Agent Orchestrator: preflight, spawn/supervise workers and orchestrators, monitor sessions | `/drive-agent-orchestrator` | `drive-agent-orchestrator` | canonical |
| browser-evidence | Drive a running app, verify a flow, and capture browser-visible evidence | `/browser-evidence` | `browser-evidence` | canonical |
| steward-research | Organize research repositories for reproducibility and safe handoff | `/steward-research` | `steward-research` | canonical |
| capture-learning | Route a verified reusable learning to its owning repository authority | `/capture-learning` | `capture-learning` | canonical |
| evaluate-skill | Author scenarios, compare skill conditions, and interpret benefit, regressions, and overhead | `/evaluate-skill` | `evaluate-skill` | canonical |
| review-change | Review a change against intent, resulting design, verification, and diff-selected risks | `/review-change` | `review-change` | canonical |
| review-complexity | Audit overengineering and review-driven complexity without changing accepted behavior | `/review-complexity` | `review-complexity` | canonical |
| google-developer-style | Draft, revise, or review clear, accessible developer documentation using distilled Google-style guidance | `/google-developer-style [documentation or path]` | `google-developer-style` | canonical |
| design-architecture | Explore consequential system choices and recommend a repo-grounded architecture before implementation | `/design-architecture [decision]` | `design-architecture` | canonical |
| review-architecture | Review a design proposal or ADR draft and return an evidence-backed architecture verdict | `/review-architecture [artifact]` | `review-architecture` | canonical |

- `babysit` never merges, enables auto-merge, or deletes branches. `land` can
  publish a missing PR and is the only skill that merges.
- `publish` and `babysit` share operational references owned by `land`.
  Select `land` alongside either skill in the installer, in the same scope;
  the CLI does not automatically install sibling dependencies.
- Continuous `babysit` follows the requested duration or completion condition and
  uses the current host's recurring facility. Quiet cycles do not end monitoring.
- `land` includes the former `publish-slack` workflow. Ask it to share the PR in
  Slack to create a draft with the Vercel preview; ask explicitly to send when
  a draft is not desired.

## Setup

Use the [`npx skills`](https://github.com/vercel-labs/skills) CLI for all
installation, refresh, and removal operations. The repository has one populated
source subtree:

- `.agents/skills` contains host-neutral sources. The CLI stores one canonical
  copy in `.agents/skills` (project) or `~/.agents/skills` (global). Codex reads
  it directly; Claude Code receives a symlink or, on Windows, a junction.

### Install

Run the installer from the project where you want to use the skills:

```bash
npx skills@latest add xuelongmu/x-skills
```

The CLI discovers the repository's canonical skills and lets you choose the
skills, supported agents, and installation scope. Restart each selected agent
after installation.

### Refresh

Refresh installed skills and reconcile upstream deletions with:

```bash
npx skills@latest update
```

Choose the project, global, or combined scope when prompted, and confirm removal
of skills deleted upstream. The update command has no repository filter, so it
can update skills installed from other sources in the selected scope. It reports
new skills without installing them. To opt into a newly reported skill, run the
installer from the **Install** section again and select that skill. Restart each
selected agent after the refresh.

### Remove or migrate a legacy installation

Use the interactive removal command:

```bash
npx skills@latest remove
```

Project-local removal is the default. Add `--global` to remove a global
installation. Select only entries installed from this repository.

For the retired pre-rename entry, run this legacy cleanup separately:

```bash
npx skills@latest remove code-meta-reviewer
```

For a legacy installation, move any source checkout outside the agent's managed
skills directory before removal. The CLI handles managed copies and links
without deleting link targets. Then reinstall with the command in **Install**.

The `land` watcher is bundled at `scripts/land_watch.py`. Skills resolve bundled
resources relative to the active `SKILL.md`; run watcher commands from the PR
repository so `gh` resolves the correct repository.

See [the skill layout audit](docs/skill-layout.md) for migration scope,
intentional exceptions, CLI constraints, and duplication counts.

## Design notes

Skills specify outcomes, meaningful constraints, and non-obvious operational
knowledge. Agents choose the method and proportionate verification. Supporting
references load only for the relevant mode or risk.

- `land` owns shared PR publication and maintenance operations, plus the
  deterministic watcher. `publish` stops at publication; `babysit` maintains
  readiness; only a landing request authorizes merging.
- Required approvals, merge methods, and branch cleanup follow the target
  repository and user on every host. Base synchronization preserves shared
  history by default; an authorized rebase uses `--force-with-lease`.
- The watcher keeps its 30-second polling and 15-minute feedback grace defaults.
  Its [contract](.agents/skills/land/references/watcher.md) documents overrides,
  exit codes, and the validated head that must be passed to merging.
- Native autofix can own remediation without creating a second loop. Readiness
  notifications use current-head evidence and monitor state, not bot reactions
  or repository labels. A closed unmerged PR is terminal, not ready.
- Browser control follows the active capability's schemas. Optional raw-CDP
  launchers live under `browser-evidence/scripts/`; a working connector never
  requires loading them.
- Review and architecture skills preserve distinct user intents without
  requiring a fixed series of passes or reports. Missing optional sibling skills
  do not block assessment. Design recommendations do not create accepted ADRs.
- `orchestrate` owns host-neutral coordination judgment: task boundaries,
  dependencies, quiet progress handling, review scope, and checkpoint handoff.
  The same source is intended for Claude Code, Codex, and other skill-capable
  harnesses; it adapts to blocking, background, or non-resumable workers without
  requiring a particular tool API. `agents/openai.yaml` is optional Codex UI
  metadata, not an execution dependency. Other harnesses have not been runtime-tested.
  The AO skills own service-specific prompt contracts and operations; none
  authorizes delegation or external changes beyond the user's request.
- Reusable learnings belong in their owning test, contract, runbook, or skill.
  Avoid general advice and duplicated rules.
- `evaluate-skill` supports scenario authoring, controlled comparisons, revision
  assessment, and interpretation independently. Baseline, discoverable, and
  explicitly loaded conditions separate instruction value from discovery.
  Bundled fixtures and a Python standard-library packet helper support manual
  simulated decisions; no isolated live model runner is bundled. Criteria must
  be inaccessible to the tested agent. See its
  [workflow and fixtures](.agents/skills/evaluate-skill/SKILL.md).

The review and learning workflows synthesize ideas from immutable snapshots of
[Compound Engineering](https://github.com/everyinc/compound-engineering-plugin/tree/5f5bc6b96518c69decdec955b353f49631f921da),
[Matt Pocock's skills](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76),
and [Addy Osmani's agent-skills](https://github.com/addyosmani/agent-skills/tree/d2c37ef6225dd8726cdd369a8030307f48592d26).
The Google style skill is a CC BY 4.0 synthesis of the Google guide.

See [evaluation scenarios](docs/skill-evaluation.md) for checking behavior after
instruction changes. Structural checks do not prove agent behavior.
