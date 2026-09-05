---
name: browser-evidence
description: Verify browser-visible behavior and capture trustworthy screenshots or walkthrough evidence from a running application.
---

# Browser evidence

Prove the requested behavior in the running app. Establish the route,
prerequisites, expected visible state, and the few captures needed to demonstrate
it. Keep artifacts in task-local scratch space unless the user requests otherwise.

## Use the available browser

Follow the active host's browser-control instructions and tool schemas. Prefer a
connected signed-in browser when existing authentication or state is needed.
Respect an explicit browser or tab selection; resolve materially ambiguous
profiles through the connector's selection flow. Use a dedicated task tab when
appropriate and inspect live state rather than reusing stale handles.

If no connector can perform the task, use a compatible Playwright runtime already
available in the repository or host. For a new setup or connection problem, read
[browser fallbacks](references/browser-fallbacks.md). Raw CDP is a last resort;
its platform launchers live in `scripts/`, not in this workflow.

## Capture credible evidence

Use stable accessible locators and wait for the relevant state. Preserve the
live page through a multi-step flow; navigation or reloading must not erase the
state being tested. Confirm the route and inspect each screenshot before using
it as evidence.

Reject captures that show stale state, an obstructing overlay, incomplete render,
or sensitive details. Inspect console or network errors when they bear on the
claim, and distinguish fresh failures from old buffer entries.

Follow the task's authorization for mutations and spending. Stop at an
unapproved consequential action; its confirmation screen can itself be evidence.
Avoid credentials and unrelated private account or tab contents.

Report what passed or failed, artifact paths with what they prove, and material
limitations or relevant errors. Distinguish direct visual evidence from inference;
do not claim coverage beyond the exercised flow.
