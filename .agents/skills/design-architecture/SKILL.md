---
name: design-architecture
description: Explore consequential choices in system boundaries, ownership, durable state, execution, or public contracts before implementation. Use when important choices remain open, not for routine implementation planning.
---

# Design architecture

Recommend a repository-grounded architecture for the decision the user needs to
make. Expose expensive commitments, credible alternatives, and the evidence that
could change the recommendation.

Read the relevant current system and its accepted constraints before proposing
a replacement. Separate verified facts, uncertain claims, and choices requiring
judgment. Check current primary sources when platform guarantees determine
feasibility; familiarity is not evidence of an external contract.

## Compare consequential choices

Identify the source of truth, write ownership, boundaries, and public or durable
contracts affected. Include the status quo or an incremental change when viable.
Compare materially different architectures only when such alternatives exist;
different libraries inside one ownership model are implementation variants.
Do not invent alternatives to fill a quota.

Trace the failure, evolution, migration, and recovery scenarios that distinguish
the options. Preserve declared project invariants without importing a universal
checklist of products or platforms. Ground quantitative claims in measurements,
targets, or labeled assumptions.

Consult [decision surfaces](references/decision-surfaces.md) for unfamiliar
territory or overlooked commitments, and
[consequence analysis](references/consequence-analysis.md) when comparing
failure or migration behavior needs more structure. Neither is a mandatory form.

Recommend a direction and explain its dominant trade-offs, accepted complexity,
reversibility, and invalidating assumptions. When the user cannot evaluate an
unfamiliar area, supply grounded options and a recommended default rather than
asking them to invent domain facts.

## Deliver the decision

Use the repository's existing format if one applies; otherwise return a concise
brief covering the decision, evidence, alternatives, recommendation, and open
proofs or judgments. Omit sections that do not help the decision.

Use `show-me` when available if a visual clarifies ownership, failure paths,
choices, or migration. Otherwise explain directly; distinguish evidence from
proposals and assumptions.

A design-only request ends with the brief. Do not mark a proposal or ADR accepted
on the user's behalf. If implementation is also requested or an approved
direction already exists, continue the authorized work; ask only about material
unresolved choices. Use the repository's ADR process when recording an accepted
durable decision, without inventing a new documentation hierarchy.

For critique of an existing proposal, use `review-architecture` when available
or perform the requested assessment directly. Missing sibling skills do not
block useful work.
