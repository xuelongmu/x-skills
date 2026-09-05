---
name: review-complexity
description: Audit overengineering or simplify a change while preserving accepted behavior. Use for explicit complexity reviews or accumulating review-fix chains; edit only when changes are requested.
---

# Review complexity

Improve clarity and maintainability while preserving accepted behavior. A review
request produces findings; a simplification or fix request authorizes in-scope
edits. Fewer lines alone are not evidence of improvement.

Establish scope and intended behavior from the request, applicable repository
guidance, diff, and affected consumers. Consult relevant task history when
decisions are missing and the host exposes it; otherwise use the conversation
or a supplied export. Do not scan unrelated tasks.

## What to challenge

Ask what requirement each mechanism serves, where the invariant belongs, and
what would fail if it disappeared. Prefer one owner, direct control flow, and
existing boundaries over duplicated state, pass-through layers, speculative
frameworks, or defenses for unreachable states.

Preserve justified complexity around authorization, exact money, durable state,
idempotency, external contracts, and compatibility. Account for any invariant
whose only enforcement would be deleted. A proposal that changes accepted
behavior is a design decision, not a behavior-preserving cleanup.

Automated feedback is evidence to evaluate, not a new product requirement.
Distinguish a real defect from a stronger unstated contract, optional polish,
or a speculative edge case. When fixes repeatedly expose problems inside earlier
fixes, reconsider ownership or semantics before adding another guard.

Use supporting detail only where it changes the assessment:

- [Review archaeology](references/review-archaeology.md) for accumulated review
  fixes whose origins or contract assumptions need investigation.
- [Transition semantics](references/transition-semantics.md) when changing
  admission, revocation, or other state transitions could affect in-flight work.

## Repair and report

Prefer deleting unnecessary work before abstracting it. Keep useful testing and
provider seams; avoid unrelated style churn, public API growth, and historical
migration rewrites.

Before editing, identify the behavior that must remain true and relevant existing
evidence. Verify changed behavior proportionately, reusing passing checks when
their inputs are unchanged. Add regression tests when they protect an actual
contract; disposable probes need not become permanent files.

Prioritize a few substantial recommendations. For each, give the location,
evidence, retained invariant, and recommended alternative. Distinguish
safe simplifications from decisions requiring changed requirements, and explain
important complexity that should stay. For edits, report what changed and the
verification or unresolved limits. If the original is clearer, leave it alone.
