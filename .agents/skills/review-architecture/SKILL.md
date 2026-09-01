---
name: review-architecture
description: >-
  Review an existing architecture brief, technical design, implementation plan,
  ADR draft, service or schema design, data flow, execution model, or proposed
  supersession. Use for consequential design review before acceptance; not for
  ordinary line-level code review, implementation-diff review, or open-ended
  architecture generation.
---

# Review architecture

Return an evidence-backed verdict on a proposed design. Review is report-only
unless the user separately asks for changes: do not edit, publish, approve,
create external records, or turn a draft into accepted history.

## Establish the review basis

1. Identify the proposal, intended outcomes, artifact maturity, and decisions it
   claims to make. A requirements brief, technical plan, and ADR draft carry
   different completeness obligations.
2. Read applicable repository instructions, the relevant current code and
   infrastructure, contracts, system docs, tests, accepted ADRs, and useful
   issue, PR, or git history. Verify external behavior against primary sources
   when it is consequential.
3. State the current system and existing accepted decisions. Do not re-litigate
   an accepted ADR without new evidence, a changed constraint, or an explicit
   supersession proposal.
4. Separate absent evidence from a defect. If missing facts prevent a responsible
   judgment, return `Blocked by unknowns` and name the smallest evidence needed;
   do not invent it.

Read [project-invariants.md](references/project-invariants.md) when repository
instructions, accepted decisions, or system documentation define architecture
constraints that the proposal must preserve. Treat named products and providers
as project evidence, never as portable defaults.

## Review the architecture

Read [review-lenses.md](references/review-lenses.md) and apply its ten lenses at
the depth justified by the artifact's maturity and risk. In particular:

- distinguish a decision from an unresolved assumption;
- find implicit choices that would become expensive contracts;
- trace partial, duplicate, replayed, timeout, and unknown outcomes where the
  artifact is mature enough to own those semantics;
- require genuinely different alternatives when alternatives exist, not a list
  of libraries inside one architecture;
- distinguish necessary complexity from premature subsystem creation;
- suppress stylistic preferences and speculative scaling concerns without a
  baseline, target, quantitative bound, or explicit assumption.

Review the proposal against the repository as it exists, not an imagined
greenfield replacement. Do not demand implementation detail from a requirements
brief when that detail can safely remain open; do not allow a technical plan or
ADR draft to defer a decision that determines feasibility, safety, migration, or
contract behavior.

## Validate findings and report

Read [findings-and-verdict.md](references/findings-and-verdict.md). Validate every
consequential finding against code, documentation, accepted decisions, primary
sources, quantitative bounds, or an explicit assumption. A concern that cannot
name its evidence, violated invariant, or concrete failure consequence is not a
finding.

Return exactly one verdict:

- `Sound` — no unresolved issue prevents acceptance at this artifact's maturity.
- `Revise` — evidence supports consequential corrections before acceptance.
- `Blocked by unknowns` — missing evidence prevents a responsible verdict.

The report must include load-bearing decisions, hidden decisions, an assumption
register, evidence-backed consequential findings, omitted alternatives,
reversibility and migration assessment, and ADR readiness with what remains
before acceptance.

`review-change` owns general implementation-diff readiness.
`review-complexity` owns review-driven accretion, overengineering, and
behavior-preserving simplification. If either exposes an unresolved
consequential choice, route exploration to `design-architecture` when that skill
is available and return here only when a proposal exists. If it is unavailable,
preserve the review verdict and add a `Design handoff required` section naming
the unresolved choice, why it is consequential, verified context, fixed
constraints, and next action: install or enable `design-architecture`, or
explicitly request a general non-decision analysis. Do not invent the missing
architecture inside this review. `write-adr` or the repository's ADR process
owns recording a driver-accepted durable decision. `capture-learning` owns
verified reusable discoveries after implementation or incidents.

## External cross-model review

External review is opt-in for each invocation. Before any export, disclose the
artifact, exact prompt, tool or provider, expected cost, and what repository
context would leave the boundary. Minimize the payload, remove secrets and
unneeded source, and use a read-only boundary when possible. Never silently
export source or confidential material, and never treat an external model's
output as the verdict; reconcile every finding against local evidence.
