---
name: evaluate-skill
description: Author skill evaluation scenarios, compare outcomes with a skill absent, discoverable, or loaded, and interpret evidence for keeping or revising it. Use for evaluating skill value or regressions, not ordinary product testing or reviewing a change.
---

# Evaluate a skill's contribution

Answer whether the skill improves the requested outcomes enough to justify its
instructions and overhead. Match the work to the request: authoring scenarios,
running an existing comparison, assessing a revision, and interpreting recorded
results are independent entry points. Do not force a full experiment when only
one part is requested.

## Choose the relevant work

- To create or repair cases, read [scenario design](references/scenario-design.md).
  Reuse verified facts and freeze outcome criteria before examining candidate
  outputs. The [fixture index](references/fixtures.md) provides a small manual
  decision set and a packet helper, not measured execution results.
- To run a comparison, read [comparison controls](references/comparison.md).
  Establish the treatment, relevant conditions, isolation, and a bounded run
  scope before using the host's actual capabilities.
- To assess a revision, include the accepted or published version as well as the
  candidate under the same controls. Preserve counterexamples and reserve
  held-out cases for validation after the candidate and criteria are frozen.
- To interpret results, read [grading and interpretation](references/interpretation.md).
  Use observable evidence, including failures and costs; do not rerun or rewrite
  a skill merely because results were supplied for analysis.

## Preserve the experiment

Use only the conditions needed to answer the question:

| Condition | Intended difference |
| --- | --- |
| Baseline | Target skill absent; agreed repository instructions, non-target skills, tools, facts, and permissions unchanged. |
| Available | Same natural-language task; target exposed through normal discovery. |
| Loaded | Same substantive task; target explicitly loaded through a supported host mechanism. |

Baseline versus loaded estimates instruction benefit under the declared treatment
boundary; baseline versus available includes discovery in practical benefit.
Available versus loaded can diagnose discovery loss when load evidence supports
that explanation. Never ask the baseline to use the missing skill. Record native
invocation wrappers as a condition difference; pasting instructions is an
instruction-injection experiment, not native loading.

Use fresh contexts and reset fixture state. Keep evaluator criteria, future
events, prior outputs, other conditions, and grading discussions inaccessible to
the tested agent, including through its filesystem and skills. An omitted prompt
is not isolation. Do not alter the user's global skill installation to construct
a baseline. If a supported isolated root or configuration cannot enforce the
needed separation, mark that condition unsupported.

Distinguish manual simulated decisions from executed actions and final state.
The bundled helper validates and emits fixture inputs; it neither isolates a
host nor launches models, grades outputs, or proves skill discovery. No isolated
live runner is bundled. Use an execution mode only when its concrete runner and
isolation have been verified for the requested host.

Reuse the user's authorization. Before a run, make material scope, repetition,
external data exposure, and cost clear when relevant; ask only for missing
authority or consequential unresolved constraints. Evaluation does not implicitly
authorize workers, paid calls, external writes, publishing, or changes to skills.
A request that includes improvement can authorize scoped local revisions.

## Close the learning loop

Connect observed failure to a candidate scenario, verified learning or proposed
revision, controlled evaluation, and an accepted improvement. An observation,
repetition, or lack of user correction does not establish correctness. When
available, `capture-learning` can help put a verified invariant in its owning
test, contract, runbook, or skill; its absence does not block evaluation.
Project constraints stay with the project. Only justified reusable methods
belong in a shared skill; do not automatically promote observations into global
guidance or create a memory database.

Return a concise **keep**, **revise**, **simplify**, **remove**, or **inconclusive**
recommendation, with evidence, regressions, costs, and limits scoped to the tested
cases, models, and harnesses. Suggest the next useful experiment only when it
resolves a remaining decision. Do not accept architecture, rewrite unrelated
skills, create external records, or publish as a side effect of evaluation.
For the borrowed concepts and deliberate departures, see
[sources and adaptations](references/sources.md).
