# Architecture review lenses

Select concerns at the depth the artifact's maturity and consequences warrant.

| Concern | Question |
| --- | --- |
| Premise and grounding | Does the proposal solve the requested problem in the system that exists? Does an accepted decision already settle the premise? |
| Hidden commitments | Which ownership, boundary, state, execution, or compatibility decisions would otherwise become accidental contracts? |
| Assumptions | What is supported, testable, contradicted, or unknown, and what changes if the claim is false? |
| Alternatives | Is a smaller change viable? Are proposed alternatives materially different architectures? |
| Failure | Who handles partial, duplicate, replayed, timeout-with-unknown-outcome, or poisoned work? |
| Evolution | How do mixed versions, migration, reversal, and accumulated state behave? |
| Operations | Is repair ownership and diagnostic evidence sufficient? Are cost or scale claims grounded? |
| Simplicity and constraints | Does each new subsystem justify its cost and preserve the repository's declared invariants? |

An early requirements brief can leave mechanisms open. A technical plan must
settle cross-boundary semantics that determine feasibility or compatibility.
An ADR draft needs a clear decision, evidence, alternatives, and consequences;
an assumption that could invert the choice needs resolution before acceptance.
A supersession proposal must explain the changed basis and transition.

Silence is a finding only when the missing decision belongs at this maturity and
could change feasibility, safety, or contract behavior. For a timeout concern,
name the unknown state and affected effect; for a migration concern, name the
incompatible producer, consumer, schema, or deployment state.
