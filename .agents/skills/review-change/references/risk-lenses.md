# Conditional review lenses

Use entries supported by actual changes or affected contracts. This is a lookup
for consequential risks, not a checklist for every review.

| Change signal | Investigate |
| --- | --- |
| Identity, authorization, data access | Identity propagation and authorization at the owning server seam, including caches, background work, direct bypasses, and administrative paths. |
| Schema, persistence, backfill | Mixed-version compatibility, locking, bounded restartable migration, and rollback or forward recovery. Preserve applied history. |
| Money, pricing, entitlements | Exact units and rounding, effective-time rules, idempotency, and behavior after unknown provider outcomes. |
| Providers, queues, retries | Effect/acknowledgement ordering, stable identity, duplicate and partial outcomes, reconciliation, and terminal ownership. |
| APIs, events, shared contracts | Producer/consumer compatibility, errors, ordering, rollout, and tests that exercise both sides. |
| Visible behavior | Relevant loading, empty, error, keyboard, focus, accessibility, responsive, and state-preservation paths. Evidence should exercise the changed flow. |
| Infrastructure or dependencies | Provenance, secrets, permissions, environment assumptions, regeneration, and deploy/recovery behavior. Review generated changes through their inputs and contracts. |
| Documentation or skills | Accuracy, commands and paths, ownership of rules, contradictory instructions, and unnecessary task expansion or blocking. |
| Hot paths or module boundaries | Actual data volume, unbounded work, ownership, query shape, and operational cost. Measure uncertain performance claims. |

Report a concrete failure path and its violated requirement. Missing evidence
is a gap; it is not automatically a defect. A documentation-only change does not
activate billing or security concerns unless its content actually affects those
contracts.
