# Consequence analysis

## Distinctness test

Before comparing alternatives, complete this sentence for each pair:

> These designs differ because one assigns **[ownership/boundary/state/execution]**
> to **[place]**, while the other assigns it to **[different place or model]**.

If the sentence names only a library, vendor product, transport, class name, or
deployment setting, collapse the pair into one architecture with implementation
variants.

Useful axes include centralized versus delegated write authority, synchronous
request versus durable command, caller-held versus service-held state, shared
store versus explicit replication, in-process module versus owned service, and
provider-specific orchestration versus a portable execution boundary.

## Scenario walk

Trace each applicable design through the same scenarios:

| Scenario | Questions |
| --- | --- |
| Normal operation | What is the authoritative flow, state transition, and acknowledgment point? |
| Missing or empty input | Is this distinct from invalid input, no work, or deletion? |
| Upstream failure | What remains durable, visible, retryable, and owned? |
| Timeout with unknown outcome | How is possible success recorded, queried, reconciled, and prevented from duplicating effects? |
| Duplicate or replay | What identity is stable, where is it claimed atomically, and what response is replayed? |
| Partial completion | Which invariant still holds, what compensates, and who repairs it? |
| Deployment | How do mixed versions and in-flight work coexist? |
| Rollback | What state or contract prevents a binary rollback, and what is the recovery path? |
| Migration | How are backfill, validation, cutover, and old-reader compatibility proven? |
| Accumulated state or features | What grows, couples, or becomes operationally expensive over time? |
| Incident diagnosis | What evidence locates ownership and reconstructs the outcome? |
| Provider or boundary replacement | What must move, be translated, or remain compatible? |

Do not force irrelevant rows. Add a domain-specific scenario when it can
invalidate the design.

## Recommendation test

Rank by the decision's actual forces, not a generic scorecard. Explain:

- why the recommended model wins under current constraints;
- what complexity it deliberately accepts and avoids;
- which assumption would invalidate it;
- the cheapest proof that reduces the most consequential uncertainty;
- which choices remain reversible and until what commitment point;
- why the credible alternatives lose now, and what changed condition could make
  one preferable.

Suppress speculative scale warnings without a baseline, target, bound, or
explicit scale assumption. A hypothetical 100x concern is not a finding by
itself.
