---
name: show-me
description: Explain a technical system, decision, change, or failure visually. Use for requested diagrams or when a visual helps the reader understand.
---

# Explain visually

Use a visual when it materially clarifies a relationship, sequence, state,
ownership, boundary, migration, or comparison. Choose the format and level of
detail for the question and audience. Place the view beside the explanation
it supports.

Possible formats by question:

| Question | Representation |
| --- | --- |
| Logic | Pseudocode |
| Runtime flow | Call tree |
| Responsibility | Component or file tree |
| Cross-service or asynchronous interaction | Mermaid sequence diagram |
| Lifecycle and legal transitions | State diagram |
| Data ownership, custody, or security | Data-flow or trust-boundary diagram |
| Migration coexistence, cutover, and rollback | Timeline |
| Before-and-after structure | Diff-oriented component, file, call, or state view |
| Consequential alternatives | Tradeoff matrix |

Include the relationships and context that help the reader understand. Distinguish
observed facts, proposals, assumptions, and inferred edges in labels or adjacent
prose. Do not silently supply a missing boundary or imply an uncertain call is
verified.

Use HTML when its layout or interaction adds value. Use available host display
capabilities; do not assume a specific
client or operating system. An existing visualization tool can render the view.

When used within another skill, preserve its scope and authority. The caller
owns the finding, decision, or durable capture. A visual explanation does not
authorize repository edits or external writes; keep review-only output in the
response unless artifact creation was requested.
