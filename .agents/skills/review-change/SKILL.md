---
name: review-change
description: Review a local change, pull request, or pre-publish diff against its intent, resulting design, verification, and diff-selected risks. Use for self-review, PR review, or a readiness audit. Review-only use never edits or publishes; return Inconclusive when the specification or correct base cannot be established.
---

# Review a Change

Produce a high-signal review of the change that will actually ship. Establish
what the change is meant to do, inspect the resulting system rather than only
the edited lines, and investigate only the risk lenses the diff activates.

## Keep review separate from mutation

A review-only invocation may read local and authorized remote context and run
non-mutating verification. It must not edit files, stage, commit, push, merge,
open or update a pull request, file an issue, submit a review, or create another
external record. A request to fix findings is separate authorization; preserve
the repository's normal issue, branch, commit, PR, and publish workflows.

Do not treat a PR number, URL, branch, or base as permission to check out or
modify it. Stay in the current checkout unless the user separately requests a
workspace change.

## Establish scope and intent

Before judging the code:

1. Read repository instructions that govern every changed path.
2. Identify the request and the authoritative specification from the supplied
   issue or PR, acceptance criteria, ADRs, service contracts, and current
   conversation. Distinguish requirements from implementation commentary.
3. Resolve the correct base. Prefer an explicit base, then the PR's actual base,
   then the repository's verified upstream default. Confirm the ref resolves and
   review the merge-base diff, commit range, worktree changes, and in-scope
   untracked files. Do not assume `main`, `origin`, or `HEAD~1`.
4. Read the changed tests and the exact verification evidence already produced.
5. Inspect directly affected callers, consumers, schemas, generated artifacts,
   and documentation needed to validate behavior beyond the diff.

If the specification or correct base cannot be established, return
`Inconclusive`. Explain what is missing and report only observations that remain
valid without guessing the intended behavior or comparison point.

## Run separate review passes

### 1. Intent and correctness

Trace each requirement to the changed behavior. Check happy paths, error paths,
state transitions, boundary values, and the absence of unintended behavior.
Read tests as evidence, not as the definition of correctness. Look for missing
requirements, scope creep, incorrect implementation, and behavior that existing
tests could not detect.

### 2. Resulting design

Review the codebase after the change: responsibilities, interfaces, data flow,
failure semantics, and operational cost. Check whether complexity was removed,
moved, or duplicated; whether new abstractions protect a real seam; and whether
the change leaves one clear owner for each invariant. Preserve justified
complexity around tenancy, authorization, exact money, idempotency, durable
state, external providers, and compatibility.

### 3. Conditional risk lenses

Read [references/risk-lenses.md](references/risk-lenses.md), select lenses from
concrete diff signals, and state why each selected lens applies. Do not run
every specialist concern against every change. A trivial documentation-only
diff does not activate generic security review merely because security is an
available lens.

## Validate findings

Before reporting a finding:

- tie it to actual changed code or a directly affected caller, test, contract,
  or generated artifact;
- describe a concrete input, sequence, actor, or failure path;
- confirm the repository authority or intended behavior it violates;
- inspect existing tests and guards that might already prevent it; and
- reproduce or probe the path when practical without mutating the reviewed
  change.

Treat automated or external review output as a hypothesis. Re-read the artifact
against every claim. Deduplicate related symptoms under their root cause and
omit speculative nits, personal style preferences, and concerns already
enforced by tooling. If evidence is insufficient, place the item under residual
risk or a verification gap rather than presenting it as a defect.

Use impact-based severity:

- **P0:** tenant isolation, security, data loss or corruption, or systemic
  failure with critical blast radius;
- **P1:** likely correctness, authorization, billing, or irreversible-data
  failure;
- **P2:** meaningful reliability, operability, or maintainability regression;
- **P3:** optional polish; normally omit it.

For each finding, provide a tight path and line, the failure scenario, evidence,
impact, and the smallest coherent repair. Severity reflects impact and
likelihood, not review confidence or author preference.

## Audit the verification story separately

Record exact commands and results, the environment, manual or browser evidence,
and deliberately omitted layers. Check that the evidence exercises the changed
behavior and important composition paths. Missing browser or manual evidence
for changed visible behavior is a verification gap, not automatically a code
finding. Judge whether each gap is acceptable from the change's risk; never
claim a layer passed when it was not run.

Product and release testing remain with the repository's specialized QA
workflow. This review evaluates whether the available story is sufficient and
names the residual risk; it does not replace that workflow.

## Report knowledge impact

Identify guidance, contracts, tests, or skills made stale by the change. List
only verified candidates for `capture-learning`: solved, evidenced, reusable
knowledge that passes that skill's gate. In review-only mode, report candidates
without editing or invoking a write workflow.

## Keep external review opt-in

External or cross-model review requires opt-in for each invocation. Before any
code or context leaves the current environment, disclose the exact artifact,
prompt, recipient tool or model, and expected cost or data boundary. Prefer a
read-only sandbox and send only the minimum necessary material. Never silently
export code, reuse authorization from an earlier invocation, or treat an
external verdict as authoritative.

Local multi-agent review is optional, not a prerequisite. Use it only when the
host, user, and change complexity justify it; this skill does not require
fan-out or a fixed reviewer roster.

## Return the review

Use one verdict:

- **Ready:** intent and base are established, no material finding remains, and
  verification is proportionate to risk;
- **Not ready:** a confirmed material finding or blocking verification gap
  remains; or
- **Inconclusive:** intent, base, or essential evidence cannot be established
  without guessing.

Report in this order:

```text
Verdict: Ready | Not ready | Inconclusive
Scope and intent: <base, diff, specification, and applicable instructions>
Findings: <P0-P2 findings ordered by severity, or "none">
Verification: <exact evidence, gaps, deliberate omissions, and environment>
Knowledge impact: <stale guidance and capture-learning candidates, or "none">
Residual risks: <accepted or unresolved risks, or "none">
```
