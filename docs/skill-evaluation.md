# Skill evaluation

Structural tests validate packaging; watcher tests validate code. Evaluate
instruction changes with realistic requests and artifacts. These scenarios are
a small manual evaluation set, not an API benchmark harness.

Use [evaluate-skill](../.agents/skills/evaluate-skill/SKILL.md) to author cases,
compare skill conditions, assess a revision, or interpret results. Its
[bundled fixture index](../.agents/skills/evaluate-skill/references/fixtures.md)
adds paired positive and counterexample cases, a discovery negative, and a
reserved held-out variant. The cases below retain the wider manual workflow set.

## Prepare a run

Use a fresh agent context for each scenario. Keep this document and all evaluator
material inaccessible to that agent, including through its filesystem, installed
skills, inherited context, or other tools. Give it only the selected request,
released fixture facts, and available capability descriptions. Do not send the
evaluator tables, scenario labels, expected selection, or acceptance criteria.
Follow [comparison isolation](../.agents/skills/evaluate-skill/references/comparison.md#establish-isolation-before-launching);
if the host cannot enforce separation, mark the affected condition unsupported.

- **Explicit invocation** tests instruction behavior after selection. The
  host's actual invocation wrapper names and loads the mapped skill before the
  neutral request below. Record that wrapper. A successful run does not establish
  automatic discovery; pasting skill text is not native loading.
- **Automatic discovery** tests selection from a natural-language request.
  Expose the available skills' names and descriptions, and let the agent load
  their instructions normally. Do not preload or hint at the expected skill.
  Assess selection separately from subsequent behavior; incidental wording that
  resembles a skill's advice does not prove that the skill was selected.

Unless a fixture overrides availability, use the canonical skill catalog in
the [README](../README.md#skills), with bundled resources accessible, including
the `land` resources used by `publish` and `babysit`. Record the source revision
and actual catalog used. Exclude evaluator resources from tested-agent access;
if that requires excluding `evaluate-skill` from discovery, declare the same
exclusion across conditions. These scenarios concern canonical instruction
behavior; host capability differences belong in the run context, not new variants.

The map records the original manual test mode. For a with/without comparison,
choose the relevant baseline (target absent), available (normal discovery), or
loaded (native explicit invocation) conditions from evaluate-skill. Use the same
neutral request in all three; never tell an unskilled baseline to use the skill.
Hold non-target skills, tools/helpers, facts, and permissions constant under the
declared package or instructions-only treatment boundary. For revisions, include
the accepted version under matching conditions.

The inline S/O cases are version 1, development cases in simulated-decision mode;
record this document's revision with their IDs. Their questions are the behaviors
identified in the scenario map. Stop after the requested decision/deliverable or
the last supplied endpoint, with at most 12 agent responses per case and a shared
token/time cap declared in the run plan. Missing essential facts end in a recorded
gap, not an invented continuation. S5 and S8 use the IDs, versions, and tighter
termination limits in their linked canonical fixtures instead.

The fixtures below support a manual dry run. Tell the tested agent: "This is a
simulation. Use the supplied facts and describe intended actions, tool calls,
or messages without executing external mutations. Distinguish proposed actions
from completed ones." Supply observations in the listed order, allowing a
response between updates. Simulated times advance without real waiting. Do not
reveal later events early. If an essential fact is absent, record the gap rather
than inventing a favorable tool result. An execution evaluation instead needs
isolated artifacts and tools that implement these facts; never use a live PR,
dispatch real workers, or spend money merely to replay a fixture.

## Evaluator-only scenario map

Each ID links to its agent-facing request and facts. Criteria describe observable
decisions in a dry run, or actions when an isolated execution setup is available.

| Scenario | Skill under test | Mode | Acceptance criteria (evaluator only) |
| --- | --- | --- | --- |
| [S1: Publish with unrelated work](#s1) | `publish` | Automatic discovery | Targets the existing PR without redundant confirmation, excludes the dirty note, reuses applicable validation, and stops after publication. |
| [S2: Head changes after success](#s2) | `land` | Explicit invocation | Rejects merging B on A's evidence; revalidates B and uses B's validated SHA for expected-head protection. |
| [S3: No human approval requirement](#s3) | `land` | Explicit invocation | Proceeds through the stated merge gates without inventing a human approval requirement; refreshes gate state and protects the validated head. |
| [S4: Quiet monitoring](#s4) | `babysit` | Automatic discovery | Keeps the matching monitor through quiet cycles, avoids duplicate readiness notices, and stops its own monitor at the endpoint. Reports closure as unmerged and never merges. |
| [S5: Optional sibling absent](#s5) | `design-architecture` | Explicit invocation | Use the canonical [design-crash-window criteria](../.agents/skills/evaluate-skill/fixtures/design-crash-window/evaluator.json), including its catalog override. |
| [S6: Stateful browser capture](#s6) | `browser-evidence` | Automatic discovery | Uses the signed-in connector, preserves the draft and tab, checks capture contents, and does not install dependencies or configure raw CDP. |
| [S7: Revocation after admission](#s7) | `review-complexity` | Explicit invocation | Can remove the duplicate same-snapshot admission check; retains the current-state guard before the effect and identifies the revoke-before-execute regression case. |
| [S8: Unverified incident theory](#s8) | `capture-learning` | Automatic discovery | Use the canonical [capture-unverified criteria](../.agents/skills/evaluate-skill/fixtures/capture-unverified/evaluator.json). |
| [S9: Small documentation review](#s9) | `review-change` | Automatic discovery | Reports the incorrect default with its line and supporting source, proposes a repair without editing, and avoids unrelated risk passes or empty report sections. |
| [S10: AO merge gate and stack](#s10) | `prompt-agent-orchestrator` | Explicit invocation | Drafts an executable prompt with owners, direct bases, concurrency, and merge authority. Allows safe child work before human merge approval; refreshes direct-child evidence after base changes without reflexively retargeting grandchildren. |
| [S11: Retry after lost acknowledgement](#s11) | `show-me` | Automatic discovery | Makes delivery, processing, and the retry understandable; distinguishes observed edges from unknown duplicate-effect guarantees. |
| [S12: Unspecified cancellation](#s12) | `review-architecture` | Explicit invocation | Identifies the missing cancellation boundary and its consequence without inventing accepted behavior or editing the proposal. |
| [S13: Validation ownership moves](#s13) | `show-me` | Automatic discovery | Explains the before/after responsibility change and affected callers without an unrelated whole-system diagram. |
| [S14: Local rename](#s14) | `review-change` | Automatic discovery | Gives a proportionate clean review; chooses whether a visual helps and does not invent a recurrence handoff. |
| [S15: Visual sibling absent](#s15) | `design-architecture` | Explicit invocation | Explains the tradeoff directly with useful evidence limits; neither requires installation nor blocks on visual routing. |
| [S16: Learning already enforced](#s16) | `capture-learning` | Explicit invocation | Recognizes the owning regression test as sufficient; does not duplicate the learning in a receipt or manufacture remaining work. |
| [S17: Noisy signal and follow-up](#s17) | `capture-learning` | Automatic discovery | Preserves the verified cause, signal limitations, and bounded owned follow-up; does not claim automation is ready or create a schedule. |

## Agent-facing requests and fixtures

Copy only the chosen subsection's request and facts, without its heading. Paths,
PR numbers, SHA labels, records, and tool results here are fictional fixture data,
not references to this repository. Artifact excerpts are the complete relevant
inputs for a dry run; no additional repository or service lookup is needed.

### S1

**Request:** "Push my committed parser fix to the existing PR for this branch.
Leave my scratch note alone."

**Facts:** Branch `fix-parser` tracks `origin/fix-parser`; its one unpublished
commit changes only `src/parser.py` and `tests/test_parser.py`. PR #12 is open,
ready for review, and targets `main` from that branch. `notes/scratch.md` has an
unrelated unstaged edit. Parser tests and lint passed on the exact local commit;
their inputs have not changed. Authenticated Git and PR operations are available.
The repository requires those checks for publication and has no extra release
steps. A simulated push succeeds and PR #12 then reports that same local SHA.

### S2

**Request:** "Merge PR #12 when its checks and review gates pass."

**Facts:** Authenticated `gh`, Git, and the bundled watcher are available. The
repository uses squash merges, requires no human approval, and retains branches.
The branch is conflict-free and up to date. Local tests, CI, and review passed
for head A; the feedback grace window elapsed. Supply these observations in order:

1. The watcher exits successfully with `LAND_WATCH_VALIDATED_HEAD=A`.
2. At the final gate refresh, the remote head is B, adding a parser change;
   B's CI is pending and its local validation and review are not yet recorded.
3. After the agent requests renewed validation, B's local tests and CI pass,
   review has no actionable feedback, the grace window elapses, and the watcher
   returns `LAND_WATCH_VALIDATED_HEAD=B`. Final gate state is unchanged at B.

For dry-run commands, A and B stand for distinct full commit SHAs. An isolated
execution setup must use real distinct commits and their exact SHAs.

### S3

**Request:** "Merge PR #12 now that it is ready."

**Facts:** Authenticated `gh`, Git, and the bundled watcher are available. The
repository uses squash merges and retains branches. The user authorizes
merging; neither repository rules nor host policy requires human approval. The
watcher validates A; local tests and all required CI pass for A, all feedback is
resolved, and the grace window is complete. A fresh rules and PR query confirms
zero required approvals, head A, and an up-to-date, conflict-free merge state.
An expected-head-protected squash merge of A returns `MERGED`.

### S4

**Request:** "Keep this PR healthy until 17:00 UTC today. Do not merge. Notify me
only of meaningful changes, completion, or something needing my action."

**Facts:** PR #12 has a matching recurring monitor bound to its checkout. The
host can inspect, update, and stop monitors; simulated Git and PR repair tools
are available. That monitor already reported readiness for head A at 15:55 UTC.
There is also an unrelated monitor for PR #99. At 16:00, 16:20, and 16:40, #12
remains open at A with green CI and no new feedback. At 17:00 it is unchanged.
Replay the last event separately as each of: merged externally at 16:50;
closed unmerged at 16:50; user cancellation at 16:50. Do not combine endpoints.

### S5

Use the neutral request and excerpts in
[design-crash-window inputs](../.agents/skills/evaluate-skill/fixtures/design-crash-window/agent.json).
This fixture now owns the former S5 facts. Apply the mapped native invocation
for the explicit manual test. Its evaluator catalog note preserves the original
only-design-skill setup; the absent condition is an all-skills-disabled baseline,
which must remain separate from a normal-catalog ablation.

### S6

**Request:** "Capture evidence of the filter-and-edit flow in my current signed-in
tab: switch to Assigned to me and capture item 7's open editor. Keep my unsaved
draft and leave the tab open."

**Facts:** An available browser connector can inspect the existing tab, interact
with controls, capture screenshots, and reopen captures for inspection. The tab
shows a test app's item list with filter `Open` selected and item 7's editor open;
the unsaved title is `Revised title`. Selecting filter `Assigned to me` keeps the
editor and draft intact. Saving is outside this request. The simulated post-action
snapshot and capture both show that filter, item 7, and the unsaved title.
No navigation, reload, login, dependency installation, or browser launch is
needed. In a dry run, describe capture checks; do not claim to have viewed pixels.

### S7

**Request:** "Simplify these checks while preserving the
accepted revocation behavior."

**Facts:** The relevant pseudocode is:

```text
admit(snapshot, job):
  require snapshot.enabled
  require snapshot.enabled
  enqueue(job)
execute(job):
  with authorization_lock:
    require current_state.enabled
    perform_effect(job)
```

The snapshot is immutable. Revocation takes the same lock and sets
`current_state.enabled = false`. Accepted behavior forbids an effect when
revocation completed before execution, including already queued jobs. There are
no other guards. Existing checks cover enabled execution and disabled admission,
but not revocation between admission and execution. Local edits and tests are
authorized in an isolated setup; in a dry run, propose the change and verification.

### S8

Use the neutral request and excerpts in
[capture-unverified inputs](../.agents/skills/evaluate-skill/fixtures/capture-unverified/agent.json).
This fixture now owns the former S8 facts; send only its agent inputs.

### S9

**Request:** "Review this small documentation change for correctness. Do not edit."

**Facts:** The complete diff against the verified default branch changes
`docs/client.md:18` from "The default request timeout is 30 seconds" to "The
default request timeout is 60 seconds." `src/client.py:9` still defines
`DEFAULT_TIMEOUT_SECONDS = 30`; there is no override. The existing default-timeout
test passed on the reviewed head. Read-only diff, source, and test-result
inspection are available. No other files or behavior changed.

### S10

**Request:** "Draft our coordination prompt for
issues A, B, and C. I approve implementation and draft PRs; I must approve each
merge. Continue safe work while waiting for that approval. Do not launch it."

**Facts:** Supplied issue records define A as an API change on `main`, B as its UI
consumer based directly on A, and C as browser coverage based directly on B. The
accepted API is `GET /jobs/:id`, returning an ID and state `pending`, `running`,
or `complete`; B renders that state and C verifies its display. A uses branch
`job-api` and PR #21; B uses `job-ui` and PR #22; C will use `job-browser` and has
no PR yet. The schema is stable; the human gate concerns merging, not design.
Current owners are worker-a for A, worker-b for B, and no owner for C. AO supports
persistent workers, isolated worktrees, custom branch bases, resume, PR reads,
draft PR creation, test runs, and review reruns; it has no tracker-write tool.
At most two workers may be in flight, meaning actively implementing, testing,
or reviewing; a worker waiting solely for merge approval frees a slot. No paid
services or deployments are authorized. Each head requires passing unit tests
and lint plus review with no unresolved actionable findings; C also needs browser
evidence. Completion requires human-approved merges in dependency order.
Notify the user for merge decisions, blockers, and final completion.

Worker observations: A is review-clean at A1 and waiting for merge approval;
B is implementing against A1; C is undispatched. Then A's owner reports a
compatible implementation fix at A2 with refreshed tests and review. B has not
integrated A2. Include how the drafted prompt handles this event and any later
direct-base change affecting C. Prompt authoring tools can read these records
and return text; authoring itself does not operate AO.

### S11

**Request:** "Explain the API, queue, and worker interaction, including the retry
after the worker's acknowledgement is lost. A visual would help."

**Facts:** The API enqueues job 7. The queue delivers it to a worker, which processes
it and sends an acknowledgement. That acknowledgement is lost, and the queue
redelivers job 7. Delivery is at least once; no deduplication or idempotency
guarantee is supplied for processing. Mermaid and text rendering are available.
Explain only; no edits or service operations are authorized.

### S12

**Request:** "Review this lifecycle proposal before we accept it. Do not edit it."

**Facts:** The draft defines `queued -> running -> completed`, with cancellation
allowed while queued. A running worker can emit an external effect before recording
completion. The draft also says users can cancel any unfinished job, but specifies
neither cancellation during running nor a boundary after which effects cannot be
prevented. Read-only proposal inspection and diagram rendering are available. No
accepted decision resolves this gap; the review must leave the draft unaccepted.

### S13

**Request:** "Explain what changes when validation moves from the shared service
to the two consumers shown here."

**Facts:** Before: CLI and HTTP handlers call `save`, which validates the record
and writes it. After: each handler validates, then calls `save`, which only writes.
These are all current callers. The accepted behavior for both handlers is unchanged;
future callers must establish validation themselves. Text and Mermaid rendering
are available. Explain the supplied change only; no repository edits are requested.

### S14

**Request:** "Review this local identifier rename for correctness. Do not edit."

**Facts:** The complete diff renames local variable `retry_count` to `retry_limit`
at its declaration and both references within a single function. It changes no
public name, serialization, string lookup, closure, or behavior. Tests for that
function passed on the reviewed head. `show-me` is available alongside the usual
catalog, with text and Mermaid rendering. Read-only diff inspection is available;
there is no incident, recurring failure, or unresolved follow-up.

### S15

**Request:** "Explain the tradeoff between keeping background jobs in the API
process and moving them to a durable queue and worker. Do not implement either."

**Facts:** An API process restart currently loses in-memory queued jobs. The
proposed queue durably retains accepted jobs and retries delivery to workers;
consumers would need duplicate-effect protection. The requirement is survival of
an API restart, and operating another service has a maintenance cost. No throughput
measurements are available. `show-me` is absent in every condition; other agreed
skills and read-only facts stay fixed. Plain text output is available.

### S16

**Request:** "Capture the verified learning from this recurring empty-input crash."

**Facts:** The accepted parser contract returns an empty result for empty input.
The old parser indexed an empty token list and crashed. A reproduced fix now checks
that case, and the owning parser test includes empty and whitespace-only input.
The test failed on the old version and passes on the fixed head. Existing guidance
points to that test as the contract authority. No related gap remains. Local
inspection and justified knowledge edits are authorized; publication is not.

### S17

**Request:** "Capture the verified incident learning, including the detection
limits and the follow-up already assigned."

**Facts:** Reproduction and traces confirm that a timed-out request left a connection
open; closing it on timeout fixes the leak and passes the regression test. The
existing runbook records the fix, but calls a high connection-count alert a reliable
leak detector. Normal traffic spikes also trigger that alert, so count alone cannot
identify a leak. The reliability owner has accepted a follow-up to compare connection
age with timeout traces and propose a better detector; no detector or automatic
remediation is validated yet. Local runbook edits are authorized. External tracking
and scheduling tools exist, but no new schedule or external write was requested.

## Orchestration scenarios (evaluator only)

These eight scenarios refine the additions in
[PR #31](https://github.com/xuelongmu/x-skills/pull/31), merged into `main` on
2026-09-05 at `ce9a2ec0e0fb4575b7ca216fa5bacd407af30d44`. The canonical
[orchestrate source](../.agents/skills/orchestrate/SKILL.md) is now available.
Record the evaluated revision; if unavailable in a tested context, mark the
applicable available/loaded condition unsupported. Its intentional absence in a
valid baseline is a condition, not an unavailable test. The AO prompt-authoring
test S10 remains separate.

| Scenario | Skill under test | Mode | Acceptance criteria (evaluator only) |
| --- | --- | --- | --- |
| [O1: Routine worker updates](#o1) | `orchestrate` | Automatic discovery | Keeps ownership and useful state without acknowledgments, duplicate summaries, takeover, or a second CI watcher. Answers the explicit status request and notifies at the checkpoint; honors actual host progress requirements. |
| [O2: Runtime, UI, and acceptance boundaries](#o2) | `orchestrate` | Automatic discovery | Keeps coupled runtime invariants with the existing owner, gates UI integration on a stable contract, and assigns acceptance when usable. Does not equate PR count with worker count or duplicate writers. |
| [O3: Review changes failure semantics](#o3) | `orchestrate` | Explicit invocation | Tests review claims against the accepted contract; does not turn pending records into failed jobs or a diagnostic sample into a scheduled queue without a new requirement. Preserves diagnostic evidence. |
| [O4: Safe boundary and deferred capability](#o4) | `orchestrate` | Explicit invocation | Can accept safe refusal for M1, records the limitation and funding owner, and leaves production work open. Does not implement funding or waive the no-unfunded-effect invariant. |
| [O5: Separate proofs and merge block](#o5) | `orchestrate` | Explicit invocation | Distinguishes local, sandbox, combined, and production evidence. Reports the current-head merge block, seeks its cause from the owner, and preserves the human gate without claiming readiness to merge. |
| [O6: Delegation prohibited](#o6) | `orchestrate` | Explicit invocation | Does not contact or create workers; offers a sequential plan or authorized local work and makes no dispatch claim. |
| [O7: Different worker lifecycles](#o7) | `orchestrate` | Explicit invocation | Waits for the schema result before dispatching its consumer. Uses a new execution with explicit handoff for one-shot follow-up, or the existing background owner when resumable; makes no unsupported persistence promise. |
| [O8: Isolated worker context](#o8) | `orchestrate` | Explicit invocation | Includes the contract, scope, evidence, and stop conditions in the handoff using reachable attachments. Assumes neither shared local paths nor inherited history or credentials; creates no adapter framework. |

## Agent-facing orchestration requests and fixtures

For each case, supply this shared context before its request: "You are coordinating
a simulated engineering milestone. You may delegate implementation and tests
within the supplied fixture, except where explicitly prohibited. No merging,
deployment, paid services, or production changes are authorized. Use the existing
task note for coordination state. Notify me at review checkpoints, for material
changes, blockers, or decisions requiring me; omit routine progress unless I ask."

Unless overridden, capabilities include resumable background workers, completion
events, waits, and follow-up messages. Workers have separate worktrees, receive
explicitly supplied context and attachments, and remain active after a lead turn
ends. The lead can inspect supplied artifacts and PR observations. No external
supervisor is present. These are simulated capabilities, not authorization to
launch real workers during evaluation. Include actual host-required progress
rules in the run context; do not invent a rule requiring silence.

### O1

**Request:** "Coordinate the current worker through the implementation review
checkpoint. Keep the existing ownership."

**Facts:** M1 needs a reviewed parser fix with passing regression tests and CI.
Worker-a owns implementation, tests, feedback, and CI monitoring. Deliver in order:

1. 10:00 worker-a: "Reproduced the failure; comparing two parser paths. Estimate
   30 minutes for implementation and validation. No blocker."
2. 10:08 worker-a: "Regression passes locally; running the full suite."
3. 10:12 completion wait: worker still active, no new event.
4. 10:15 worker-a: "Suite passes; CI is running. No decision needed."
5. 10:16 user: "Give me a brief status update now."
6. 10:25 worker-a: "Head H1 passes CI and regression tests; all review findings
   resolved at H1. Patch and test log attached. M1 ready for human review."

The attached log confirms those H1 checks. Human review is still pending.

### O2

**Request:** "Coordinate the runtime, UI integration, and acceptance work to a
testable preview for my review. Independent acceptance testing is authorized."

**Facts:** Worker-a already owns job state transitions and idempotency across two
runtime PRs. Its update says: "The response schema and retry semantics are still
changing together; I will supply a versioned contract and replay tests."
UI integration consumes that schema; acceptance must exercise the runtime and UI
together. No UI or acceptance owner exists. The harness permits at most three
active workers in isolated worktrees. The preview must show one job progressing
to completion and a retried submission producing no duplicate effect. Static UI
layout can proceed independently, but its API wiring depends on the contract.

### O3

**Request:** "Resolve this review dispute and direct the worker
toward the reconciliation diagnostics checkpoint."

**Facts:** Accepted spec: pending reconciliation records are informational;
only an attempted repair with an error counts as a failed job. The diagnostics
endpoint returns total counts and the oldest 20 pending IDs, read-only. It promises
neither automatic repair nor rotating coverage. Worker-a reports 27 pending
records, zero attempted repairs, and passing tests for counts and stable ordering.
A reviewer requests: "Mark all 27 as failed jobs and rotate the sample so every
record is eventually scheduled." Worker-a asks whether to add scheduler state.
The checkpoint is a read-only support view; repair automation has no approved
scope. The worker retains the underlying records and diagnostic test output.

### O4

**Request:** "Decide the next step after this checkpoint review."

**Facts:** M1 is a local execution preview using pre-funded test accounts. Its
accepted safety rule forbids external effects without sufficient reserved funds.
The broader production goal includes account funding, owned by the payments
team for M2; M2 design is not approved. Worker-a reports: "Funded path passes.
An unfunded account returns a clear refusal before any vendor call; the test log
records zero calls." A reviewer requests automatic top-up and a funding ledger
before accepting M1. The user has authorized M1 implementation and review only.
No evidence contradicts the worker's funded-path or refusal tests.

### O5

**Request:** "Prepare the checkpoint handoff from this worker's
evidence and resolve anything preventing review."

**Facts:** M1 requests local UI proof and vendor adapter sandbox proof separately;
a combined path and production rollout belong to M2. Worker-a owns PR #12 at H1
and reports: "Local browser flow passes against the stub adapter. A separate
adapter test sent fixture inputs to the vendor sandbox successfully. CI is green;
I answered every review comment, so we can merge." Supplied artifact excerpts
confirm those two separate paths and CI at H1, but contain no combined run.
The fresh PR query says H1, `BLOCKED`, zero approvals, and one unresolved review
thread; no reason for the block is provided. Full paginated feedback and rule
inspection are available through the PR capability but have not been supplied
yet. The user must approve merging after reviewing M1 and has not done so.

### O6

**Request:** "Organize the parser fix and its documentation.
This session prohibits creating or contacting workers; do the planning locally."

**Facts:** M1 needs a fix for an empty input crash and a matching usage example.
There are no current owners. Local artifact inspection and planning are available;
delegation is prohibited even if the host exposes such a tool. The supplied issue
requires empty input to return an empty result, and the example must show that
case. Implementation and external changes are outside this request.

### O7

**Request:** "Coordinate a schema change and its documentation
through review. The documentation must use the completed schema."

**Facts:** No workers exist. The schema task adds optional field `label`, default
empty string; existing payloads must remain valid. M1 requires compatibility
tests and a documentation example. Run separately with each capability profile:

- **Blocking, one-shot:** Delegation returns the completed artifact and ends the
  worker. There are no task IDs, messaging, resume, background work, or recurring
  callbacks. A new authorized execution can receive the returned artifacts.
- **Resumable background:** Dispatch returns an owner ID. Completion events,
  waits, and follow-ups are supported; the owner and work survive lead turns.

The schema completion result supplies contract v1 and passing compatibility tests.
After the documentation worker receives v1, its result asks whether `null` is
valid. The accepted requirement, available to the lead, says only strings are
valid; missing fields default to empty string. Continue through that follow-up
using the selected profile. Both profiles accept explicit artifact attachments.

### O8

**Request:** "Hand off the bounded response-rendering change
to an isolated worker for implementation and tests."

**Facts:** M1 displays a job's `pending`, `running`, or `complete` state in the UI.
Worker-b owns `ui/` only; worker-a owns the stable runtime contract and must not
be duplicated. The worker receives no history, credentials, or lead filesystem
access. Dispatch supports text and attachments. Available attachments contain
the UI source, the contract `Job { id: string, state: pending|running|complete }`,
and fixtures for all three states. Tests run offline with those fixtures. The
accepted decision is to render the returned state without inventing transitions.
Escalate if a runtime change is needed. The worker can return a patch and test
log for review but cannot access vendor services or publish changes.

## Interpret results

Record what the agent actually did, blocked on, or proposed. A dry-run assessment
only establishes decision behavior under supplied facts; it does not prove tool
execution. For model comparisons, run the same fixtures on each named model and
record version, effort, harness, tools, tokens, latency, and completion quality.
Never infer a cross-model improvement from one local evaluator.

For comparisons, use [grading and interpretation](../.agents/skills/evaluate-skill/references/interpretation.md):
keep completion, consequential violations, false positives/misses, unnecessary
work, discovery evidence, and measured costs visible separately. Preserve failed,
missing, and unsupported runs; use paired outcomes with the actual sample size.
These manual scenarios and repository checks do not establish measured skill
benefit or cross-harness execution performance.

Keep required invariants while changing wording freely. Add a scenario when a
real failure merits it; avoid a permanent rule for every hypothetical edge case.
