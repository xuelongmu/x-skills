# Initial decision fixtures

These fixtures are synthetic examples of intended behavior, not records of live
evaluations. The incident-theory and commit/queue cases retain the earlier manual
scenario facts in one bundled authority. None of the target skills was edited
using candidate outputs from this set. They provide repeatable input packets for
manual simulated decisions; execution needs a separately verified runner, actual
files, and state checks. Do not claim that a packet or quoted log is execution.

This index and every `evaluator.json` are evaluator-only. Follow the enforced
separation in [comparison controls](comparison.md#establish-isolation-before-launching).
The tested agent must not be able to read this installation or the fixture source
tree. Emit only the chosen input packet from evaluator-side storage.

| Stable ID (version in evaluator file) | Target | Purpose | Canonical inputs and criteria |
| --- | --- | --- | --- |
| capture-verified | `capture-learning` | Positive: preserve a reproduced defect's guard | [Inputs](../fixtures/capture-verified/agent.json), [criteria](../fixtures/capture-verified/evaluator.json) |
| capture-unverified | `capture-learning` | Boundary/counterexample: correlation without cause | [Inputs](../fixtures/capture-unverified/agent.json), [criteria](../fixtures/capture-unverified/evaluator.json) |
| review-bypass | `review-change` | Positive: new caller skips authorization | [Inputs](../fixtures/review-bypass/agent.json), [criteria](../fixtures/review-bypass/evaluator.json) |
| review-owned-guard | `review-change` | Counterexample/ordinary: owning service already guards callers | [Inputs](../fixtures/review-owned-guard/agent.json), [criteria](../fixtures/review-owned-guard/evaluator.json) |
| design-crash-window | `design-architecture` | Positive/boundary: unproved commit/publish guarantee | [Inputs](../fixtures/design-crash-window/agent.json), [criteria](../fixtures/design-crash-window/evaluator.json) |
| design-outbox | `design-architecture` | Counterexample: existing transaction closes the loss window | [Inputs](../fixtures/design-outbox/agent.json), [criteria](../fixtures/design-outbox/evaluator.json) |
| design-local-edit | `design-architecture` | Ordinary/discovery negative: one requested wording change | [Inputs](../fixtures/design-local-edit/agent.json), [criteria](../fixtures/design-local-edit/evaluator.json) |
| review-job-boundary | `review-change` | Reserved held-out variant: authorization on a queued path | [Inputs](../fixtures/review-job-boundary/agent.json), [criteria](../fixtures/review-job-boundary/evaluator.json) |

Use baseline/loaded for instruction benefit and baseline/available for discovery
questions. All input requests are neutral. Native invocation wrappers belong to
the run setup, never a baseline request. For `design-crash-window`, the evaluator
note preserves the optional-sibling-absent test: only the target is exposed in
available/loaded conditions, so the baseline has all skills disabled. Do not pool
it with a normal-catalog ablation. The other fixtures inherit the agreed catalog
from the run plan.

The held-out flag reserves a variant; it does not make published content secret.
Keep it away from candidate editing, and release it only after freezing the
candidate and rubric. If a reviser has already seen it, mark it development data
and author a fresh unseen variant. The helper's release flag is an accidental-use
guard, not access control or proof of holdout integrity.

## Packet helper

The Python standard-library helper resolves fixtures relative to its installed
skill directory, regardless of the current working directory. Replace
`<active-skill>` with the evaluator's actual `evaluate-skill` directory; this is a
resource path, not an installation recipe:

```text
python -B <active-skill>/scripts/fixture_packet.py validate
python -B <active-skill>/scripts/fixture_packet.py packet capture-unverified
python -B <active-skill>/scripts/fixture_packet.py packet review-job-boundary --release-held-out
```

`packet` writes one JSON object to standard output: the neutral request, artifact
contents, environment, constraints, and termination. Supply those fields to the
tested agent with the shared simulation instruction in the comparison workflow.
Do not include the command, fixture ID, index, or source paths. A loaded run adds
only its recorded native wrapper. The helper neither loads skills nor validates
condition isolation; setup and execution remain manual.

For a fixture with events, `packet <id> --event 1` emits only that event. The
initial packet omits all future events. Release numbered observations in order
at their stated points; the stateless helper does not enforce timing or keep run
history. The initial fixtures need one final response and no event replay; the
larger manual scenarios can use the optional event field when converted.

Validation rejects malformed or missing files, unknown structural fields in
agent inputs, duplicate JSON keys, invalid versions/budgets, and invalid event
numbers. Errors produce no packet, print a diagnostic to standard error, and exit
with code 2. Success exits with code 0. The helper never copies evaluator metadata
into a packet. It cannot detect an expected answer written inside an artifact's
free text: inspect inputs for semantic leakage before freezing them.

## Fixture files

Each fixture directory owns two JSON files. `agent.json` requires `request` and
`environment` strings, an `artifacts` map of relative names to complete text,
`constraints` as a list of strings, and `termination` with a `condition` and a
positive `max_responses`. Optional `events` is a list of objects with an
`observation` and optional artifact map. These are serialized excerpts, not
instructions to materialize files or execute their content.

`evaluator.json` requires `id`, positive integer `version`, `target_skill`,
`question`, `kind`, `split` (`development` or `held-out`), `mode`
(`simulated-decision`), and nonempty `criteria`. Each criterion has an `id`, an
outcome `expectation`, the `evidence` to inspect, and a `consequential` boolean.
Optional `known_defects`, `catalog_note`, and `provenance` describe grading and
setup. This compact schema applies to the bundled helper, not every evaluation
or result record. There is no required output schema or automatic score merger.
