# Architecture review lenses

Apply these separately so strength in one area does not hide a defect in
another. Scale depth to the artifact's maturity and the consequence of being
wrong.

1. **Premise** — Is this the right architectural problem? Would the stated
   outcome still fail to solve the actual need? Suppress this lens when an
   accepted upstream decision already settles the premise unless new evidence
   changes it.
2. **Grounding** — Does the proposal match the actual code, infrastructure,
   contracts, operational model, and accepted decisions? Does it duplicate an
   existing capability or assume greenfield conditions?
3. **Decision completeness** — Which consequential ownership, boundary, state,
   execution, compatibility, security, or operational choices are implicit?
4. **Assumptions** — Classify each important claim as verified, testable,
   unsupported, or false. State the consequence if it is wrong and the cheapest
   useful test.
5. **Alternatives** — Were materially different ownership, boundary, state, or
   execution models considered? Library or vendor substitutions inside the same
   model do not count. Include the status quo or smallest change when credible.
6. **Failure semantics** — Trace missing and empty input, upstream failure,
   timeout with unknown outcome, duplicate and replay, partial completion,
   reconciliation, and poison states where applicable.
7. **Evolution** — What public behavior, write authority, data shape, execution
   history, or provider dependency becomes hard to change? How do mixed versions
   and accumulated state behave?
8. **Operational reality** — Are observability, ownership, repair, migration,
   deployment, rollback, retention, deletion, and incident diagnosis sufficient
   for the artifact's maturity?
9. **Project invariants** — Does the design preserve applicable repository rules,
   accepted ADRs, trust boundaries, source-of-truth rules, and compliance
   obligations?
10. **Simplicity** — Does each new subsystem or seam remove more complexity than
    it creates? Could the design delete, defer, or remain inside an existing
    boundary without losing the intended outcome?

## Maturity calibration

- **Requirements brief:** challenge premise, outcomes, fixed constraints,
  fundamental conflicts, and dangerous assumptions. Do not require migration
  mechanics or detailed failure protocols unless the brief claims to settle
  them.
- **Architecture brief or service design:** require ownership, boundaries,
  authoritative state, major contracts, distinct alternatives, failure model,
  operational owner, evolution, and invalidating assumptions.
- **Technical or implementation plan:** require implementable cross-boundary
  semantics, compatibility, migration, rollback, observability, repair, and
  verification. Architectural choices must not be left to implementation.
- **ADR draft:** require a decided question, evidence-backed context, explicit
  alternatives and consequences, accepted risks, migration/reversal implications,
  and no unresolved assumption that could invert the decision.
- **Supersession proposal:** require new evidence or changed constraints, the
  relationship to the accepted ADR, coexistence and migration, and preservation
  of historical context.

Silence is a finding only when the omitted decision belongs at the artifact's
current maturity and can change feasibility, safety, or the accepted contract.
