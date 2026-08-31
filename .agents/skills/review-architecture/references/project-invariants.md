# Project-invariant review

Use this only when the target repository defines project-specific architecture
constraints. Read applicable instructions, accepted ADRs, contracts, system
documentation, infrastructure, and configuration. Cite the evidence that makes
each invariant binding; do not infer one from a checkout path or transfer it to
another codebase.

Check the proposal against declared constraints involving:

- tenant isolation and authorization across calls, queues, stores, replay,
  repair, and administrative paths;
- an authoritative application or control plane paired with stateless compute
  or provider workers;
- billing idempotency and an external pricing or metering authority;
- durable execution and reconciliation for unknown provider outcomes;
- documented, compatible cross-service contracts;
- cloud portability, deliberate provider coupling, and exit cost;
- provider credentials, secret custody, rotation, and least-authority use;
- schema expand-contract, reversibility, ERDs, seeds, backfills, and audit effects;
- compliance-forward data ownership, retention, deletion, and evidence; and
- preservation of observable UI behavior when replacing interfaces.

Do not hard-code these as universal facts. Missing or contradictory evidence
belongs in the assumption register or a `Blocked by unknowns` verdict when it is
load-bearing.
