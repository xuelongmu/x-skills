---
name: design-architecture
description: >-
  Design consequential software architecture before implementation: service or
  trust boundaries, data ownership, execution models, public contracts, durable
  workflows, migrations, and major module seams. Use when important choices are
  still open and expensive to reverse; not for routine implementation planning,
  small local refactors, visual ideation, or designs whose consequential choices
  are already settled.
---

# Design architecture

Expose consequential choices before they become accidental contracts. Produce a
repo-grounded architecture decision brief with a recommendation; do not
implement code, silently approve a direction, or create accepted history.

## Establish scope and evidence

1. Confirm that the request contains a difficult-to-reverse choice in ownership,
   boundary, durable state, execution, compatibility, or public behavior. Route
   ordinary implementation planning and local refactors to the normal planning
   workflow. Route critique of an existing proposal to `review-architecture`.
2. Read every applicable repository instruction. Inspect the real system before
   proposing changes: relevant code, accepted ADRs, contracts, system docs,
   infrastructure, tests, issue or PR history, and git history. Follow evidence
   where it is useful; do not perform a ceremonial full-repository scan.
3. Treat the system as brownfield unless evidence proves otherwise. Name the
   current boundary, source of truth, owners, callers, state, and operational
   path. Separate verified repository facts from external facts and inferences.
4. Frame the decision: why now, affected actors and systems, fixed constraints,
   negotiable choices, success, safe failure, and reversal cost. Ask only for
   judgments that repository evidence cannot answer.

When current platform behavior or an external contract matters, consult primary
sources and record the version or date checked.

## Build the decision map

Maintain six explicit buckets:

- **Verified facts:** evidence-backed properties of the current system.
- **Fixed constraints:** requirements or accepted decisions this design must
  honor.
- **Testable assumptions:** uncertain claims with a proposed proof, owner, or
  deadline.
- **Judgment decisions:** real choices whose trade-offs require a driver.
- **Explicit deferrals:** choices intentionally postponed, with the trigger for
  revisiting them.
- **Accepted risks:** known downside, why it is tolerated, and the repair or exit
  path.

Read [decision-surfaces.md](references/decision-surfaces.md) and inspect only the
surfaces applicable to the decision. If the driver cannot evaluate an unfamiliar
territory, use its blindspot pass to turn unknown unknowns into decisions,
hazards, defaults, or experiments; do not ask the driver to invent domain facts
and do not turn the pass into a tutorial.

Read [project-invariants.md](references/project-invariants.md) when repository
instructions, accepted decisions, or system documentation define architecture
constraints that must shape the design. Treat named products and providers as
project evidence, never as portable defaults.

## Develop and compare architectures

Read [consequence-analysis.md](references/consequence-analysis.md) before
generating alternatives or analyzing failure behavior.

- Generate two to four architectures only when materially different choices
  remain. Include the status quo or smallest credible change when it can satisfy
  the goal.
- Require alternatives to differ in ownership, boundary, durable state, or
  execution model. Different libraries, names, transports, or deployment
  products inside the same model are variants, not distinct architectures.
- If only one approach is viable under fixed constraints, state why and test
  that conclusion; do not manufacture a menu.
- Compare consequences in normal operation, failure, evolution, migration,
  rollback, repair, and replacement. Use quantitative bounds only when grounded
  in measurements, stated targets, or explicit assumptions.
- Look for the deletion, deferral, or existing-boundary option before accepting
  a new subsystem.

Recommend a direction. State the forces that dominate, complexity accepted and
avoided, invalidating assumptions, proof or prototype still needed, and which
decisions remain reversible. A recommendation is not acceptance: preserve the
driver's decision authority.

## Deliver and hand off

Read [decision-brief.md](references/decision-brief.md) and return its concise
brief in chat or in the repository's existing design-artifact location when the
user requested a file. Do not introduce a new generic architecture-document
hierarchy.

Stop after the decision brief and ask the driver to accept, reject, or revise the
direction. Only after explicit acceptance, route the durable decision to the
repository's existing `write-adr` skill or ADR process. That workflow owns the
record, status, naming, and location. Never mark an ADR accepted or create
accepted history on the driver's behalf.

Verified reusable discoveries that emerge after implementation or an incident
belong to `capture-learning`. Delivery skills for issues, branches, commits, and
PRs remain authoritative for implementation work.
