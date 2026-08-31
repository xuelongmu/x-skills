---
name: capture-learning
description: Capture a verified, reusable engineering learning in the repository authority that should prevent rediscovery or recurrence. Use after solving a non-obvious problem, incident, or repeated workflow failure, or when asked to compound a learning. Do not use for unresolved hypotheses, session transcripts, or one-off facts with no durable value.
---

# Capture a Verified Learning

Turn one solved problem into the smallest durable change that will help the next
engineer act correctly. The destination is the repository authority that owns
the behavior, not a generic archive of solution notes.

## Pass the evidence gate

Capture only after the available evidence establishes all of the following:

- a causal chain from the trigger through the mechanism to the observed failure
  or constraint;
- concrete root-cause evidence, not merely the hypothesis that led to the fix;
- the resolution and why it addresses the cause;
- verification that the resolution works; and
- the known scope, including material conditions that remain unverified.

Unresolved causal chains are not durable learnings. Do not convert a plausible
theory, an unverified fix, or an incident still under investigation into a rule.
Return `Not captured` with the missing evidence instead. An unresolved product
or implementation need may be an issue candidate, but creating or updating an
external issue requires separate authorization.

## Research before writing

Read the repository instructions and inspect the evidence that owns or explains
the behavior:

1. Search the relevant implementation, callers, tests, schemas, and generated
   artifacts.
2. Search existing skills, runbooks, repository instructions, system docs,
   ADRs, contracts, and nearby documentation for the same invariant.
3. Search relevant issue and pull-request history when it is available within
   the task's authorized systems.
4. Use `git log`, `git blame`, and the introducing or corrective commits to
   recover why the behavior exists and whether guidance has already drifted.
5. Check paths, commands, names, links, and ownership statements that the
   learning would rely on. Note stale or contradictory guidance.

Do not scan unrelated workstreams or expose secrets, customer data, tenant
identifiers, credentials, or sensitive incident payloads. Redact examples while
retaining the minimum facts needed to explain the invariant.

## Decide whether it is durable

A learning qualifies when at least one of these is supported by evidence:

- the problem can plausibly recur;
- rediscovery was expensive;
- the constraint is non-obvious from code and types;
- engineers or agents are likely to repeat the same mistake;
- an executable safeguard is missing; or
- current guidance is stale, misleading, duplicated, or incomplete.

A one-off fact with cheap rediscovery or no plausible recurrence routes to
`No durable change`. Report the evidence and stop rather than manufacturing a
rule, test, document, skill, or issue.

## Route to the owning authority

After a candidate passes the evidence and durability gates, read
[references/destination-routing.md](references/destination-routing.md). Use it
to choose one primary destination and any genuinely necessary companion
safeguard. Discover the repository's actual conventions before naming a path.

Prefer updating or superseding an existing authority over creating a parallel
explanation. Architectural decisions belong in the repository's ADR process.
Unimplemented work belongs in the issue tracker. Customer-facing release notes
belong to the repository's release-note tooling. Do not create a generic
`solutions/`, `learnings/`, or similar archive unless that is already the
repository's explicit authority.

## Distill and validate

Write only the durable content future work needs:

- **invariant:** what must remain true;
- **scope:** where and under which conditions it applies;
- **safe behavior:** what to do at the relevant decision point;
- **enforcement or verification:** the test, guard, check, or observation that
  proves it; and
- **rejected alternatives:** only approaches a future engineer might plausibly
  retry, with the evidence that rejects them.

Do not preserve the session transcript, debugging chronology, false starts, or
generic advice. Keep historical detail only when it changes a future decision.

Validate the destination with the repository's relevant checks. Re-read every
edited or linked authority for stale paths, superseded rules, duplicated claims,
and contradictions. If the capture reveals broader cleanup, report it without
performing unrelated changes.

## Preserve authorization boundaries

Capturing a learning authorizes only the in-scope local knowledge or safeguard
change. It does not authorize unrelated cleanup, commits, pushes, pull requests,
issue updates, comments, release notes, or other external writes. Use the
repository's existing issue, branch, commit, PR, ADR, and release workflows
instead of replacing them.

## Return a learning receipt

Return a concise receipt even when no durable change qualifies:

```text
Learning: <invariant or "Not captured">
Evidence: <causal chain, root-cause evidence, resolution, and verification>
Destination: <owning authority or "No durable change">
Changes: <paths changed or "none">
Staleness check: <what was checked and what was updated, superseded, or still stale>
Residual uncertainty: <known limits or "none">
```
