# Simplifying State-Transition Controls

Use this checklist when a diff changes authorization, impersonation, operating
mode, revocation, or another state whose transition can affect in-flight work.
Also use it when repeated review fixes are spreading one concern across several
system layers.

## Recover the contract first

Determine the established transition semantics from explicit requirements,
tests, documentation, and current behavior. Preserve those semantics during a
review or behavior-preserving simplification. If the evidence is inconsistent
or incomplete, report **DECISION REQUIRED** instead of choosing a default.

When the user explicitly asks to design or change the transition contract,
evaluate when the new state should take effect:

- request admission;
- transaction commit;
- every durable or external side-effect boundary; or
- retroactively for already-admitted work.

An admission boundary is often the simplest option for a new contract, but it
is not the default for an existing system. Immediate or continuous revocation
may be an intentional security property, including for emergency termination
or kill-switch behavior. Do not remove mid-flight authorization checks or allow
admitted work to continue unless the established contract already permits it or
the user explicitly authorizes that behavior change. Conversely, do not add
retroactive revocation when the established contract lets admitted work settle.

Write down the threat model:

- Who initiates the transition?
- Is this hostile revocation, an operator mode change, or ordinary configuration?
- What exact event must be prevented?
- Is bounded propagation acceptable?
- What audit or compliance evidence is actually required?

Do not claim that a framework requires instantaneous retroactive cancellation
without a specific control. Centralized least-privilege admission, auditability,
and documented semantics may provide a stronger control than distributed
best-effort cancellation.

## Find the authoritative seam

Prefer one fail-closed chokepoint, or a small number of domain admission seams,
over route-by-route assertions. Authentication, impersonation, and mutation
policy belong in shared server or domain guards.

Treat UI hiding, disabled controls, dialog cleanup, refreshes, cross-tab
broadcasts, and polling as usability or defense-in-depth aids. They are not the
security authority. A temporarily stale control is acceptable when the server
returns a structured denial. Do not add real-time synchronization solely to make
non-authoritative UI state look instantaneous.

Suspect a distributed-revocation protocol when live reauthorization spreads
across several of these layers:

- UI refs or effects;
- cross-tab broadcasts;
- polling or status endpoints;
- server actions or routes;
- database writes;
- object storage or presigned URLs;
- provider jobs or queues;
- background or scheduled settlement; and
- cleanup or compensation state machines.

When this smell appears, challenge the semantic boundary before hardening every
layer.

## Preserve system-owned settlement

Separate new user-requested mutations from required system work such as cleanup,
ledger settlement, provider-handle persistence, or compensation for already
created effects. A later authority change must not strand durable work that the
system is obligated to settle. Conversely, do not add feature-specific
compensation when ordinary lifecycle handling already settles admitted work
safely.

## Bound review-driven accretion

Pause before another patch when any condition holds:

- three or more consecutive review-fix commits address the same concern;
- a new helper needs another helper for cleanup, retry, or compensation;
- UI synchronization needs its own convergence state machine;
- the diff has roughly doubled since the initial implementation;
- one feature now touches unrelated domains; or
- fixing each race exposes a narrower race at the next boundary.

At that point, recommend a semantic or architecture review. Identify the hidden
contract that makes every edge case appear mandatory and propose a narrower
boundary before changing more code.

## Keep rollout machinery temporary

Prefer correct new writers plus a one-time backfill or clamp. Use permanent
database triggers for permanent invariants, not merely for a short mixed-version
window. Avoid trigger chains that rewrite related audit payloads when a
correction event or read-time projection is sufficient. Call out rollout
infrastructure that would become permanent product complexity.

## Test the behavior

Reject source-text tests that assert strings or ordering when a behavioral seam
exists. Prefer tests proving that:

- denial occurs before durable or external effects;
- direct bypasses fail at the authoritative seam;
- already-admitted system settlement remains safe; and
- transition semantics remain stable while implementation details can change.

## Produce a keep/cut assessment

For a complex diff, report:

1. intended invariant;
2. threat model;
3. chosen admission and transition semantics;
4. authoritative controls to keep;
5. UX or defense-in-depth machinery to cut;
6. tests to retain or replace;
7. rollout complexity that can be one-time;
8. estimated post-simplification surface area; and
9. risks explicitly accepted by the simpler design.
