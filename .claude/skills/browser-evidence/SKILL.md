---
name: browser-evidence
description: >-
  Drive a real browser against a running application to capture trustworthy UI
  evidence, including PR walkthrough screenshots, visual verification, and
  front-end bug reproductions. Use when asked to verify behavior in the app,
  screenshot a flow, reproduce a browser-visible defect, or attach walkthrough
  evidence to a PR. Prefer the Claude-in-Chrome extension; when it cannot be
  connected, recommend installing and configuring Playwright before considering
  raw CDP.
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

Call `mcp__claude-in-chrome__list_connected_browsers`. In sessions where the
`claude-in-chrome` tools are deferred, load their schemas first with a single
`ToolSearch` call naming every tool the task needs; calling a deferred tool
directly fails.

When one to three browsers are returned, use `AskUserQuestion` to list every
browser as a separate option. Include its display name and device ID. Add a
final option labeled exactly:

`Open a confirmation screen in every connected Chrome extension and let me select the right one there.`

Use `select_browser` with the selected device ID, or `switch_browser` for the
confirmation-screen option. Never choose a browser or profile for the user.

When four or more browsers are returned, do not exceed `AskUserQuestion`'s
four-option limit. Explain that the list is too long for one question, call
`switch_browser`, and let the user select from the confirmation screens opened
in the connected extensions.

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

Give the user a real opportunity to fix the connection before offering the
Playwright fallback.

Once connected, call `tabs_context_mcp{createIfEmpty:true}`, then
`tabs_create_mcp` for a dedicated tab. Never reuse tab IDs from an earlier
session. Prefer `browser_batch` for predictable runs of clicks, typing, and
captures.

## Offer Playwright next

When Claude-in-Chrome cannot be connected, recommend installing and configuring
Playwright. Explain that it provides resilient locators, auto-waiting,
screenshots, traces, and console/network inspection that raw CDP would otherwise
require implementing by hand.

Check the repository's package manager, dependencies, and test conventions
before proposing commands. Reuse an installed compatible Playwright version;
do not upgrade it solely for this task.

When Playwright is absent, offer the user these choices:

- **Task-local automation** for one-off evidence: create a package in task-local
  scratch space, install the `playwright` library there, and install Chromium.
  With npm:

  ```powershell
  New-Item -ItemType Directory -Force -Path "<scratch>\browser-evidence"
  Set-Location "<scratch>\browser-evidence"
  npm init -y
  npm install --save-dev playwright
  npx playwright install chromium
  ```

  On macOS or Linux:

  ```bash
  scratch_dir="<scratch>/browser-evidence"
  mkdir -p "$scratch_dir"
  cd "$scratch_dir"
  npm init -y
  npm install --save-dev playwright
  npx playwright install chromium
  ```

- **Repository test setup** when the flow should become durable regression
  coverage: use the repository's package manager and the official Playwright
  initializer (with npm, `npm init playwright@latest`), then align the generated
  configuration and test location with repository conventions. Configure the
  existing dev-server command and `baseURL`, start with a Chromium project, set
  a deterministic viewport, and keep trace, screenshot, and output paths out of
  source control unless the repository intentionally tracks them.

Installing packages or browser binaries changes disk state and may use
significant bandwidth. Explain the chosen scope and obtain approval before
installation. Do not add dependencies, lockfile changes, configuration, example
tests, or generated evidence to the repository unless the user wants them
committed.

For evidence runs:

- use Chromium and a deterministic viewport such as `1680x1050`;
- use accessible Playwright locators and web-first waits instead of sleeps;
- enable tracing or HAR capture only when it helps the requested evidence;
- mask or omit secrets and personal data from screenshots and traces;
- use a fresh context by default, and use approved authentication setup rather
  than copying a daily browser profile;
- launch a clean browser with `chromium.launch()`: pass `{ headless: false }`
  only when a display is available and watching the run helps; stay headless
  (the default) in CI containers, SSH sessions, and other display-less
  environments, where a headed launch fails and headless capture works the
  same; or attach with
  `chromium.connectOverCDP("http://127.0.0.1:<verified-port>")` when an
  existing remote-debugging Chromium instance must remain stateful.

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

## Use raw CDP only as a last resort

Use hand-written CDP only after the extension cannot be connected and
Playwright installation or execution is declined, unavailable, or blocked.
State why Playwright was not used in the final report.

Launch Chrome as a separate process with a fresh profile. On Windows:

```powershell
$scratch = "<task-local scratch directory>"
$profileName = "chrome-profile-{0}" -f [guid]::NewGuid().ToString("N")
$profile = Join-Path $scratch $profileName
New-Item -ItemType Directory -Force -Path $profile | Out-Null
$quotedProfile = '"' + $profile + '"'
$chromeArgs = @(
  "--remote-debugging-port=0",
  "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=$quotedProfile",
  "--no-first-run",
  "--no-default-browser-check",
  "--window-size=1680,1050",
  "--force-device-scale-factor=1",
  "--disable-backgrounding-occluded-windows",
  "--disable-renderer-backgrounding",
  "--disable-background-timer-throttling",
  "--disable-features=CalculateNativeWinOcclusion"
)
$chromeExe = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $chromeExe) { throw "Chrome not found in a known install location" }
$chrome = Start-Process `
  -FilePath $chromeExe `
  -ArgumentList $chromeArgs `
  -WindowStyle Normal `
  -PassThru

function Stop-FailedChrome {
  if (-not $chrome.HasExited) {
    Stop-Process -Id $chrome.Id -Force -ErrorAction SilentlyContinue
  }
  [void]$chrome.WaitForExit(5000)
}

try {
  $activePortFile = Join-Path $profile "DevToolsActivePort"
  $deadline = (Get-Date).AddSeconds(15)
  while (-not (Test-Path -LiteralPath $activePortFile)) {
    if ($chrome.HasExited) { throw "Chrome exited before CDP became ready" }
    if ((Get-Date) -gt $deadline) { throw "Timed out waiting for Chrome CDP" }
    Start-Sleep -Milliseconds 100
  }

  $activePort = @(Get-Content -LiteralPath $activePortFile)
  if ($activePort.Count -lt 2) { throw "Invalid DevToolsActivePort file" }
  $cdpPort = [int]$activePort[0]
  $browserPath = $activePort[1].Trim()
  $cdpEndpoint = "http://127.0.0.1:$cdpPort"
  $version = Invoke-RestMethod "$cdpEndpoint/json/version"
  $browserSocket = [Uri]$version.webSocketDebuggerUrl
  if ($browserSocket.Port -ne $cdpPort -or
      $browserSocket.AbsolutePath -ne $browserPath) {
    throw "CDP endpoint does not belong to the launched Chrome profile"
  }
} catch {
  Stop-FailedChrome
  throw
}
```

The literal quotes in `$quotedProfile` are required because `Start-Process`
joins `-ArgumentList` entries into one command line. Do not name the variable
`$args`; PowerShell reserves it. Keep the browser running for the full flow and
clean up the throwaway profile only after Chrome has exited.

On macOS or Linux:

```bash
if [ "$(id -u)" -eq 0 ]; then
  echo "Run Chrome as an unprivileged user, not root." >&2
  echo "In a trusted isolated container only, --no-sandbox requires explicit approval and disables Chromium's sandbox." >&2
  exit 1
fi

scratch="<task-local scratch directory>"
profile="$(mktemp -d "$scratch/chrome-profile-XXXXXXXX")"
chrome_bin=""
for candidate in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$candidate" >/dev/null 2>&1; then chrome_bin="$candidate"; break; fi
done
[ -n "$chrome_bin" ] || { echo "No Chrome or Chromium binary found" >&2; exit 1; }

"$chrome_bin" \
  --remote-debugging-port=0 \
  --remote-debugging-address=127.0.0.1 \
  --user-data-dir="$profile" \
  --no-first-run \
  --no-default-browser-check \
  --window-size=1680,1050 \
  --force-device-scale-factor=1 &
chrome_pid=$!

stop_failed_chrome() {
  kill "$chrome_pid" 2>/dev/null || true
  wait "$chrome_pid" 2>/dev/null || true
}

active_port_file="$profile/DevToolsActivePort"
attempt=0
while [ "$attempt" -lt 150 ]; do
  [ -s "$active_port_file" ] && break
  if ! kill -0 "$chrome_pid" 2>/dev/null; then
    wait "$chrome_pid" 2>/dev/null || true
    echo "Chrome exited before CDP became ready" >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 0.1
done
if [ ! -s "$active_port_file" ]; then
  echo "Timed out waiting for Chrome CDP" >&2
  stop_failed_chrome
  exit 1
fi

cdp_port="$(sed -n 1p "$active_port_file")"
browser_path="$(sed -n 2p "$active_port_file")"
cdp_endpoint="http://127.0.0.1:$cdp_port"
ws_url="$(curl -fsS "$cdp_endpoint/json/version" | node -e '
  let d = "";
  process.stdin.on("data", c => d += c);
  process.stdin.on("end", () => console.log(JSON.parse(d).webSocketDebuggerUrl));
')"
case "$ws_url" in
  "ws://127.0.0.1:$cdp_port$browser_path") ;;
  *) echo "CDP endpoint does not belong to the launched Chrome profile" >&2
     stop_failed_chrome
     exit 1 ;;
esac
```

On a display-less Linux host, add `--headless=new` to the Chrome arguments;
`Page.captureScreenshot` works the same headlessly.

Run Chrome as an unprivileged user. Only in a trusted, isolated container and
after explicit user approval may you append `--no-sandbox`; doing so disables a
critical Chromium security boundary. Never use it on a shared host or for
untrusted content.

Node 22+ provides `WebSocket`. Use the verified CDP endpoint, fetch its
`/json` target list, connect to the page target's
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
