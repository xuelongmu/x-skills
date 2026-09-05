# AO prompt starter

Use only sections needed for this project. Replace placeholders with verified
facts or explicit decisions; an unresolved execution gate means the draft is
not ready.

```markdown
Coordinate <project and issue set> through AO. Workers own implementation and
their PRs. Follow <repository instructions and worker playbook>; the live brief
is <source>.

## Delivery contract

- VERIFY: <required checks and any manual evidence>
- REVIEW_CLEAN: <blocking feedback, current-head evidence, reviewer trigger,
  completion event, and response/resolution policy>
- HUMAN_GATE: <who decides, what evidence clears it, and whether it blocks
  building, merging, or both>
- DONE: <PR, tracker, and handoff facts>

## Issue graph

| Issue | Direct base | Dispatch gate | Collision rule | Merge authority |
| --- | --- | --- | --- | --- |
| <issue> | <base or parent> | <event> | <none or lock> | <worker/AO/driver> |

Run at most <N> in-flight workers, meaning <states>. Use one persistent worker
and PR per issue unless <explicit exception>. Give each worker its scope,
direct base procedure, required evidence, and relevant project decisions.

Continue safe unblocked and stackable work while other issues await decisions.
On a direct parent head change, integrate that head into its direct children
and refresh their evidence. Merge parents before children.

## Operations and waits

Use <verified AO capabilities and necessary fallbacks> for tracker updates,
review triggers, merge, and cleanup. Check the exact current head against
<gates> immediately before merging. Preserve collaborator work and dirty
worktrees.

Escalate <conditions> to <owner> after <timeout or deadline>, using <observable
completion event> to resume. Gates block only <affected scope>. Respect
<spending, secret, and destructive-action limits>.

Report meaningful milestones and required decisions. Finish at <terminal
condition>; otherwise continue runnable work and monitor pending transitions.
```
