---
name: prompt-agent-orchestrator
description: Draft or assess a project-specific Agent Orchestrator coordination prompt for multi-issue delivery, dependency scheduling, and review or merge gates.
---

# Author an AO coordination prompt

Produce an executable project contract that relies on AO's injected role for
generic coordination behavior. Authoring a prompt does not authorize changing
issues, sessions, branches, or PRs.

Ground the prompt in binding repository instructions, live issue records and
relations, and the installed AO capabilities the plan actually needs. Do not
assume support for tracker writes, arbitrary base branches, reviewer reruns, or
merge commands. State a usable fallback or a concrete blocker for a missing
capability.

## Decisions the prompt must settle

- Each issue's scope, direct base, dispatch gate, persistent worker owner, PR,
  merge authority, and completion condition.
- Concurrency and collision rules expressed in the project's own coordination
  vocabulary, with an unambiguous meaning for in-flight work.
- Verification and review evidence required for the current head, including
  who triggers a review, which findings block, and how rebuttals are handled.
- Human gates, spending limits, destructive-action boundaries, and escalation
  for waits that cannot progress autonomously.

One persistent worker and PR per issue is the default. Make multi-parent
integration or ownership exceptions explicit. Do not hide a synthetic merge or
competing writer behind an undefined scheduling rule.

A human gate blocks merging by default. Block building too when the decision
could change what the issue or its dependents should build. Continue other
safe work, including children that can stack on their direct parent's branch.

When a direct parent's head changes, resume its direct children to integrate the
new base and refresh relevant verification and current-head review evidence.
Do not retarget grandchildren solely because a grandparent changed.

## Keep the contract concise

Define repeated predicates once, such as `VERIFY`, `REVIEW_CLEAN`, and `DONE`.
Use a table for a multi-issue graph and delete unused template sections. The
[starter template](references/prompt-template.md) is optional; adapt it to the
actual project rather than adding gates to fill placeholders.

Check the resulting prompt for contradictory authorities, unsupported operations,
cycles, orphaned waits, and an ending condition that abandons runnable work.
Migrations, backfills, and shared-data ownership changes need the repository's
corresponding scope and human gates even if issue labels omitted them.

Return `GO` when the prompt is executable, or `NOT READY` with the concrete
missing decisions or capabilities. Include evidence sources and the prompt;
label an incomplete draft accordingly. Omit empty warnings and checklist receipts.
