# Run a controlled comparison

Select only conditions that answer the user's question. Authoring fixtures and
interpreting existing results require no model calls. A manual decision run uses
the real tested agent and, if supported, real skill loading, but its task actions
are simulated. An execution run needs an independently verified, isolated runner
and resettable artifacts. This skill ships no such runner or provider adapter.

## Define the treatment and plan

Record the target and exact source revision, question, selected cases/versions,
conditions, repetitions, shared budgets, endpoint, and available run telemetry.
For a revision comparison, use separate fresh runs of accepted and candidate
versions in the selected available or loaded conditions. Keep the absent baseline
paired when it helps answer absolute value. Do not load both versions together.

| Comparison | What it can establish |
| --- | --- |
| Baseline / loaded | Benefit of the declared treatment when deliberately applied |
| Baseline / available | Benefit under normal discovery, including activation errors |
| Available / loaded | Possible discovery loss; attribution needs load evidence and matching controls |
| Accepted / candidate | Regression or improvement within the same condition and controls |

Choose a **complete-package** or **instructions-only** boundary explicitly.
Package tests include bundled scripts/resources and their availability overhead;
they do not isolate prose benefit. Instructions-only tests must give both sides
equivalent tool/helper capabilities, including the same script versions through
neutral access that does not expose the target instructions. If this cannot be
done, report a package comparison instead or mark the requested comparison invalid.

Inspect sibling imports before claiming ablation. For example, `publish` and
`babysit` use resources owned by `land`. Retaining a sibling that teaches the same
behavior measures incremental value within that catalog, not the absence of the
behavior. Removing it changes the treatment. State the confound or select a valid
alternative, such as a declared multi-skill package comparison. Do not quietly
vary dependencies or tools to produce a cleaner result.

Freeze the model/version, reasoning effort, harness/version, request and files,
repository instructions, non-target catalog, tools, permissions, endpoint, and
budgets across paired conditions. Record unavoidable differences, including the
native loading wrapper, cache policy, and helper access. Distinguish a target
ablation in a normal catalog from an all-skills-disabled or reduced-catalog
baseline; label them separately and do not pool their results.

## Establish isolation before launching

Use only a documented isolated configuration or root supported by the chosen
host. Record the actual configuration and evidence of what it controls. Merely
using a new worktree, fresh prompt, or different working directory is insufficient.
Do not uninstall user skills, edit global configuration, or change real junctions.

Check the target's absence in the baseline across global/inherited installs,
project and parent discovery, resolved symlink/junction targets, sibling imports,
session history, and cached instructions. Keep agreed non-target skills fixed.
In available runs, expose the target description through normal discovery and
let the agent select it. In loaded runs, use the host's documented native loading
mechanism and record the exact wrapper. Observe load events when the host exposes
them; otherwise record selection as unknown, even if the answer looks compliant.

Keep the evaluator workspace outside the tested agent's accessible surfaces.
This includes fixture rubrics, this skill's source fixtures, prior outputs,
condition/version labels, grading discussions, and held-out material. A second
directory is not sufficient when tools can read the whole filesystem. Use an
enforced allowlist/sandbox or a tool-free context receiving only released inputs.
Do not give the tested agent the evaluation repository or an evaluator skill
installation that can read the rubric. If excluding this evaluator skill changes
the agreed catalog, make the same declared exclusion in all conditions. Required
target resources must remain available without exposing evaluation material.

Record whether filesystem, network, context, catalog, and event isolation are
actually enforceable. Where required controls cannot be established, record the
condition as unsupported and stop dependent runs. A tool-free simulated decision
exercise can still be useful, but if it cannot load skills natively, label any
injected-instruction variant as a separate treatment. Do not count it as loaded
or as a native discovery test.

## Run the authorized scope

1. Freeze criteria in evaluator-only storage and allocate opaque run IDs. Assign
   paired condition order before observing outputs; counterbalance or randomize
   it where useful and record the order. Reserve held-out releases until the
   candidate is frozen. Use the same repetition count unless a difference is
   intentional and reported.
2. Reset the fixture and start a fresh context. Apply the recorded catalog and
   condition through supported controls. Submit the same neutral task packet.
   The [packet helper](fixtures.md#packet-helper) can emit inputs without rubrics;
   it does not perform these host setup steps.
3. In a simulated decision run, instruct all conditions: "Use only the supplied
   facts. Describe intended actions or patches without executing them; distinguish
   proposals from completed actions. Stop at the supplied endpoint." Reveal events
   individually when due, with a response opportunity between them. In execution,
   use actual actions/state and observed tool outputs under the runner's boundary.
4. Stop at the frozen endpoint or budget. Preserve the answer, actual tool trace
   and final artifacts where available, selection/load evidence, and telemetry.
   Record timeout, infrastructure failure, model/task failure, or unsupported
   condition distinctly. Never silently discard unsuccessful runs.
5. Grade using [interpretation guidance](interpretation.md), preferably with
   condition/version labels hidden. Keep the run-to-condition key outside the
   grader context. Record unblinding when a wrapper or output reveals the condition.

No ongoing scheduler is needed. End after the authorized set. Additional model
calls, paid grading, or exposure to another service need applicable authorization;
reuse it when already present. A missing measurement is unavailable, not zero.

## Minimal run evidence

Use the project's existing records or concise notes; no fixed report format is
required. Preserve enough to reconstruct the pairing: opaque run ID, scenario
ID/version/hash, condition and target revision, package boundary, catalog and
isolation evidence, model/effort/harness, task/tool/permission/budget controls,
order and repetition, status, output/trace references, and observed telemetry.
Keep grader evidence and the identity key separate when blinding is feasible.
For an interpretation-only request, assess the supplied record's gaps without
inventing missing facts or demanding a new run for every absent field.
