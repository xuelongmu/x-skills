---
name: capture-learning
description: Preserve a verified, reusable engineering learning in the repository authority that owns it. Use after a non-obvious problem is solved or when asked to capture a learning.
---

# Capture a verified learning

Make the smallest durable change that prevents rediscovery or recurrence.
Capture only what the evidence establishes: the cause or constraint, why the
resolution works, and its verified scope. An unresolved hypothesis does not
become a rule merely because it motivated a successful-looking fix.

Search existing guidance and enforcement before adding content. Reuse the
investigation already completed; consult code, tests, or history only to resolve
gaps or contradictions relevant to the learning.

A durable change is worthwhile when recurrence is plausible, rediscovery is
expensive, the constraint is non-obvious, or an existing safeguard or instruction
is missing or misleading. Otherwise explain briefly why nothing was captured.

## Put it where future work needs it

Update the authority that owns the behavior. A regression test may be the entire
capture. Use [destination routing](references/destination-routing.md) only when
ownership is unclear. Prefer an existing rule, contract, runbook, or skill over
a parallel archive. Follow the repository's ADR process for architectural
decisions and preserve accepted history.

Write the invariant, scope, safe behavior, and the evidence or enforcement that
supports it. Include rejected alternatives only when someone is likely to retry
them. Omit debugging chronology, generic advice, sensitive payloads, and
unverified claims.

Validate the changed authority with relevant repository checks and correct
directly affected stale references. Report broader unrelated cleanup separately.
Capturing authorizes the in-scope local knowledge or safeguard change; commits,
publication, external records, and unrelated cleanup need their own authorization.

Return what was learned, where it was captured, and material evidence or limits.
If no durable change qualifies, say so without manufacturing a receipt or file.
