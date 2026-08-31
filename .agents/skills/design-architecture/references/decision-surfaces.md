# Decision surfaces

Use this as a risk-based scan, not a form to fill mechanically. Mark each
applicable surface as settled by evidence, a fixed constraint, an assumption, a
judgment decision, a deferral, or an accepted risk.

## Ownership and boundaries

- Which system is the source of truth? Who may write, correct, or delete it?
- Where are the process, service, tenant, and trust boundaries?
- Which interface becomes a contract, who consumes it, and who owns compatibility?
- Can the work remain inside an existing boundary, or can a boundary disappear?

## State and time

- What are the states and legal transitions, including missing, empty, pending,
  failed, poisoned, deleted, retained, and replayed?
- What is atomic? Where can concurrency race, and how are duplicates recognized?
- Is an idempotency identity stable across attempts and distinct across intents?
- What happens on timeout when the external effect may have succeeded?
- How are partial success, retry exhaustion, reconciliation, and manual repair
  represented?

## Evolution and operations

- How do old and new producers, consumers, schemas, and deployments coexist?
- What is the expand-contract, backfill, cutover, rollback, and replacement path?
- What evidence makes an incident diagnosable? Who owns alerts, repair, replay,
  rollback, and long-lived poison states?
- What grows with tenants, traffic, features, or retention? Ground latency,
  fan-out, storage, and provider cost in a target, measurement, or assumption.
- What is the provider or cloud exit cost, and which coupling is deliberate?

## Security, custody, and compliance

- Where are authentication and authorization enforced? Can tenant identity be
  confused or lost across a boundary?
- Which system holds secrets and provider credentials, and which actors can use
  or rotate them?
- Who owns each datum, audit event, retention rule, deletion proof, and compliance
  record?
- Does replay or repair preserve authorization, billing, audit, and retention
  semantics?

## Blindspot pass

Use this only for a territory the driver cannot evaluate, not for an expert who
is merely undecided.

1. Ground the territory in repository evidence and, when needed, current primary
   sources. Show settled answers rather than presenting them as choices.
2. Identify only items that change a decision. Convert each into one of:
   - a decision with realistic options and a recommended default;
   - a hazard that constrains every design;
   - an assumption with a falsification test;
   - an experiment or proof needed before commitment.
3. Explain the consequence of the default and the signal that should change it.
4. Keep domain trivia out. The result is a decision map, not a lesson.

If the driver remains unable to choose, recommend a reversible default and label
it as an assumption. If no safe default exists, mark the decision blocked and
name the evidence or expert judgment required.
