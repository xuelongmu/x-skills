# Grade and interpret the evidence

Evaluate the user's outcome against frozen criteria, not compliance with the
skill's wording. Prefer deterministic checks of executable invariants and final
artifact state. A test that only matches prose or a helper's implementation is
not behavioral proof. Keep those structural checks separate from task grading.

For architecture, review, or other qualitative judgments, hide condition/version
labels and prior conclusions when feasible. Give the grader the neutral task,
released observations, candidate output or artifacts, and frozen rubric. Record
whether blinding succeeded. Do not ask a grader to infer the condition, and do
not treat an agent's self-rating as evidence. Every judgment should cite an
observable action, artifact location, trace event, or output passage.

Preserve meaningful grader disagreement and uncertainty. A newly identified real
defect is not automatically a false positive. Seek human interpretation for
ambiguous high-impact judgments rather than converting disagreement into an
arbitrary confidence number. Regrading changed criteria requires a new version
and consistent regrading of paired outputs, with the change disclosed.

## Keep dimensions visible

| Dimension | Evidence to retain when applicable |
| --- | --- |
| Completion and correctness | Criteria met, failed, or unknown; resulting artifact/state or proposed decision |
| Consequential violations | Each violated authorization, safety, data, or other accepted invariant, separately from any aggregate |
| Review quality | Known defects found/missed by ID and substantiated false positives; no reward for finding count alone |
| Friction | Unnecessary blocking, scope expansion, extra user interventions, duplicate checks, or other observed overhead |
| Discovery | Observed selection/load event, observed absence, or unknown; separate from behavior after loading |
| Resources | Measured tokens, latency, tool calls, and cost, with units and scope; unavailable fields stay unavailable |
| Run status | Completed, timed out, infrastructure/runner failure, model/task failure, unsupported, or missing result |

A task can finish with a justified incomplete or inconclusive answer when the
fixture withholds a required fact. A model refusal or an unnecessary question
on a fully specified positive case is a failure of completion. Infrastructure
failure is not proof of model failure, but remains visible in the planned-run
denominator. Do not silently drop timeouts, missing results, or failed runs.
Any rerun gets a new run ID and retains the original outcome.

Use artifact checks for executable claims. For simulations, grade what the agent
proposed and its reasoning boundaries, not whether an imaginary command passed.
Quoted fixture logs are supplied facts, not fresh telemetry. If cost is estimated
from measured tokens, name the price schedule and calculation and label the cost
as estimated. Do not estimate missing tokens or treat missing latency as zero.

## Compare paired outcomes

Pair by scenario/version, repetition, and shared controls. Report sample size,
planned/attempted/completed runs per condition, and pairwise wins/ties/losses.
Define preference before grading: consequential violations dominate; then compare
completion/correctness; use friction or resource savings only when outcomes are
otherwise equivalent. If dimensions conflict or evidence is missing, mark the
pair unresolved rather than forcing a tie. Include unresolved pairs alongside
the wins/ties/losses denominator. Show severe failures even if the average improves.

For example, five planned pairs might yield two wins, one tie, one loss, and one
unresolved pair because a runner failed. Report all five and the runner failure;
do not describe the candidate as winning two of three selected runs. For loaded
versus available, an outcome gap with unknown loading is not proof of a discovery
defect. Compare observed activation separately, including inappropriate activation
on discovery negatives.

Use repeated independent runs when authorized to inspect variability. A small
pilot is directional evidence scoped to its cases, model, and harness, not a
statistical claim or cross-model validation. Independent repetitions start fresh
and receive no earlier feedback. Retries that see feedback or revised instructions
are a different treatment, even when the final attempt succeeds.

Prefer raw paired outcomes to advanced metrics for small sets. If pass@k is
needed, define it as the probability of at least one success among k independent
attempts for the same task. With n independent attempts and c successes, the
usual estimator is `1 - C(n-c, k) / C(n, k)` for `1 <= k <= n`, taking
`C(n-c, k) = 0` when `n-c < k`. Compute per task before aggregating with stated
weights. It is not the ordinal number of the successful retry and does not apply
to attempts that incorporated prior feedback. All-k success is a different
quantity. If reporting uncertainty intervals, state the estimand, sampling unit,
method, assumptions, and confidence level; use the paired structure and do not
pretend repeated runs create more independent scenarios. Omit intervals that the
available sample and design cannot support.

## Make the decision

Recommend keep, revise, simplify, remove, or inconclusive with evidence and scope.
Keep when benefit survives relevant counterexamples at acceptable overhead;
revise when intended benefits coexist with fixable regressions; simplify when
less instruction preserves the benefit; consider removal when the tested skill
adds no value or harms outcomes. An unsupported runner or a tiny mixed pilot
usually supports an inconclusive result, not a claim that the skill never helps.

Name material regressions, costs, and limits before proposing a next experiment.
Choose the smallest experiment that could change the decision. Evaluation alone
does not authorize editing, acceptance, or publication. When improvement is
requested, route verified reusable learnings to their owning authority and test
the proposed revision against frozen development cases plus an untouched held-out
set. Do not upgrade repeated observations or user silence into accepted rules.
