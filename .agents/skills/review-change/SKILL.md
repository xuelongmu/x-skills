---
name: review-change
description: Review a local change or PR for correctness, resulting design, and sufficient verification. Return evidence-backed findings without editing or publishing.
---

# Review a change

Assess the change that will ship against the user's intent and repository
requirements. Review-only requests authorize inspection and non-mutating checks,
not edits, checkout changes, PR writes, or publication.

## Review basis

Establish intent and the comparison point from the request, PR, and applicable
repository guidance. Use the explicit base, the PR's actual base, or the verified
upstream default; inspect the merge-base diff plus in-scope worktree and
untracked changes. Include affected consumers and contracts where needed.

If a missing base or requirement prevents a verdict, say what is unknown and
report observations that remain valid. Do not turn a narrow uncertainty into
a reason to abandon the rest of the review.

## Findings

Investigate the risks the change actually introduces. For a consequential or
unfamiliar area, consult the relevant entries in
[risk lenses](references/risk-lenses.md); routine reviews need no additional
skill or fixed sequence of passes.

A finding needs a concrete input or failure path, evidence that it violates the
intended behavior, and a useful repair. Check existing guards and tests before
reporting it. Review the resulting responsibilities and contracts as well as
edited lines. Treat automated review as a hypothesis, and deduplicate symptoms
under their cause.

Investigate without a severity cutoff; prioritize substantiated findings when
reporting. Use P0 for critical widespread harm, P1 for serious likely failures,
and P2 for meaningful correctness, reliability, or maintainability issues.
Omit stylistic nits unless requested. Unproven concerns and missing evidence
belong under uncertainty, not confirmed defects.

For explicit overengineering audits or repeated fixes inside earlier review
fixes, `review-complexity` can help when available. Use its conclusions as
evidence rather than requiring a second verdict. Its absence does not block
review.

## Evidence and result

Reuse applicable verification already performed. Probe unresolved material
claims when practical; broaden testing only when the risk or new evidence
justifies it. Tests of extracted helpers may not establish that a multi-step
flow actually progresses. Missing browser evidence is a verification gap, not
automatically a code defect.

Lead with `Ready`, `Not ready`, or `Inconclusive`, followed by findings with
tight file/line locations, impact, and repairs. Include the scope and material
verification results or gaps; omit empty boilerplate sections. Identify stale
guidance only when the change makes it relevant.

External review requires authorization covering the artifact, recipient, prompt,
and data or cost boundary. Reuse applicable authorization; reconcile external
claims against local evidence. Review never implicitly authorizes exporting
repository content.
