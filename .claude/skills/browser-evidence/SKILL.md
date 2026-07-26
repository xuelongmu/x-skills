---
name: browser-evidence
description: >-
  Drive a real browser against a running application to capture trustworthy UI
  evidence, including PR walkthrough screenshots, visual verification, and
  front-end bug reproductions. Use when asked to verify behavior in the app,
  screenshot a flow, reproduce a browser-visible defect, or attach walkthrough
  evidence to a PR. Prefer the Claude-in-Chrome extension and use a clean CDP
  browser only when the extension cannot be connected.
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

## Use Claude-in-Chrome first

Call `mcp__claude-in-chrome__list_connected_browsers`.

When one or more browsers are returned, use `AskUserQuestion` to list every
browser as a separate option. Include its display name and device ID. Add a
final option labeled exactly:

`Open a confirmation screen in every connected Chrome extension and let me select the right one there.`

Use `select_browser` with the selected device ID, or `switch_browser` for the
confirmation-screen option. Never choose a browser or profile for the user.

When no browser is returned:

1. Explain that the extension must be connected to the same Claude account as
   the current session.
2. If the session exposes `userEmail`, name that address. Otherwise, do not
   guess; ask the user to compare the account shown by the extension with the
   account used by the session.
3. Ask the user to confirm that the extension shows **Connected** for that
   account.
4. Call `switch_browser` once. A Connect prompt means the extension is
   registered; "No other browsers available to switch to" means no extension is
   registered to the current account.

Give the user a real opportunity to fix the connection before falling back to
CDP.

Once connected, call `tabs_context_mcp{createIfEmpty:true}`, then
`tabs_create_mcp` for a dedicated tab. Never reuse tab IDs from an earlier
session. Prefer `browser_batch` for predictable runs of clicks, typing, and
captures.

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

Use CDP only after the extension cannot be connected. State that the fallback
was necessary in the final report.

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
