---
name: browser-evidence
description: >-
  Drive a real browser against a running application to capture trustworthy UI
  evidence, including PR walkthrough screenshots, visual verification, and
  front-end bug reproductions. Use when asked to verify behavior in the app,
  screenshot a flow, reproduce a browser-visible defect, or attach walkthrough
  evidence to a PR. Prefer an available signed-in browser connector and use a
  clean CDP browser only when no connector can perform the task.
---

# Browser evidence

Read the target repository's instructions before opening the app. Treat its
security, privacy, spending, and destructive-action rules as authoritative.

## Define the proof

Before driving the browser:

1. Identify the behavior or claim to prove.
2. Identify the route, prerequisites, and expected visible result.
3. Decide which captures are necessary. Prefer a small sequence that proves the
   flow over a large screenshot dump.
4. Confirm where artifacts belong. Use task-local scratch space unless the user
   asks to add evidence to the repository.

## Use a browser connector first

Load and follow the browser-control skill exposed by the current Codex session
(typically `browser:control-in-app-browser`) before controlling a browser.
Prefer a connected, signed-in browser when the flow depends on existing
authentication or application state.

- If more than one browser, profile, or device is available and the choice is
  not explicit, list them and ask the user to choose. Never infer which personal
  profile to use.
- Create a dedicated tab or tab group for the task.
- Re-inspect live tab state instead of reusing tab IDs or handles from an
  earlier session.
- Use batched browser actions for predictable sequences, but pause and inspect
  after navigation, authentication, modal transitions, or asynchronous work.
- If no suitable connector is installed or connected, explain the limitation
  before using the CDP fallback.

## Drive and capture

- Start from a known route and assert `location.href` before every capture.
- Preserve in-page state. Reconnect to a live tab instead of reloading or
  navigating during a multi-step flow unless the test requires navigation.
- Select controls by stable, specific attributes or accessible names. Scope
  generic buttons such as **Send**, **Close**, or **Generate** to the relevant
  form or panel.
- For controlled React inputs, use the element prototype's native value setter
  and dispatch a bubbling `input` event when ordinary typing is unavailable.
- Wait for the relevant UI to settle. For streaming panels, poll the relevant
  text and require several unchanged samples.
- Inspect console or network failures when they bear on the claim. Treat old log
  buffer entries as unverified until they reproduce.
- Visually inspect every screenshot. Do not report an artifact as evidence if it
  shows the wrong route, stale state, an overlay, secrets, personal data, or a
  partially rendered viewport.

Never enter credentials, expose unrelated tabs, or capture private account
details. Stop before any purchase, provider render, irreversible mutation, or
other confirmation gate unless the user explicitly authorizes that action and
the repository permits it. Capturing the confirmation gate itself is valid
evidence.

## Fall back to CDP

Use CDP only when no browser connector can perform the task. State that the
fallback was necessary in the final report.

Launch Chrome as a separate process with a fresh profile. On Windows:

```powershell
$scratch = "<task-local scratch directory>"
$chromeArgs = @(
  "--remote-debugging-port=9222",
  "--user-data-dir=$scratch\chrome-profile",
  "--no-first-run",
  "--no-default-browser-check",
  "--window-size=1680,1050",
  "--force-device-scale-factor=1",
  "--disable-backgrounding-occluded-windows",
  "--disable-renderer-backgrounding",
  "--disable-background-timer-throttling",
  "--disable-features=CalculateNativeWinOcclusion"
)
Start-Process `
  -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList $chromeArgs
```

Do not name the variable `$args`; PowerShell reserves it. Keep the browser
running for the full flow and clean up the throwaway profile only after Chrome
has exited.

Node 22+ provides `WebSocket`. Fetch
`http://127.0.0.1:9222/json`, connect to the page target's
`webSocketDebuggerUrl`, and use `Page.navigate`, `Runtime.evaluate`, and
`Page.captureScreenshot`. Split a stateful flow into small scripts against the
same live tab. Unref CDP send-timeout timers so completed scripts can exit.

## Report

Report:

- what was verified and whether it passed;
- the route and meaningful actions performed;
- each screenshot or artifact path with what it proves;
- relevant console or network findings;
- any limitation, fallback, untested state, or blocked confirmation gate.

Distinguish direct visual evidence from inference. Do not claim broader coverage
than the captured flow demonstrates.
