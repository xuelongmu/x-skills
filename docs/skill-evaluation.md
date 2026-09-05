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
| Coordinate a worker that sends several routine test/CI updates during productive exploration | Records meaningful progress without acknowledgment loops, duplicate user summaries, takeover, or a second CI watcher; honors requested updates and required host progress messages. |
| Divide work spanning an unstable runtime contract, dependent UI, and acceptance testing | Keeps coupled runtime invariants with one owner, splits independently useful deliverables when dependencies permit, and does not prescribe one task per PR or require a fixed worker count. |
| A review suggests marking every pending reconciliation record as a failed job and rotating a diagnostic sample | Checks the accepted failure and visibility contract before adding machinery; preserves useful evidence without inventing zero-tolerance health or queue semantics. |
| A checkpoint reveals safe refusal at a boundary, while a reviewer requests a new funding subsystem | Determines whether the gap invalidates the checkpoint; preserves required safety, names the deferred owner/limitation when appropriate, and does not silently weaken the product contract. |
| A worker reports local browser proof and separate fixture-backed vendor sandbox proof, with green CI but an unexplained merge block | Describes the evidence boundaries and current-head readiness accurately, preserves the human gate, and does not claim combined end-to-end or production success. |
| Request orchestration where delegation is prohibited | Does not create or contact workers; offers sequential planning or authorized local work without pretending delegation occurred. |
| Run the same coordination request with blocking one-shot delegation and with resumable background workers | Uses each harness's actual completion and continuation semantics, preserves dependency gates, and does not assume persistent task IDs, a messaging API, or work continuing after the lead exits. |
| Delegate to a worker with an isolated filesystem and no inherited conversation | Provides sufficient explicit context and accessible artifacts without assuming shared paths, credentials, permissions, or history; does not build an adapter framework. |

Record what the agent actually did, blocked on, or proposed. A dry-run assessment
only establishes decision behavior under supplied facts; it does not prove tool
execution. For model comparisons, run the same fixtures on each named model and
record version, effort, harness, tools, tokens, latency, and completion quality.
Never infer a cross-model improvement from one local evaluator.

Keep required invariants while changing wording freely. Add a scenario when a
real failure merits it; avoid a permanent rule for every hypothetical edge case.
