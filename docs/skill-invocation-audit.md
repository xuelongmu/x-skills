# Skill invocation audit

This audit selects by requested outcome and current phase. A skill can own the
task or support a bounded step; mentioning a technology does not establish either
role. Frontmatter must communicate likely discovery boundaries before the body
is loaded. Explicit invocation still loads the skill, with its guidance applied
within the user's scope and existing authorization. Exclusions constrain implicit
selection; they do not disable explicit invocation or needed supporting guidance.

## Owned inventory

All thirteen sources are canonical under `.agents/skills/`. Seven descriptions
changed; six already distinguish the intended outcome sufficiently. No changes
disable implicit invocation, impose approval gates, or alter installation scope.

| Skill | Audit result and boundary |
| --- | --- |
| browser-evidence | Changed description and opening scope. Specific UI verification or visual capture owns the browser step, not an entire campaign for a product with a web UI. Ordinary browser operation alone does not require evidence collection. |
| capture-learning | Changed description. A solved problem must yield a verified, reusable constraint worth preserving; a routine fix or status recap does not automatically launch durable capture. The existing body already tests whether capture is worthwhile. |
| steward-research | Changed description and opening scope. Reproducibility assessment, organization, or handoff is the outcome; running a product test or benchmark alone is insufficient. Provenance work can support an experiment without replacing its protocol. |
| orchestrate | Changed description. Delegated tasks or workers require coordination; a task with many steps does not automatically require delegation. |
| review-change | Changed description and complexity routing. A requested or distinct code-review phase is different from routine implementation verification or critique of a proposed architecture. Supporting complexity review requires evidence of accumulating complexity. |
| review-complexity | Changed description. Requested simplification or a complexity audit applies; repeated review fixes can justify support when they indicate accumulating complexity. Review comments or an ordinary bug fix alone are insufficient. |
| land | Changed description. Requested landing owns publication and maintenance through merge; publication alone routes to publish, maintenance alone to babysit. Requested Slack sharing remains a supported separate endpoint. |
| publish | Retained. The description already selects pushing or publishing a PR; the body excludes merge and ongoing monitoring. |
| babysit | Retained. Existing PR maintenance or requested monitoring is explicit, and merging is excluded. |
| design-architecture | Retained. Consequential open system choices are explicit; routine implementation planning is excluded, and the body routes proposal critique separately. |
| review-architecture | Retained. Assessment of a proposed design before acceptance is explicit; ordinary code review is excluded. |
| google-developer-style | Retained. English developer documentation is the writing artifact, with project style precedence. Merely reading documentation does not match the described actions. |
| show-me | Retained. A requested diagram or a visual that materially aids understanding is a useful supporting outcome. The body already preserves the caller's scope and authority. |

The optional UI descriptions and default prompts match these outcomes. Resource
references remain conditional. The two service-specific orchestration skills and
their prompt template have been removed from the project; general coordination
remains available. The remaining selection guidance is portable across hosts.

## Local decision walkthrough

The following is a manual review of selection using the revised descriptions,
followed by a body consistency check. The decisions below are the walkthrough's
results, not results from executing these workflows or measuring an independent
agent. All cases were consistent with their intended scope after the changes.
They also form reusable inputs for the independent evaluation procedure in
[skill-evaluation.md](skill-evaluation.md); withhold the decision column when
evaluating another agent.

| Kind | Request and current phase | Selection decision and scope |
| --- | --- | --- |
| Positive | Verify that a completed generation updates the displayed balance and capture proof. | browser-evidence owns this UI check; the expected balance comes from the task's billing contract. |
| Negative | Stress-test a web product through its existing API under an approved spending cap; currently generating load. | Domain testing and billing guidance own the campaign. No browser-evidence or research stewardship merely from the product or test context. |
| Mixed phase | Run that campaign, then verify quote, generation, and balance in the UI and reconcile the ledger. | browser-evidence supports only the UI verification step. Domain runbooks own reconciliation and spending; implementation tracking stays with its existing workflow. |
| Negative | Open the project settings page and change an already authorized preference. | Use browser control as needed; no evidence workflow merely to operate the UI. |
| Explicit | Use $browser-evidence to capture the settings page. | Load the explicitly named skill and capture the requested evidence; do not invent a wider testing campaign. |
| Positive | Preserve the verified cause and guard for a recurring retry defect in its owning runbook. | capture-learning owns durable preservation; an existing regression test may already be sufficient. |
| Negative | Fix a spelling error and report what changed. | Ordinary edit and report; no capture-learning solely because a fix finished. |
| Ambiguous | Capture our theory that a timeout caused duplicate billing; the cause is still unverified. | The capture request selects capture-learning, whose body prevents promoting the theory to a durable rule and identifies missing evidence. |
| Positive | Audit whether these experiment records can reproduce the reported result for handoff. | steward-research owns a read-only reproducibility audit; it does not rerun experiments by default. |
| Negative | Run the existing benchmark once and tell me the throughput. | Benchmark execution and reporting; no automatic research reorganization. |
| Mixed phase | Run the benchmark and prepare its inputs, environment, and results for another researcher to reproduce. | Execution follows the benchmark protocol; steward-research supports the requested provenance and handoff. |
| Positive | Lead two authorized workers implementing independent backend and UI deliverables. | orchestrate owns delegation boundaries and dependencies. |
| Negative | Implement a three-step fix across backend, UI, and tests in this task. | Local implementation; multiple steps and components alone do not select orchestrate or authorize workers. |
| Positive | Review this PR's correctness and test coverage without editing. | review-change owns the verdict, with only relevant risk lenses. |
| Negative | Fix the bug and run its regression tests. | Implementation and verification; no separate review-change workflow merely because tests are run. A required later review phase can still select it. |
| Positive | Simplify duplicated fallback state while preserving accepted behavior. | review-complexity applies and edits are in scope. |
| Mixed phase | A PR review reveals each previous fix adds a new guard around the last guard. | review-change may use review-complexity for the evidenced accumulation, without requiring a second independent verdict. |
| Negative | Address one review comment correcting a missing null check. | The owning fix or PR-maintenance workflow handles it; a review comment alone does not require a complexity audit. |
| Positive | Push this fix and open a PR. | publish owns publication and stops there; reading shared land references does not authorize landing. |
| Positive | Keep the PR healthy until tomorrow without merging. | babysit owns requested maintenance and monitoring, preserving the duration and notification intent. |
| Positive | Land this fix, opening the PR if needed. | land owns publication, maintenance, and merge subject to the repository's existing gates. |
| Ambiguous | Share this PR in Slack; no landing request. | land uses its sharing mode only, preserving the existing draft/send authorization rules. It does not enter merge gates. |
| Positive | Choose the durable-state owner before implementing a cross-service workflow. | design-architecture owns the consequential open choice. |
| Negative | Implement the already accepted field rename. | Routine implementation; no architecture workflow solely because a schema changes. |
| Positive | Assess this draft ADR's cancellation and recovery semantics. | review-architecture owns proposal assessment; ordinary code-review output is not the requested artifact. |
| Positive | Rewrite this API guide for developers. | google-developer-style supports the documentation artifact, subordinate to project guidance. |
| Negative | Read the API guide to identify the supported request field. | Reading for facts does not select a documentation-writing workflow. |
| Positive | Explain the queue's retry and acknowledgement paths with a diagram. | show-me supports visual explanation, without granting edit or external-write authority. |
| Negative | Report the result of a one-line identifier fix. | A short report suffices; show-me is not automatic for any technical change. |

## External ownership boundary

The referenced project-specific model-integration skill belongs to another
repository, and a separate task owns its implementation. Its intended boundary
selects adding, changing, retiring, or
explicitly auditing catalog entries, schemas, routing, pricing configuration,
or cross-model media behavior. Executing an existing model or looking up provider
cost to enforce an authorized cap does not select the integration workflow.
It is a motivating example here, not a new portable skill or an edit
to the active external checkout. Billing runbooks, domain testing strategy, and
issue tracking also remain with their owning project; this audit does not
replace or claim to validate those workflows.

These additional local decision checks describe the intended external boundary;
they do not validate the separately owned implementation:

| Kind | Request and current phase | Selection decision and scope |
| --- | --- | --- |
| Positive | Add a model, update its schema or pricing configuration, change routing or media behavior, or retire a catalog entry. | model-integration owns the authorized integration change and relevant protocol sections. |
| Positive | Explicitly audit catalog schemas and configured pricing for drift. | model-integration owns inspect-and-report audit scope; no catalog edits are implied. |
| Negative | Generate with an existing model during a billing test. | Domain testing owns execution; use no full integration workflow. |
| Negative | Look up the provider's unit cost to keep the authorized run below its cap. | Retrieve the relevant pricing facts for budget enforcement; no integration audit or configuration change is implied. |
| Mixed phase | The test exposes a wrong catalog multiplier; fixing discovered billing defects is already in scope. | Use model-integration for the configuration correction, then return to the test campaign. No redundant permission request is needed for the authorized fix. |
| Ambiguous | Check pricing during the run. | Use the conversation's purpose: cost estimation stays in testing; an explicit configuration audit selects integration. Clarify only if that distinction remains material and unresolved. |
| Explicit | Use $model-integration to check the existing model's test setup. | Load the named skill and apply relevant guidance within the test scope; do not infer authorization for catalog mutation or launch unrelated integration procedures. |

These thirty-six cases check discovery and scope under supplied facts. They do not
establish live browser, provider, or PR behavior, or cross-host/model routing
accuracy. Packaging and resource checks are run separately as described in
[skill-layout.md](skill-layout.md).

Validation for this change passed all 37 repository tests, including the layout,
metadata, relocated-resource, and watcher checks. The skill-authoring validator
also passed for all seven changed skills. Validation of the external integration
skill's implementation belongs to its separate task.
