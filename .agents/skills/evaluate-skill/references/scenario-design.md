# Design a useful scenario

Start with a question about an outcome: does the instruction prevent a known
failure, improve an ordinary task, or impose unnecessary work? Derive facts from
verified incidents, recurring workflow failures, intended behavior, and typical
work. Preserve provenance and uncertainty. A suspected incident cause can test
whether the agent recognizes missing evidence; it cannot establish that cause.

Give each runnable case a stable ID and version. Change the version when task
facts, constraints, grading, or termination change. Record source and fixture
hashes in the experiment so an unchanged ID cannot conceal changed inputs.
Keep only fields that serve the case:

| Evaluator-controlled material | Agent-facing material |
| --- | --- |
| ID/version, target skill, question, case kind, development or held-out split | Neutral request with the same substantive task in every condition |
| Frozen criteria, known defect IDs and severity, expected state/actions | Initial files or complete excerpts, repository instructions, capabilities and observations |
| Treatment, catalog and runner setup, condition labels, grading notes | User constraints and permissions, termination condition and budget |
| Future events until their release point | Only the next observation when it becomes available |

For explicit-invocation cases, remove the skill invocation to obtain the neutral
request. Apply the host's actual loading wrapper only in the loaded condition.
Do not rewrite the task to help one condition. Keep evaluator hints out of file
names, artifact comments, test names, and requests as well as the prompt body.
Real requirements are valid agent inputs; expected diagnoses are not.

## Cover both benefit and harm

Choose a small set appropriate to the requested claim, including:

- Positive cases with a concrete completion obligation, so refusing everything
  cannot pass: a reproduced defect needs a durable guard, or a new caller skips
  an authorization boundary.
- Counterexamples: recovery after a restart does not prove a leak; a service
  already checks authorization; a transaction already persists an outbox record.
- Ordinary work where extra process adds no value, such as a precise local edit.
- Boundaries where useful incomplete analysis is correct because a guarantee,
  artifact, or permission is absent. Grade useful progress as well as honesty.
- Discovery negatives where the target should stay inactive. These principally
  compare baseline and available; a forced load tests restraint, not discovery.
- Held-out variants reserved from candidate editing. Freeze the candidate and
  criteria before releasing them. A published fixture is only held out if its
  contents have actually stayed out of that candidate's development context.

The [initial fixtures](fixtures.md) cover learning, review, and architecture.
Visual advice is worth testing only when the relevant instructions are actually
available: pair an interaction explanation that benefits from a diagram with a
local change best explained briefly. Grade understanding and usefulness, not the
existence or count of diagrams. Do not add an imaginary visual skill to a catalog.

## Grade outcomes

Define observable success and consequential violations before running. Prefer
final state or behavior over exact language, section headings, tool sequence,
number of findings, documentation volume, or refusal. Accept equivalent repairs
and sound alternatives. A clean review or no durable learning can be correct;
the paired positive case still requires the agent to complete useful work.

For reviews, name each known defect privately and its concrete trigger. Count a
miss only when the defect is known and in scope. Count false positives against
the supplied contract and guards, with evidence; do not assume every unexpected
finding is false. Resolve a newly discovered real issue before scoring the case.
If the case was wrong, version its criteria and report the invalidated comparison
rather than moving the goalposts to favor a candidate.

For execution, supply resettable initial files and deterministic checks where
possible. For simulation, supply sufficient excerpts and observations to judge
the intended action without invented tool results. Do not label hypothetical
commands, quoted test logs, or fabricated screenshots as executed evidence.

Freeze a bounded endpoint: final answer, specified artifact state, terminal event,
or inability to proceed plus a common response/token/time budget. Keep required
events in order and withhold future events even if a worker asks for them early.
When an observation needed beyond the fixture is missing, end with a recorded
gap; do not improvise a success. Use the same endpoint policy in each condition.

Keep development results available for authorized revisions, and keep held-out
outputs and criteria away from the reviser. Once a held-out case has been used
to edit the skill, it is development data. Reserve a new unseen variant before
the next validation; do not run an automatic rewrite/retest loop against it.
