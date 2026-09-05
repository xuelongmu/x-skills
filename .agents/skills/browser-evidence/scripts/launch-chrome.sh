#!/usr/bin/env bash
# Usage: launch-chrome.sh <task-local scratch directory>
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

scratch="${1:?Usage: launch-chrome.sh <scratch-directory>}"
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
if [ "$(uname -s)" = "Linux" ] && [ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
  set -- "$@" --headless=new
fi
chrome_log="$profile/chrome.log"
chrome_pid="$(
  CHROME_BIN="$chrome_bin" CHROME_LOG="$chrome_log" node -e '
    const fs = require("node:fs");
    const { spawn } = require("node:child_process");
    const log = fs.openSync(process.env.CHROME_LOG, "a");
    const child = spawn(process.env.CHROME_BIN, process.argv.slice(1), {
      detached: true,
      stdio: ["ignore", log, log]
    });
    fs.closeSync(log);
    child.once("error", error => {
      console.error(error.message);
      process.exitCode = 1;
    });
    child.once("spawn", () => {
      console.log(child.pid);
      child.unref();
    });
  ' -- "$@"
)" || { echo "Could not launch detached Chrome" >&2; exit 1; }
case "$chrome_pid" in
  ''|*[!0-9]*) echo "Chrome did not return a valid process ID" >&2; exit 1 ;;
esac

stop_failed_chrome() {
  kill "$chrome_pid" 2>/dev/null || true
  stop_attempt=0
  while kill -0 "$chrome_pid" 2>/dev/null && [ "$stop_attempt" -lt 50 ]; do
    stop_attempt=$((stop_attempt + 1))
    sleep 0.1
  done
  if kill -0 "$chrome_pid" 2>/dev/null; then
    kill -KILL "$chrome_pid" 2>/dev/null || true
    stop_attempt=0
    while kill -0 "$chrome_pid" 2>/dev/null && [ "$stop_attempt" -lt 50 ]; do
      stop_attempt=$((stop_attempt + 1))
      sleep 0.1
    done
  fi
  if kill -0 "$chrome_pid" 2>/dev/null; then
    echo "Chrome process $chrome_pid did not exit after SIGKILL" >&2
    return 1
  fi
}

active_port_file="$profile/DevToolsActivePort"
attempt=0
while [ "$attempt" -lt 150 ]; do
  [ -s "$active_port_file" ] && break
  if ! kill -0 "$chrome_pid" 2>/dev/null; then
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
if ! CONNECTION_FILE="$connection_file" \
  CDP_ENDPOINT="$cdp_endpoint" \
  CHROME_PID="$chrome_pid" \
  PROFILE="$profile" \
  node -e '
    const fs = require("node:fs");
    const manifest = {
      cdpEndpoint: process.env.CDP_ENDPOINT,
      chromePid: Number(process.env.CHROME_PID),
      profile: process.env.PROFILE
    };
    fs.writeFileSync(
      process.env.CONNECTION_FILE,
      `${JSON.stringify(manifest, null, 2)}\n`
    );
  '; then
  echo "Could not write the connection manifest" >&2
  rm -f "$connection_file"
  stop_failed_chrome
  exit 1
fi
printf 'Connection manifest: %s\n' "$connection_file"
cat "$connection_file"
