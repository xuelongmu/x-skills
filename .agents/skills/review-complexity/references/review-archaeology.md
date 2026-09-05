# Review-driven complexity

Use when repeated review fixes may have changed the design's contract or owner.
History helps explain a mechanism; its author and commit count do not determine
whether it is justified.

## Recover the cause

Compare the initial solution with the review delta when the boundary is clear.
Trace suspicious state, helpers, public exports, schemas, and rules to the
feedback or requirement that introduced them. Cluster related symptoms rather
than letting one comment at a time dictate the architecture.

For each substantial mechanism, identify the reachable failure it prevents and
the requirement that makes that prevention necessary. A reviewer can find a
locally valid issue under a contract the product never needed to promise.

Separate the claimed mechanism from the conclusion. Probe a concrete path when
practical; an incorrect explanation can still point to a nearby real defect.
For timing-dependent failures, consider the fastest relevant actor, including
automated clients or adversaries. Do not dismiss a race using human timing when
automation can reach it.

## Find the owner

Recurring fixes inside earlier fixes are a reason to revisit the boundary.
Look for duplicate predicates, parallel representations of one fact, helpers
surrounding an untested composition, and controls for states upstream cannot
produce. Prefer removing the condition that needs arbitration to adding more
synchronization.

Put bounds at the lifetime of the operation they bound. A continuation must not
reset a logical budget. Put heavyweight parsing and validation at ingest or load
when request-time work can consume a trusted representation.

For hashes, registries, proofs, or attestations, identify the threat and verifier.
Self-derived evidence is not authenticity. Keep distinct controls only when they
protect distinct boundaries. Fail closed on unknown outcome-affecting semantics
without turning harmless additive metadata into outages.

Distinguish easily reversible preferences from commitments in persisted formats,
public APIs, and external contracts. An architecture change may be worthwhile
but requires an explicit decision rather than being smuggled into cleanup.

## Assess the candidate

For each material recommendation, give its evidence, owning invariant, cost,
and recommended alternative. Keep justified controls; simplify duplicate
mechanisms; move concerns to their owner; remove unsupported machinery; and
separate proposals that change accepted behavior.

Tests can preserve an accidental abstraction. Retain evidence for real contracts
and remove implementation-only assertions with the mechanism they describe.
For state machines or continuation flows, exercise the composition when leaf
tests cannot establish progress. Report unexercised claims as uncertain.

Prioritize substantial simplifications and explain important complexity that
execution or repository evidence justified retaining.
