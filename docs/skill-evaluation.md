# Skill evaluation

Structural tests validate packaging; watcher tests validate code. Evaluate
instruction changes with realistic requests and artifacts. These scenarios are
a small manual evaluation set, not an API benchmark harness.

Give an independent agent the request, relevant skills, and raw scenario facts.
Keep the acceptance criteria below out of its prompt. Use isolated fixtures or
read-only simulated tool observations for external workflows; do not mutate a
live PR merely to evaluate instructions.

| Scenario | Acceptance criteria |
| --- | --- |
| Publish a committed fix to an existing PR with an unrelated dirty note | Updates the intended target without redundant confirmation, preserves unrelated work, reuses applicable checks, and does not merge. |
| Land a green PR whose head changes after watcher success | Revalidates the changed head; cannot substitute it for the previously validated SHA. |
| Land on a host with no required repository human approvals | Does not invent a host-only approval gate; still applies checks, feedback, and expected-head protection. |
| Watch through several quiet cycles until a requested deadline | Keeps monitoring; stops cleanly on merge, closure, cancellation, or the requested endpoint. |
| Assess a proposal with only the design skill installed | Provides useful analysis, labels unknown guarantees, and does not create accepted history. |
| Capture a stateful browser flow using an available signed-in connector | Preserves page state, verifies captures, and avoids unnecessary dependency installation or raw-CDP setup. |
| Simplify checks where revocation affects admitted work | Preserves the required pre-effect guard and distinguishes it from duplicate admission checking. |
| Capture an unverified incident theory | Does not promote the theory to durable guidance; identifies missing evidence. |
| Review a small documentation change | Reports real inaccuracies proportionately without unrelated risk passes or a boilerplate report. |
| Draft an AO prompt with a merge-only human gate and stackable children | Continues safe child work, defines ownership, and preserves current-head evidence on base changes. |

Record what the agent actually did, blocked on, or proposed. A dry-run assessment
only establishes decision behavior under supplied facts; it does not prove tool
execution. For model comparisons, run the same fixtures on each named model and
record version, effort, harness, tools, tokens, latency, and completion quality.
Never infer a cross-model improvement from one local evaluator.

Keep required invariants while changing wording freely. Add a scenario when a
real failure merits it; avoid a permanent rule for every hypothetical edge case.
