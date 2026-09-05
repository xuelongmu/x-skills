# Browser fallbacks

Use this only when the active browser connector cannot perform the task.
Follow its current discovery and recovery instructions before treating a
deferred tool or unselected browser as unavailable.

## Playwright

Reuse an installed compatible runtime, including one bundled by the host.
Otherwise choose task-local setup for one-off evidence or repository test setup
when durable coverage is requested. Explain the chosen scope and proceed within
existing authorization; ask if a necessary installation or repository dependency
change is not covered. Follow the repository package manager and test conventions.

Use accessible locators, web-first waits, and a deterministic viewport.
Capture traces or HAR only when useful, with sensitive data masked or omitted.
Use a fresh context and authorized authentication setup instead of copying a
daily browser profile. Launch headlessly on display-less hosts, or connect over
CDP to a verified existing debugging endpoint when its state must be preserved.

## Raw CDP

Use this when no suitable connector is available and Playwright is unavailable,
blocked, or declined. Explain this fallback in the result.

Bundled launchers create an isolated Chrome profile, bind an ephemeral debugging
port to loopback, verify the endpoint against that profile's `DevToolsActivePort`,
and print a connection manifest:

- Windows: [launch-chrome.ps1](../scripts/launch-chrome.ps1), with
  `-ScratchDirectory <absolute-scratch>`. It is headless unless `-Visible`
  is requested.
- macOS/Linux: [launch-chrome.sh](../scripts/launch-chrome.sh), run with
  `bash <script> <absolute-scratch>`.
  Requires Node 22+, curl, and Chrome or Chromium. Display-less Linux uses
  headless mode automatically.

Resolve script paths from the active skill directory. Both launchers leave
Chrome running so later steps can reconnect to the same tab. Read the manifest
for the endpoint, owned process ID, and profile. After the flow, stop only that
owned process and remove its profile and manifest after it exits. Verify cleanup
targets remain within the task's scratch directory.

Use the verified endpoint's target list and page WebSocket for navigation,
evaluation, and screenshots. Node 22+ supplies `WebSocket`; unref send-timeout
timers so completed helpers can exit.

Run Chromium unprivileged. The POSIX helper refuses root unless
`BROWSER_EVIDENCE_ALLOW_NO_SANDBOX=1` is explicitly set. Allow that override only
with user authorization in a trusted isolated container; never on a shared host
or for untrusted content.
