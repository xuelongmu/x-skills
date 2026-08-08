---
name: steward-research
description: Steward research repositories for reproducibility and handoff. Use when an agent needs to audit or document experiments, record provenance or assumptions, create runbooks, separate local artifacts from versioned source, promote reusable research tooling, prepare a focused contribution, or hand unfinished research to another collaborator.
---

# Steward a Research Repository

Turn exploratory work into a reproducible handoff without disturbing the
user's data, unfinished work, or repository conventions.

## Set scope

1. Read applicable repository instructions and documentation.
2. Inspect Git status, the current branch, remotes, recent commits, and all
   modified or untracked files. Treat existing changes as user-authored unless
   their provenance is known.
3. Match the work to the request:
   - **audit:** inspect and report without writing;
   - **organize or hand off:** update local documentation or reusable tooling;
   - **publish:** use the repository's publishing workflow only when requested.
4. Define a focused file and contribution scope before broad reorganization.

Do not infer permission to rerun costly experiments, delete artifacts, stop
processes, upload data, or mutate remote state.

## Keep a reproducible record

Follow existing documentation conventions. If none fit, add only what the
handoff needs, usually a dated experiment log or focused runbook.

For each meaningful experiment or decision, record what applies:

- date, objective, status, and next action;
- input identity, provenance, access limits, and license caveats;
- code revision, environment, configuration, seeds, and data split;
- the exact command or repository-relative launcher;
- reused artifacts or caches and the variable intentionally changed;
- quantitative results with units and qualitative observations;
- failures, limitations, uncertainty, and artifact locations.

Append corrections instead of silently rewriting history. Distinguish
observations from inferences and verified ground truth from proxies. Preserve
negative or superseded results when they affect later decisions.

## Preserve experimental validity

- Change one intended variable in an ablation and keep claimed controls fixed.
- Record reused artifacts and their compatibility assumptions.
- Inspect relevant diagnostics and representative outputs; a successful exit
  alone is not scientific evidence.
- Mark pending, partial, blocked, and invalid runs clearly.
- Record methodology changes made after seeing results as new experiments.

## Separate source from artifacts

Classify files before staging:

| Class | Normal handling |
| --- | --- |
| reusable source, tests, configs, and documentation | version when sanitized and in scope |
| datasets, model weights, credentials, and private paths | keep out of Git |
| generated outputs, caches, and checkpoints | ignore unless the repository defines a canonical fixture |
| images, audio, video, and render previews | keep local by default |

Upload media only when repository policy permits it and the user confirms it
is non-sensitive client data. Never upload credentials, restricted or licensed
assets, or private machine state.

Use the repository's scratch convention. If none exists and policy permits,
use an ignored root `tmp/` directory. Before staging, scan for secrets, private
paths, unexpected binaries, generated output, and licensed assets.

## Promote reusable tooling

- Use explicit inputs, configurable paths, and repository-relative defaults.
- Write a manifest for data or calibration transformations.
- Validate inputs before expensive work and require opt-in for overwrites.
- Test fragile transforms, conversions, indexing, and format parsing.
- Reuse the repository's runtime and dependencies.

Keep personal paths and unexplained machine-specific helpers out of the
contribution.

## Validate proportionately

Use repository-native checks. When applicable:

1. run `git diff --check` and `git diff --cached --check`;
2. inspect the final diff, status, untracked files, and staged file list;
3. parse changed configuration and verify documentation links or commands;
4. run focused tests, dry-runs, or the smallest representative smoke test;
5. confirm the contribution contains no unrelated files or disallowed artifacts.

Separate environmental failures from defects. State whether validation covered
syntax, configuration, a smoke test, or full experiment reproduction.

## Contribute and hand off

- Work on a focused branch and keep unrelated changes unstaged.
- Verify the repository and branch immediately before any remote action.
- Do not push, open or merge a PR, create an issue, or upload data unless the
  user requested it.
- Use the established publishing workflow instead of duplicating it here.

At handoff, summarize the branch, intended diff, validation, excluded local
work, artifact handling, pending research, and next action.
