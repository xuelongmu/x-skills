---
name: steward-research
description: Organize and maintain research-oriented repositories for reproducibility, experiment continuity, and collaborator handoff. Use when an agent needs to audit or document experiments, preserve a dated research log, capture data provenance or calibration assumptions, create runbooks, separate local artifacts from versioned source, turn one-off research commands into portable tooling, prepare a focused contribution, or safely hand unfinished research to another person or agent.
---

# Steward a Research Repository

Convert exploratory work into an honest, reproducible handoff while preserving
the user's data, unfinished work, and repository conventions.

## Establish scope before changing files

1. Read every applicable `AGENTS.md` and repository-specific instruction.
2. Inspect the README, documentation layout, changelog, issue/PR conventions,
   Git status, current branch, remotes, and recent commits.
3. Inventory untracked and modified files. Treat existing changes as
   user-authored unless their provenance is known.
4. Classify the request:
   - **audit or report:** inspect and recommend without writing;
   - **organize or hand off:** update documentation and portable repository
     materials, but do not publish;
   - **publish:** prepare and validate the contribution, then use the
     repository's publishing workflow only when explicitly requested.
5. State the proposed file and PR scope before a broad reorganization. Keep
   unrelated work out of the contribution.

Do not use a documentation task as permission to rerun costly experiments,
delete caches, terminate processes, upload artifacts, or mutate remote state.

## Build a durable research record

Prefer the repository's existing conventions. When no equivalent exists,
propose the smallest useful set:

- root `AGENTS.md` for operating and contribution policy;
- a direct pointer file for another agent system only when the repository uses
  one;
- root `CHANGELOG.md` for repository-visible changes;
- `docs/status.md` as an append-only, dated experiment log;
- focused runbooks for environment, execution, recovery, data preparation,
  visualization, or evaluation.

Do not rename established documentation merely to impose these names. Link the
handoff documents from the README when that materially improves discovery.

For each meaningful experiment or decision, record the applicable fields:

- date, objective, and current state;
- input identity, provenance, access restrictions, and license caveats;
- code revision, environment, configuration, seeds, frame interval, data split,
  camera/view subset, and output tag;
- exact reproducible command or a repository-relative launcher;
- cache or artifact reuse and the variable intentionally changed;
- quantitative results with units and qualitative observations;
- artifact locations without embedding credentials or private machine state;
- failures, limitations, uncertainty, superseded conclusions, and next action.

Append corrections instead of silently rewriting past results. Distinguish
observations from inferences and verified ground truth from proxy or duplicated
fields. Preserve negative results and failed approaches when they affect future
decisions.

## Protect experimental validity

- Change one intended variable in an ablation. Keep inputs, preprocessing,
  identity assignments, seeds, frame ranges, and upstream caches fixed when the
  comparison claims they are controlled.
- Record every reused artifact and its compatibility assumptions.
- Treat a successful process exit as insufficient evidence. Inspect scientific
  diagnostics and representative outputs appropriate to the domain.
- Do not report accuracy from arrays named like ground truth until provenance
  and independence are established.
- Do not tune away outliers or revise methodology after seeing results without
  documenting the change as a new experiment.
- Mark pending, partial, blocked, and invalid runs explicitly.

## Separate source from research artifacts

Classify files before staging:

| Class | Normal handling |
| --- | --- |
| source, tests, small text configs | version when reusable and in scope |
| runbooks and research metadata | version after removing secrets and private state |
| datasets, model weights, credentials | never commit |
| generated outputs, caches, checkpoints | ignore unless the repository explicitly defines a small canonical fixture |
| images, audio, video, recordings, render previews | keep local by default; upload only when policy permits and the user confirms the content is non-sensitive |

If repository policy permits it, use a root `tmp/` directory for disposable
local work, including temporary media. Add `/tmp/` to `.gitignore`; never
force-add or upload its contents. Otherwise use the repository's existing
scratch convention or an external temporary directory.

Keep media local by default. Attach it to PRs or issues, add it as a release
asset, or upload it to a separate storage service only when repository policy
permits it and the user confirms it is non-sensitive client data. Never upload
credentials, restricted or licensed assets, or private machine state.

Scan the intended contribution for common media extensions, large binaries,
credentials, absolute user paths, hostnames, PIDs, fixed ports, and licensed
assets before committing.

## Promote only reusable tooling

Convert a one-off command into repository tooling only when another researcher
can run it with explicit inputs and understand its assumptions.

- Use repository-relative defaults and CLI parameters.
- Keep source data and output paths configurable.
- Write an auditable manifest when transforming data or calibration.
- Refuse destructive overwrites unless the user opts in.
- Validate inputs before expensive computation.
- Add focused tests for fragile conventions, coordinate transforms, unit
  conversions, indexing, and file-format parsing.
- Prefer the repository's existing runtime and dependencies.

Leave machine-specific orchestration, personal paths, and unexplained local
helpers outside the contribution.

## Validate in proportion to risk

Prefer commands already documented by the repository. At minimum, when the
relevant tools exist:

1. run `git diff --check` and `git diff --cached --check`;
2. parse changed structured configuration with its native loader;
3. run focused tests and syntax checks for changed tooling;
4. validate documentation links and command paths;
5. materialize or dry-run new experiment configurations;
6. perform the smallest representative smoke test that exercises new code;
7. inspect the final Git diff, file modes, untracked files, and staged file list;
8. confirm no media, generated output, secret, credential, or unrelated file is
   staged.

Report environmental failures separately from defects introduced by the
change. State the validation level accurately and distinguish syntax or
configuration checks from full experiment reproduction.

## Prepare contributions safely

- Never commit directly to the default branch.
- Use one focused PR for a cohesive handoff. Use stacked PRs only when later
  changes functionally depend on earlier independently reviewable changes.
- In a fork workflow, identify the head and base owner, repository, and branch
  explicitly. Treat upstream as read-only unless both repository policy and the
  user explicitly authorize an upstream action.
- Never open an issue or PR on an inferred target. Verify it immediately before
  creation.
- Do not push, open a PR, create an issue, merge, or upload anything unless the
  user explicitly requests that remote action.
- Use the established publishing skill or workflow rather than duplicating it
  here.

At handoff, summarize the branch, intended diff, validation, excluded local
work, artifact policy, pending research, and the next concrete action.
