---
name: browser-evidence
description: >-
  Drive a real browser against a running application to capture trustworthy UI
  evidence, including PR walkthrough screenshots, visual verification, and
  front-end bug reproductions. Use when asked to verify behavior in the app,
  screenshot a flow, reproduce a browser-visible defect, or attach walkthrough
  evidence to a PR. Prefer an available signed-in browser connector; when no
  connector can perform the task, recommend installing and configuring
  Playwright before considering raw CDP.
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
  before offering the Playwright fallback.

## Offer Playwright next

When no browser connector can perform the task, recommend installing and
configuring Playwright. Explain that it provides resilient locators,
auto-waiting, screenshots, traces, and console/network inspection that raw CDP
would otherwise require implementing by hand.

Check the repository's package manager, dependencies, and test conventions
before proposing commands. Reuse an installed compatible Playwright version;
do not upgrade it solely for this task. Also reuse a Playwright runtime bundled
with an available Codex browser-control environment instead of adding a project
dependency.

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

Use hand-written CDP only after no browser connector can perform the task and
Playwright installation or execution is declined, unavailable, or blocked.
State why Playwright was not used in the final report.

Launch Chrome as a separate process with a fresh profile. On Windows:

```powershell
$scratch = "<task-local scratch directory>"
$profileName = "chrome-profile-{0}" -f [guid]::NewGuid().ToString("N")
$profile = Join-Path $scratch $profileName
$connectionFile = Join-Path $scratch "$profileName-connection.json"
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

  $connection = [ordered]@{
    cdpEndpoint = $cdpEndpoint
    chromePid = $chrome.Id
    profile = $profile
  }
  $connection | ConvertTo-Json | Set-Content -LiteralPath $connectionFile
  Write-Output "Connection manifest: $connectionFile"
  $connection | ConvertTo-Json | Write-Output
} catch {
  Remove-Item -LiteralPath $connectionFile -Force -ErrorAction SilentlyContinue
  Stop-FailedChrome
  throw
}
```

The literal quotes in `$quotedProfile` are required because `Start-Process`
joins `-ArgumentList` entries into one command line. Do not name the variable
`$args`; PowerShell reserves it. Later scripts can read the printed connection
manifest to reconnect and clean up. Keep the browser running for the full flow;
after Chrome exits, remove both the throwaway profile and the manifest.

On macOS or Linux:

```bash
command -v node >/dev/null 2>&1 || {
  echo "Node 22 or newer is required for raw CDP automation" >&2
  exit 1
}
node_major="$(node -p 'Number(process.versions.node.split(".")[0])')" || exit 1
case "$node_major" in
  ''|*[!0-9]*) echo "Could not determine the Node version" >&2; exit 1 ;;
esac
[ "$node_major" -ge 22 ] || {
  echo "Node 22 or newer is required for raw CDP automation" >&2
  exit 1
}
command -v curl >/dev/null 2>&1 || {
  echo "curl is required for raw CDP endpoint verification" >&2
  exit 1
}

chrome_extra_arg=""
if [ "$(id -u)" -eq 0 ]; then
  if [ "${BROWSER_EVIDENCE_ALLOW_NO_SANDBOX:-}" != "1" ]; then
    echo "Run Chrome as an unprivileged user, not root." >&2
    echo "For an explicitly approved trusted isolated container, set BROWSER_EVIDENCE_ALLOW_NO_SANDBOX=1." >&2
    exit 1
  fi
  chrome_extra_arg="--no-sandbox"
fi

chrome_bin=""
for candidate in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$candidate" >/dev/null 2>&1; then chrome_bin="$candidate"; break; fi
done
[ -n "$chrome_bin" ] || { echo "No Chrome or Chromium binary found" >&2; exit 1; }

scratch="<task-local scratch directory>"
umask 077
mkdir -p "$scratch" || { echo "Could not create scratch directory" >&2; exit 1; }
[ -d "$scratch" ] && [ -w "$scratch" ] || {
  echo "Scratch directory is unavailable or not writable" >&2
  exit 1
}
profile="$(mktemp -d "$scratch/chrome-profile-XXXXXXXX")" || {
  echo "Could not create the throwaway Chrome profile" >&2
  exit 1
}

set -- \
  --remote-debugging-port=0 \
  --remote-debugging-address=127.0.0.1 \
  --user-data-dir="$profile" \
  --no-first-run \
  --no-default-browser-check \
  --window-size=1680,1050 \
  --force-device-scale-factor=1
if [ -n "$chrome_extra_arg" ]; then set -- "$@" "$chrome_extra_arg"; fi
"$chrome_bin" "$@" &
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

connection_file="$(mktemp "$scratch/browser-evidence-connection-XXXXXXXX")" || {
  echo "Could not create the connection manifest" >&2
  stop_failed_chrome
  exit 1
}
if ! {
  printf 'CDP_ENDPOINT=%s\n' "$cdp_endpoint"
  printf 'CHROME_PID=%s\n' "$chrome_pid"
  printf 'PROFILE=%s\n' "$profile"
} > "$connection_file"; then
  echo "Could not write the connection manifest" >&2
  rm -f "$connection_file"
  stop_failed_chrome
  exit 1
fi
printf 'Connection manifest: %s\n' "$connection_file"
cat "$connection_file"
```

On a display-less Linux host, add `--headless=new` to the Chrome arguments;
`Page.captureScreenshot` works the same headlessly.

Run Chrome as an unprivileged user. Only in a trusted, isolated container and
after explicit user approval may you set
`BROWSER_EVIDENCE_ALLOW_NO_SANDBOX=1`; the sample then appends `--no-sandbox`.
Doing so disables a critical Chromium security boundary. Never use it on a
shared host or for untrusted content.

Later scripts can read the printed connection manifest to reconnect and clean
up. Keep Chrome running for the full flow; after it exits, remove both the
throwaway profile and the manifest.

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
