---
name: review-architecture
description: Assess a proposed architecture, technical plan, or ADR for consequential decisions, assumptions, and risks. Use for design review before acceptance, not ordinary code review.
---

# Review architecture

Assess whether the proposal can advance at its stated maturity. A review request
is report-only; recommendations do not accept a design, change files, or publish
records.

Establish the proposal's intended outcomes, current system, and applicable
repository constraints. A requirements brief and an ADR draft have different
completeness obligations. Revisit an accepted decision only when new evidence,
changed constraints, or an explicit supersession request gives a basis.

## Assess the proposal

Look for implicit commitments, unsupported assumptions, failure semantics,
migration costs, and unnecessary subsystems. Consult
[review lenses](references/review-lenses.md) only where the proposal's risk or
maturity needs a deeper check. Do not demand implementation mechanics from an
early brief, or allow a mature plan to defer decisions that determine feasibility
or contract behavior.

Distinguish a judgment call, such as who owns writes, from a testable claim,
such as provider retry behavior. Check consequential external claims against
current primary sources. Consider credible alternatives that change ownership,
boundaries, state, or execution; suppress library preferences and speculative
scaling stories without evidence.

A finding needs the proposal claim or omission, evidence or a labeled assumption,
a concrete consequence, and the decision or revision needed. Missing information
is blocking only when it prevents a responsible judgment.

## Return the assessment

Lead with `Sound`, `Revise`, or `Blocked by unknowns`. Explain consequential
findings and what must change or be proven, with references. Include important
hidden decisions, alternatives, and reversal costs when relevant. Scale the
report to the decision; no fixed matrix or empty sections are required.

Use `show-me` when available to clarify the proposal against a failure path,
missing state, or boundary. Otherwise explain directly, labeling assumptions
and inferred edges. A diagram supports the finding; it does not establish it.

Explore alternatives with `design-architecture` when available and requested;
otherwise provide useful analysis directly. Do not expand a review into an
unrequested redesign. Record accepted decisions through the repository's ADR
process only when authorized.

External review needs authorization covering the artifact, recipient, prompt,
and data or cost boundary. Reuse applicable authorization and reconcile any
external findings against local evidence.
