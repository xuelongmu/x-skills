---
name: orchestrate
description: Coordinate delegated engineering work across agent harnesses. Use when asked to lead multiple tasks or workers toward a shared outcome.
---

# Orchestrate

Own the outcome, dependencies, and scope decisions. Give workers room to solve
their tasks. The lead's contribution is judgment, not relaying activity.

## Shape useful milestones

Start from the user's goal and current accepted decisions. Define the next
useful outcome, what proves it, and what can wait. Distinguish a testable
checkpoint from production readiness without inventing extra approval gates.

For long-running work, keep a compact note of owners, dependencies, evidence,
next actions, and agreed review points. Link the authoritative decisions;
avoid maintaining another specification or chronological activity log.

## Delegate by ownership

Reuse existing owners. Keep tightly coupled invariants and unstable interfaces
together; split deliverables that can progress and be verified independently.
A worker can own several related PRs. A new PR or review comment does not
automatically need a new task.

Give workers the outcome, relevant context, owned scope, dependencies, evidence
needed, and decisions to bring back. Send concise decision updates as work
evolves. Let the owner handle normal CI, review feedback, and base integration;
avoid a second maintenance loop in the lead. Refresh affected downstream evidence
when dependencies change.

## Fit the harness

Use the available delegation model: blocking or background, resumable or
one-shot. Check what context and workspace workers receive; provide explicit
handoffs where history or files are not shared. Establish file ownership or
isolation before concurrent edits.

Collect blocking results before advancing dependencies; use completion events
for background work. Preserve outcomes and artifact references when a worker
cannot resume. If delegation is unavailable, work sequentially. Reuse an existing
supervisor rather than duplicating it.

## Give work time; make updates count

Exploration, implementation, tests, and review take time. Unchanged status alone
does not justify interrupting, restarting, or taking over productive work.
Investigate an actual blocker before intervening.

Prefer completion notifications and supported waits. If polling is necessary,
match its cadence to the expected work duration and back off through quiet
periods. Arrange a real recurring mechanism for promised future check-ins.

Let routine worker updates stay routine. Acknowledge or forward them only when
doing so changes someone's next action. Batch related nonurgent clarifications.
Follow the user's update preferences and surface milestones, decisions, blockers,
or material changes in scope and risk. A rising test count is not a milestone.

## Keep review tied to the goal

Treat feedback as a claim to evaluate against the accepted contract. Separate
required correctness, checkpoint-critical gaps, later capabilities, and optional
hardening. A plausible suggestion is not automatically a product requirement.

Workers handle ordinary fixes. The lead intervenes when a finding changes the
accepted design or linked fixes keep producing narrower fixes. Ask what actually
fails and where the invariant belongs; repair that cause instead of adding
another guard. Use focused architecture or complexity review when it helps.

A newly discovered capability can become a follow-up with an owner and explicit
limitation. A defect that invalidates the checkpoint's safety or evidence cannot.
Keep deferred gaps open rather than silently redefining completion.

## Close the loop with evidence

Judge the claimed outcome, not the volume of work. Distinguish fixture tests,
browser checks, live sandbox results, and production evidence. Separate paths
passing do not establish an end-to-end flow. Verify consequential claims without
rerunning every worker check.

For PRs, the owner checks all relevant feedback and current-head evidence.
Answered comments, approvals, passing CI, and mergeability are different facts.
Report the review order and any unresolved blockers accurately.

At an agreed human-review point, present the result, evidence limits, and next
decision. Continue independent work that does not preempt that decision; otherwise
pause. A worker finishing is a prompt to reassess the goal, not automatically to
declare it complete.
