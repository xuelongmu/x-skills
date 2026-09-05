---
name: orchestrate
description: Coordinate delegated engineering work across agent harnesses through bounded milestones, clear ownership, selective updates, and human review checkpoints. Use when asked to coordinate multiple tasks or workers; not for ordinary single-task implementation or merely reporting status.
---

# Orchestrate toward a reviewable outcome

Own the outcome, dependency decisions, and scope boundaries. Let workers own
implementation and its normal verification loop. The lead should add judgment,
not a second stream of the same progress reports.

## Adapt to the execution harness

Here, a worker means a delegated unit of execution, not a particular tool,
persistent conversation, process, or model. Use the active harness's documented
capabilities and instruction precedence; no named service or tool API is required.

Check only the capabilities needed for the plan: whether delegation blocks or
runs in the background, whether workers can receive follow-ups or resume, what
context and workspace they receive, and whether work survives the lead ending
its turn. Do not assume inherited history, credentials, permissions, shared file
paths, or persistent worker identity. Give explicit context and reachable artifact
references; verify isolation before scheduling concurrent writers.

With blocking delegation, collect its result before advancing dependencies.
With background workers, use supported completion and messaging mechanisms.
When a worker cannot resume, hand off its recorded outcome and artifacts to the
next authorized execution rather than treating it as a live owner. These are
capability choices, not reasons to build a harness adapter framework.

Use only delegation and task capabilities available and authorized in the current
environment. This skill grants no permission to create tasks, spend money, merge,
deploy, or change shared data. If delegation is unavailable, offer a sequential
plan or perform authorized local work; do not pretend workers were dispatched.
If an external supervisor already owns scheduling or PR maintenance, use its
operational guidance and avoid creating a competing supervision loop.

## Establish the next checkpoint

Recover the current goal and accepted decisions before dispatching. Prefer the
current ADR, specification, and issue relationships over an older conversation
or reviewer suggestion. Identify:

- The next useful outcome and the evidence that demonstrates it.
- What is required now, explicitly deferred, and outside the authorization.
- Dependencies, current owners, and where a human decision or review stops work.

For long-running work, keep a compact coordination note in the existing task or
authorized tracking location: milestone, owner/task, dependency, status/evidence,
next action, and human gate. Update it when those facts change. Link canonical
decisions rather than copying them into another specification or activity log.

Distinguish an implementation checkpoint, a testable environment, and production
readiness. A safe limitation may be acceptable for one checkpoint without
becoming the permanent product contract. Record its consequence and owner.

## Split by independent ownership

Inventory existing owners before creating another worker. Keep tightly coupled
invariants and unstable interfaces together. Split when a deliverable has a
clear boundary, can be verified separately, and benefits from an independent
owner. File count, PR count, and new review comments are not task boundaries.

For example, core runtime work can stay with one owner while UI integration
starts after its interfaces stabilize. A separate acceptance pass can then
exercise the combined result if independent review is authorized and useful.
This is an option, not a required three-worker structure.

Give each worker a bounded handoff: outcome, relevant sources and decisions,
owned scope, upstream dependencies, required evidence, and escalation/stop
conditions. Include mutation and spending limits. Send decision deltas when
context changes, not the entire conversation each time. Avoid competing writers;
define ownership or isolation before workers touch shared files or state.

One worker may own several related PRs. Assign normal CI, feedback handling, and
base integration to that owner or the existing automation, not to both. Integrate
dependency changes through direct children and refresh affected evidence; do not
retarget or restart an entire stack reflexively.

## Coordinate patiently and communicate selectively

Allow exploration, implementation, tests, and review windows to finish. Silence
or an unchanged status is not evidence of a stalled worker. Do not interrupt,
restart, duplicate, or take over work merely to obtain a fresher update.

Prefer completion events and the host's wait or recurring mechanisms over rapid
polling. Choose any fallback check interval around the work's expected duration
and the user's preferences; widen it when state is unchanged. Do not promise
future check-ins without an actual supported mechanism. One owner monitors a
given loop; the lead inspects exceptions and milestone outcomes.

Worker reports should distinguish routine progress from a decision request,
material scope/risk change, blocker, or milestone ready for review. On receipt:

- Incorporate routine progress without sending an acknowledgment or paraphrasing
  it to the user when neither would change anyone's next action.
- Route a substantive decision to its owner with the evidence and recommended
  action. Batch related nonurgent clarifications into one message.
- Notify the user at agreed checkpoints, for decisions needing their authority,
  and for meaningful changes to outcome, risk, or expectations.

Honor explicit update requests and host-required progress messages. Keep those
updates concise and useful; a running test-count tally is not a milestone.
When stuck, check the actual blocker and ownership before nudging. Do not invent
a fixed timeout after which productive work must be reassigned.

## Prevent review from becoming an unbounded work generator

Treat automated and human review findings as claims to evaluate against the
accepted contract. Separate required correctness/security, checkpoint-critical
gaps, later capabilities, and optional hardening. A locally plausible suggestion
does not by itself authorize a stronger product promise or new subsystem.

Let workers resolve normal defects. Intervene when feedback changes a money,
authorization, schema, lifecycle, or public-contract assumption, or when linked
fixes repeatedly produce another narrower fix. Ask which invariant is involved,
which reachable case fails, and which layer should own the correction. Prefer a
root-cause repair over another guard around an accidental boundary. Use a focused
complexity or architecture review when warranted and available, not on every
comment.

Preserve real safety while rejecting unsupported zero-tolerance requirements.
For example, an informational reconciliation backlog is not automatically a
failed repair job; a bounded read-only sample is not automatically a queue that
needs scheduling. Establish the required consequence before adding machinery.

Revisit checkpoint scope when review uncovers a materially new capability. A
deferred gap needs an explicit limitation, owner, and the safety evidence needed
for the current checkpoint. Do not call it fixed or close its parent goal. Do
not defer a defect that invalidates the claimed evidence or accepted safety.

## Verify, hand off, and pause deliberately

Ask for evidence appropriate to the claimed outcome, not just aggregate test
counts. Keep fixture execution, local browser verification, live sandbox/vendor
proof, and production validation distinct. Separate paths passing does not prove
their end-to-end composition. Independently check consequential claims where it
adds confidence; do not duplicate every worker test or full review audit.

For PR work, the owner accounts for all relevant feedback, including pagination,
and ties checks and review evidence to the current head. Answered comments,
resolved threads, approvals, green CI, and mergeability are different facts.
Surface unexplained blockers; do not bypass them to complete the milestone.

At the checkpoint, give the user the outcome, review/dependency order, evidence
limits, and remaining decisions or blockers. Pause where human review is the
agreed gate. Continue independent authorized work only when it cannot preempt
that decision. A worker finishing does not authorize merging or imply the whole
goal is complete. Stop only owned monitors/resources at their agreed endpoint;
leave user state and unrelated work intact.
