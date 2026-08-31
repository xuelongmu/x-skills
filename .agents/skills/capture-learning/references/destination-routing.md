# Learning Destination Routing

Choose the authority that should make a future mistake less likely. Follow the
repository's existing locations, formats, owners, and lifecycle; the examples
below are categories, not prescribed paths.

## Route by the job the learning must do

| Destination | Choose it when | Required shape |
|---|---|---|
| Regression test or executable check | A confirmed defect or constraint can be exercised at the behavior's owning seam. | Reproduce the failure without the fix, pass with it, and avoid encoding incidental implementation details. A test may be the entire capture. |
| Existing skill | The reusable workflow is already owned by a skill but its instruction, gate, or routing is incomplete or stale. | Update the canonical skill and any directly related reference or metadata; do not add a second skill for the same decision. |
| New skill | A repeatable, non-obvious workflow recurs across tasks or repositories and no existing skill owns it. | Keep discovery precise, preserve authorization boundaries, and follow the repository's skill creation and validation process. Do not create a skill for a single repository fact. |
| Operations or runbook documentation | Operators need a repeatable diagnostic, recovery, rollback, or maintenance procedure. | State prerequisites, safe steps, verification, stop conditions, and escalation. Keep architectural rationale in its ADR. |
| ADR | The learning establishes or changes a durable architecture, responsibility, interface, data-model, platform, or hard-to-reverse technical decision. | Use the repository's ADR process, status, and supersession rules. A decision that changes architecture routes to an ADR rather than a skill or generic learning note. |
| Dated system documentation | The learning describes current topology, deployed state, inventory, capacity, or another fact that will drift over time. | Include the observation date, evidence source, scope, and refresh owner or method. Do not present a dated observation as an invariant. |
| Service contract | Producers and consumers need a stable boundary: schema, errors, ordering, compatibility, idempotency, ownership, or versioning. | Update the canonical contract and verify affected callers or consumers. Put rationale in an ADR only when it is an architectural decision. |
| Repository instructions | The rule applies broadly to future work in the governed tree and agents must see it before acting. | Add the narrowest durable directive to the nearest authoritative instruction file. Do not paste a runbook or duplicate a skill. |
| Issue tracker | The learning identifies necessary work that is not implemented or verified in the current scope. | Record the evidence, impact, acceptance condition, and owning area only with authorization to create or update the external record. |
| PR or commit context | The fact explains why a specific change was made but does not govern future work independently. | Put it in the authorized change description or commit context. Do not promote change-local history into a repository-wide rule. |
| No durable change | The fact is one-off, obvious from the current authority, cheaply rediscovered, sensitive, unresolved, or too narrow to change future behavior. | Return the receipt with `Destination: No durable change`; do not create an artifact for completeness. |

## Resolve overlaps

Prefer executable enforcement over prose when it completely expresses the
invariant. Use a companion document only when future engineers also need
procedure, scope, rationale, or ownership that the test cannot convey.

When several destinations appear plausible, identify the primary owner:

- decision rationale lives in an ADR; the resulting boundary lives in the
  contract;
- an operational procedure lives in a runbook; its regression guard lives in a
  test or check;
- a workflow lives in a skill; repository-specific facts stay in the
  repository authority the skill discovers;
- unimplemented work lives in the issue tracker, not as present-tense guidance.

Update cross-references only when they improve discovery. Do not duplicate the
same rule across every authority.

## Supersede cleanly

Before adding content, search for equivalent, narrower, stale, or conflicting
guidance. Update it in place when it has the right authority. If the repository
preserves historical decisions, use its explicit supersession mechanism rather
than silently rewriting history. Remove or correct stale links and path names
that are directly in scope; report broader drift separately.
