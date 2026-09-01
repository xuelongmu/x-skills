# Findings and verdict

## Evidence standard

A consequential finding must contain:

1. the proposal claim or omission;
2. concrete evidence or an explicitly labeled assumption;
3. the violated constraint or failure scenario;
4. the consequence over time or under failure;
5. the decision or revision needed before acceptance.

Prefer file and line references, accepted ADRs, contracts, infrastructure state,
primary documentation, measured baselines, or stated quantitative targets. Do
not elevate architecture taste, generic best practice, or an unbounded future
scale story into a finding.

For a timeout or partial-flow issue, name the exact unknown state and the effect
that may duplicate, disappear, or become unrecoverable. For a migration issue,
name the incompatible producer, consumer, schema, deployment, or rollback state.

## Assumption register

Classify every load-bearing assumption:

| Class | Meaning | Review action |
| --- | --- | --- |
| Verified | Direct evidence supports it | Cite the evidence and continue |
| Testable | A bounded proof can resolve it | Name the test, owner, and decision deadline |
| Unsupported | No adequate evidence yet | Revise or block according to consequence |
| False | Evidence contradicts it | Treat as a consequential finding |

Do not mislabel a judgment decision as an assumption. A choice such as who owns
writes cannot be measured into truth; the driver must decide it. Conversely, a
claim such as provider retry behavior is an assumption until verified, not a
design preference.

## Verdict rules

- **Sound:** The proposal can advance at its stated maturity. Remaining items are
  genuinely reversible, explicitly deferred, or accepted risks with owners.
- **Revise:** At least one evidence-backed issue could change feasibility,
  safety, ownership, public behavior, migration, or long-term operability.
- **Blocked by unknowns:** Missing evidence prevents judging a load-bearing
  assumption or current-system fact. Name the minimum evidence needed; do not
  disguise uncertainty as `Revise`.

## Report shape

1. `Verdict: Sound | Revise | Blocked by unknowns`
2. **Review basis** — artifact maturity, intended outcome, current-system evidence,
   accepted decisions, and important coverage limits.
3. **Load-bearing decisions** — explicit decisions on which the proposal depends.
4. **Hidden decisions** — consequential choices the proposal leaves implicit.
5. **Assumption register** — class, evidence, consequence if wrong, and next proof.
6. **Consequential findings** — evidence-backed, ordered by impact; say `None`
   when appropriate.
7. **Omitted alternatives** — only credible, materially different architectures.
8. **Reversibility and migration** — commitment points, coexistence, rollback,
   accumulated state, and exit path.
9. **ADR readiness** — `Ready`, `Not ready`, or `Not applicable`, followed by what
   remains before driver acceptance and ADR handoff.

Do not add an approval statement. `Sound` is a review verdict, not authorization
to accept, implement, publish, or record the decision.
