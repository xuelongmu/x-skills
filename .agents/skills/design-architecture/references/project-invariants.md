# Project-invariant discovery

Use this only when the target repository defines project-specific architecture
constraints. Read applicable instructions, accepted ADRs, contracts, system
documentation, infrastructure, and configuration. Cite the evidence that makes
each invariant binding; do not infer one from a checkout path or transfer it to
another codebase.

Give special weight to declared constraints involving:

- tenant isolation and authorization across calls, queues, stores, replay,
  repair, and administrative paths;
- an authoritative application or control plane paired with stateless compute
  or provider workers;
- billing idempotency and an external pricing or metering authority;
- durable execution when a provider timeout leaves the outcome unknown;
- documented cross-service contracts and compatibility during mixed versions;
- cloud portability, deliberate provider coupling, and exit cost;
- provider credentials, secret custody, rotation, and least-authority use;
- schema expand-contract, reversibility, ERDs, seeds, audit, and backfill effects;
- compliance-forward data ownership, retention, deletion, and evidence; and
- preservation of observable UI behavior when replacing an interface.

Classify each applicable item as a verified fact, fixed constraint, assumption,
judgment decision, deferral, or accepted risk. If repository authorities are
absent or contradictory, surface the conflict instead of hard-coding a rule.
