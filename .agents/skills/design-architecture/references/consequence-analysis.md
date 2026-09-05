# Compare architectural consequences

Alternatives should differ in ownership, boundary, durable state, or execution.
If the only difference is a library, transport, name, or vendor setting, treat it
as an implementation variant.

Trace applicable options through the same discriminating scenarios:

| Scenario | Distinguishing question |
| --- | --- |
| Normal operation | Where is authoritative state and when is success acknowledged? |
| Timeout or partial completion | What may have succeeded, who records uncertainty, and who repairs it? |
| Duplicate or replay | Which identity prevents duplicate effects, and where is it claimed? |
| Deployment and migration | Can old and new readers, writers, and in-flight work coexist? |
| Rollback and replacement | What persisted or external commitment prevents reversal? |
| Growth and incidents | What becomes costly, who operates it, and what evidence locates failure? |

Add a domain-specific scenario when it could invalidate a design; omit irrelevant
ones. Rank by the decision's real constraints, measurements, or stated targets.
Explain why the recommendation wins, what complexity it accepts or removes,
which assumption could reverse it, and the cheapest useful proof before commitment.
