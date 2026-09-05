# State-transition semantics

Use when admission, operating mode, revocation, or a similar transition can
affect in-flight work. Recover the existing contract before changing controls.

## Preserve the promised boundary

A transition may apply at admission, commit, each external effect, or to work
already admitted. Preserve the established semantics during simplification.
Immediate revocation can be an intentional security property; do not replace it
with admission-only checks without authorization. Conversely, do not add
retroactive cancellation to a contract that allows admitted work to settle.

Identify the actor, forbidden effect, acceptable propagation delay, and required
audit evidence. Missing or contradictory requirements are a decision to resolve,
not permission to select an easier security boundary.

## Separate authority from presentation

Enforce policy at its authoritative server or domain seam. UI disabling,
cross-tab broadcasts, polling, and dialog cleanup may improve usability but
cannot replace authorization. Temporary UI staleness may be acceptable when the
server safely denies the action; evaluate it against the actual UX contract.

If one transition now requires coordinated guards across UI, routes, databases,
storage, providers, and settlement, reconsider which boundary should own it.
Distributed best-effort cancellation is not automatically stronger than a clear
admission rule with documented semantics.

## Preserve completion obligations

Separate new user mutations from system work needed to settle existing effects,
such as cleanup, ledger settlement, and provider-handle persistence. A later
authority change must not strand work the system is obligated to complete.

Use permanent controls for permanent invariants. A mixed-version rollout may
need a one-time backfill instead of lasting trigger or compensation machinery.

Verify behavior at the owning seam: denied work produces no forbidden effects,
direct bypasses fail, admitted settlement remains safe, and the promised
transition timing survives simplification. Exercise the full flow when isolated
guards cannot prove these properties.
