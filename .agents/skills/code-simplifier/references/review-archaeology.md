# Review Feedback Archaeology

Use this mode for a large diff shaped by many review-fix commits, especially
when multiple locally reasonable fixes may have accumulated into a globally
unreasonable design. Judge every mechanism on its merits; automated origin is a
reason to verify authority, not a reason to dismiss a finding.

## Reconstruct how complexity accumulated

When Git history or review comments are available:

1. Compare the initial implementation with the current diff.
2. Count follow-up commits that each answer one review finding.
3. Trace suspicious helpers, public exports, schema fields, proof layers, ADR
   edits, and tests to the commit or comment that introduced them.
4. Distinguish the author-designed core from incremental reviewer residue.
5. Look for several mechanisms that solve the same root concern in overlapping
   ways, including generated feedback promoted into durable documentation.

Do not use commit count or line count as proof. Use them to locate decisions
whose contract, owner, and operational cost need re-evaluation.

Measure the review loop before reading threads one by one. Identify the target
base and, when history makes it reasonably clear, the last feature commit before
review-only fixes. Compare the feature diff with the post-review delta using
commit counts and diff short statistics. Report the actual numbers and any
uncertainty; do not manufacture a boundary from ambiguous history.

Count tests near the changed area, then count those that exercise the relevant
composition or orchestrator rather than extracted leaves. A large unexercised
core lets hypothetical findings accumulate because execution cannot refute them.

Cluster the threads before answering them. Many symptoms often reduce to a few
root causes. Report and repair the cluster, then explain which sibling symptoms
the repair retires. Do not let thread-by-thread replies dictate the architecture.

## Verify reachability and mechanism

Reclassify findings by reachable impact rather than inheriting a reviewer's
severity label:

- a deterministic single interaction is directly reachable and normally needs
  correction;
- an ordered sequence without timing is usually reachable and should be tested;
- a timing-dependent sequence requires measurement of both the vulnerable
  window and the fastest relevant actor, which may be a human, client, retry,
  worker, or adversary.

Do not decline a timing issue based on a human interaction floor when the threat
model permits automation. Conversely, do not add concurrency machinery for a
window that reliable measurements show cannot be reached by any relevant actor.

Try to reproduce or refute material findings against the target revision with a
disposable probe or real application flow. Record observed output, keep probes
out of the final diff, and label findings that remain unverified. Verify the
reviewer's claimed mechanism separately from the underlying conclusion: an
incorrect explanation can point toward a real adjacent defect, while a plausible
explanation can also collapse under execution.

When behavior depends on a vendor, SDK, protocol, or library contract, consult
current primary documentation or an executable compatibility probe. Separate
documented guarantees from observations and unknowns. Prefer stating the
required invariant and leaving an unverified mechanism open over inventing a
guarantee to make the design appear closed.

## Challenge accidental contracts

For each rule introduced during review, ask:

- What concrete failure mode does it prevent?
- Which reachable acceptance scenario exercises it?
- Which requirement, ADR, contract, or domain owner makes it authoritative?
- Is it true for every entity and configuration, or only declared and reachable
  cases?
- Would keeping it create a Cartesian domain model containing invalid or purely
  theoretical combinations?

Any response that changes an ADR, public API, persistent schema, or product
policy requires explicit product or architecture scrutiny. “The reviewer asked
for it” is not sufficient justification.

Distinguish overengineering from foreclosure: ask whether reversing the choice
later is an ordinary code change or a migration across persisted or external
state. Preserve justified flexibility at hard-to-reverse boundaries. Defer
mechanisms that merely pre-decide a preference before evidence exists.

Present material forks rather than resolving them silently. Give the owner the
coherent options, cost and risk of each, and a recommendation. Do not widen a
focused simplification into a rewrite merely because a cleaner global design is
imaginable.

## Raise the repair altitude

Trace chains in which review round N+1 finds a defect inside round N's fix on
the same path. After two or three linked fixes, treat the chain itself as the
finding: the invariant is being enforced at the wrong level.

Ask:

- Is the proposed repair adding a check, or removing the condition that made
  the check necessary?
- Does a bound live at the same scope and lifetime as the thing it bounds?
- Is there one owner, or a lock and state machine arbitrating multiple owners?
- Would this repair retire sibling symptoms, or only the latest one?

Prefer deleting unnecessary work to abstracting it. Prefer one owner to a lock,
one lifetime-correct bound to resettable per-leg limits, and one level-correct
repair to several symptom guards. A large refactor without a safety net is a
different project; separate it from what the current change can safely carry.

Watch for review-loop signatures:

- the same rule restated in several places;
- offer, preview, or enable predicates that mirror an apply or commit gate;
- several guards hand-composed at several call sites;
- parallel counters, refs, or maps representing one keyed concept;
- flattened projections that manually maintain a join;
- extracted leaf modules surrounding an untested composition core;
- machinery for disabled or unreachable states;
- stale names, single-valued flags, or validation of states upstream cannot
  produce; and
- a comment confidently explaining a field, bound, or missing signal that was
  never verified.

Where preview and mutation genuinely share a rule, consider a pure planning
step consumed by the mutation rather than duplicated predicates, while checking
the cost of preview-path execution. Where paraphrase cannot be removed, declare
one canonical source and a precedence rule.

For every hardening change ask what it newly permits as well as what it blocks.
Retries need idempotency; widened input boundaries need authenticity checks;
continuations must not reset logical-operation budgets. Control flow must use
explicit state rather than rendered strings. Verify fields from actual types or
runtime payloads rather than preserving confident comments. Tests over shared
ordered collections should assert the global invariant and the new entry's own
identity, not that one contributor remains “last.”

## Put work at the correct boundary

Determine whether a concern belongs to configuration compilation, ingest,
activation, funding, request admission, settlement, reconciliation, UI, or
another lifecycle owner. Visible data does not make the current module the
owner. A defensive check is harmful when it encodes an adjacent subsystem's
policy or creates contradictory setup requirements.

Move heavyweight parsing, recursive freezing, hashing, semantic validation,
proof reconstruction, and coverage scans to ingest, compile, load, or activation
boundaries when possible. Runtime admission should consume a trusted immutable
handle and perform only checks that can vary per request, such as freshness,
effective time, lease, tenant or account identity, and current status. Flag a
public API that makes heavyweight validation the easy hot-path call even if a
future optimization promises memoization.

## Match integrity machinery to a threat

For each digest, registry, proof, evidence array, freeze, or attestation, name
the threat and verifier:

- accidental mutation;
- persistence corruption;
- malicious in-process construction; or
- remote tampering.

Self-derived evidence is not an authenticity boundary. Prefer the smallest set
of non-overlapping controls: for example, authenticated transport plus one
content digest for source capture, or one immutable projection checksum for load
integrity. Keep multiple attestations only when each protects a distinct
boundary and has a realistic trust root.

## Apply fail-closed behavior precisely

Fail closed on unknown money, security, authorization, or other
outcome-affecting semantics. Do not turn harmless additive metadata, unrelated
records, descriptions, or timestamps into outages. Prefer parsing required
fields, rejecting known unsupported shapes that can affect outcomes, and
ignoring irrelevant additive metadata over strict whole-response allowlists.

## Preserve justified complexity

Do not optimize for line-count reduction. Large-looking code may be warranted
for exact money or rational arithmetic, untrusted numeric parsing and bounded
inputs, tenant or authorization boundaries, idempotency and concurrency,
effective dating and interval overlap, remote identity correlation, unsupported
outcome-affecting shapes, and preventing stale or free fallback. Explain why
such code stays when deletion would weaken a real invariant.

## Review the tests with the machinery

Tests can preserve an accidental abstraction. Remove or consolidate tests whose
only purpose is a hypothetical construction seam, ownership leak, unjustified
global invariant, or mechanism being removed. Prefer realistic baseline
fixtures and table-driven rejection cases over fixtures enumerating every
theoretical combination.

Preserve direct evidence for real money, tenancy, authorization, concurrency,
idempotency, time-boundary, and fail-closed invariants.

Tests written immediately after a mechanism may encode what was implemented
rather than the external contract. For resume, continuation, state-machine, or
multi-request flows, require an end-to-end exercise when unit tests cannot prove
that composition actually advances. A large green suite is not evidence for a
flow that can silently do nothing.

## Give every candidate an evidence-based disposition

Classify each material candidate:

- **KEEP:** canonical requirement protected at the correct boundary.
- **SIMPLIFY:** real invariant implemented with unnecessary machinery.
- **MOVE/DEFER:** real concern owned by another subsystem or lifecycle phase.
- **REMOVE:** hypothetical or redundant machinery without a supported failure
  mode.
- **DECISION REQUIRED:** changing it would alter product policy, an ADR, public
  API, or the data model.

For each recommendation, provide:

- exact file and tight line range;
- origin or rationale when review history is available;
- concrete failure mode;
- canonical requirement, or note its absence;
- runtime and operational cost;
- smallest coherent alternative;
- tests that remain or should be removed; and
- whether the change preserves behavior or requires a decision.

For each defect, also state a concrete failure scenario, whether the correct
repair is a **patch**, **level change**, or **decision**, and whether recent
history already contains linked fixes on that path. Separate deliberate design
constraints and scope gaps from defects.

Prioritize a few architecture-level changes over dozens of cosmetic comments.
End with one merge disposition: **merge as-is**, **simplify before merge**,
**split or defer named pieces**, or **no actionable overengineering**. Include a
short list of material concerns that execution or documentation verified as
correct so the review's depth and boundaries are visible.
