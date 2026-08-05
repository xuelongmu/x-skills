---
name: author-ao-orchestrator
description: Draft, critique, and validate a project-specific Agent Orchestrator coordinator prompt from a project brief, issue graph, or existing draft. Return an explicit GO or NOT READY verdict without mutating live work.
argument-hint: "[project brief, issue range, or draft prompt]"
---

# Author an Agent Orchestrator Prompt

Use the request in `$ARGUMENTS` to produce an executable coordination contract,
not a narrative plan. Separate reusable AO behavior from project facts and
temporary driver decisions.

Do not mutate issues, labels, branches, PRs, sessions, or repository files while
authoring unless the user separately asks for those changes.

## Workflow

1. Read the target repository's complete binding instructions:
   - every applicable `AGENTS.md`;
   - workflow and contribution documents referenced by it;
   - worker playbooks named by the proposed prompt.
2. Read the live project brief and full issue records when the plan comes from
   Linear, GitHub, or another tracker. Include relations, status, labels,
   Areas/scope, and decision comments.
3. Inspect the installed AO version when the prompt depends on its behavior.
   Check tracker access, worker spawn/base-branch support, persistent worker
   ownership, raw review-thread visibility, external reviewer reruns, merge
   operations, and worktree cleanup.
4. Build an issue matrix before drafting. Give every issue exactly one direct
   base, dispatch gate, persistent worker, PR, merge authority, and completion
   gate.
5. Define repeated predicates once: `VERIFY`, `IN_FLIGHT`, `REVIEW_CLEAN`,
   `HUMAN_GATE`, `READY`, and `DONE`, as applicable.
6. Resolve contradictions and unsupported operations. Name an authorized
   fallback or return `NOT READY`; never hide a capability gap behind confident
   wording.
7. Remove unused sections and placeholders from the final prompt.
8. Run the readiness checklist and return an explicit verdict.

## Drafting Rules

- Rely on AO's injected orchestrator role for generic coordination behavior.
  Reinforce the coordination-only boundary in one sentence.
- Preserve project-specific issue IDs, dependency edges, exceptions, recorded
  decisions, verification commands, and spend restrictions.
- Use a table for three or more issues.
- Distinguish direct parents from transitive ancestors. A child issue may
  dispatch before its parent merges by stacking a PR on the parent's open
  branch; when a parent merges, resume and retarget only direct children, then
  rerun `VERIFY` and require current-head evidence before they become ready.
- A human review gate blocks merging by default, not building. Keep dependent
  issues moving as stacked PRs unless the gated question could change what the
  gated issue itself or its dependents build, and say so when a gate blocks
  building too.
- Never tell a worker to build a synthetic merge of unmerged parents.
- Replace words such as "stagger", "clean", "done", "wait", and "every state
  change" with observable conditions, owners, and timeouts.
- Keep one persistent worker session and one PR per issue through
  implementation, CI, review, rebase, and merge.
- Express collision rules using repository Areas or coordination surfaces
  rather than guessed file overlap.
- Treat migrations, one-time backfills, and shared-data ownership changes as
  data/schema-sensitive even when an issue omitted that Area.

## Required Capability Fallbacks

When AO lacks a requested native operation, require one explicit alternative:

- Tracker: name the authenticated connector or CLI and require a live read
  before mutation.
- Stacked branch: give the exact clean-worktree fetch/base procedure that runs
  before edits.
- Review rerun: name the trigger owner, evidence of completion, spend policy,
  timeout, and escalation action.
- Merge: name the authorized UI, API, or CLI path and require an
  exact-current-head recheck immediately before merging.
- Cleanup: distinguish remote branch deletion from AO's safe worktree cleanup;
  never force-delete a dirty worktree.

If no authorized fallback exists, return `NOT READY`.

## Readiness Checklist

Return `GO` only when all of these hold:

- Repository instructions were read and each exception is narrower and
  higher-authority than the rule it overrides.
- Every issue exists in the stated project/team and is dispatchable or has a
  measurable future gate.
- Current labels and decision comments support every claimed clearance.
- The dependency graph is acyclic and matches live blocked-by relations.
- Every issue has exactly one direct base and every multi-parent issue has an
  explicit integration strategy.
- Stack creation is natively supported or has a safe pre-edit fallback.
- One issue maps to one persistent worker and one PR.
- `IN_FLIGHT` identifies exactly which sessions consume concurrency.
- Every shared-area mutex has an explicit capacity.
- Declared Areas match the described work, including backfills and shared-data
  changes.
- `REVIEW_CLEAN` names blocking reviewers/findings, requires current-head
  evidence, defines rebuttal/resolution, and owns the follow-up trigger.
- The prompt does not assume AO's merge-readiness calculation is stricter than
  it actually is.
- Merge authority is mutually exclusive and includes allowlists, exclusions,
  gates, and the exact merge mechanism.
- Human gates state whether they block building, merging, or both.
- Spend, secrets, shared-data, workflow-file, and destructive-operation stops
  are concrete.
- Every wait has an owner, observable completion event, timeout, and escalation
  path.
- Safe unrelated work — and dependent work that can stack — continues while
  one lane waits.
- Reporting covers meaningful milestones rather than low-level mutations.
- The completion condition cannot end while safe runnable work remains.

## Output

Return:

1. `Verdict: GO` or `Verdict: NOT READY`.
2. `Evidence checked` listing repository, tracker, GitHub, and AO capability
   sources.
3. `Blocking corrections` containing only execution blockers.
4. `Warnings` containing non-blocking ambiguity or conservatism.
5. `Final orchestrator prompt` only for `GO`. For `NOT READY`, provide a
   corrected draft clearly labeled as not yet executable.

Use this structure for a final prompt, deleting unused sections:

```markdown
Coordinate `<project>` (`<team>`, `<issue set>`) through Agent Orchestrator.
Stay coordination-only; implementation and PR ownership belong to workers.

## Authority and preflight

Read `<binding files>`. Verify `<tracker>`, `<GitHub>`, `<worker harness>`,
current issue facts, existing sessions/PRs, and required capability fallbacks.

## Definitions

- `VERIFY`: `<commands and manual checks>`
- `IN_FLIGHT`: `<states consuming concurrency>`
- `REVIEW_CLEAN`: `<current-head review predicate and rerun ownership>`
- `HUMAN_GATE`: `<label/comment semantics and whether it blocks building,
  merging, or both; default merge-only unless the gated question could change
  what the gated issue itself or its dependents build>`
- `READY`: `<pre-merge facts>`
- `DONE`: `<merged, tracker, branch, and cleanup facts>`

## Issue graph

| Issue | Direct base | Dispatch gate | Collision lock | Merge authority | Completion gate |
|---|---|---|---|---|---|
| `<id>` | `<main or parent>` | `<event>` | `<none or mutex>` | `<agent or driver>` | `<facts>` |

## Worker contract

`<persistent ownership, worker playbook, base procedure, verification, PR and
tracker metadata, review handling, spend restrictions>`

## Scheduling and stack lifecycle

`<concurrency, mutexes, direct-child transitions, draft/ready rules; keep
dispatching children that can stack a PR on their direct parent's open branch
while a merge-only HUMAN_GATE or unmerged parent is pending, unless a
build-blocking HUMAN_GATE applies to that child or its base>`

## CI, review, merge, and cleanup

`<current-head evidence, rerun trigger, exact merge mechanism, cleanup>`

## Hard stops

`<conditions, affected scope, and exact escalation action>`

## Reporting and completion

| issue | status | PR | blocking on |
|---|---|---|---|

`<milestones and terminal condition>`

## Recorded project decisions

- `<decision>`
```
