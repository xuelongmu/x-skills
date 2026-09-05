[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$ScratchDirectory,
  [switch]$Visible
)

$ErrorActionPreference = 'Stop'
$scratch = [IO.Path]::GetFullPath($ScratchDirectory)
$profileName = "chrome-profile-{0}" -f [guid]::NewGuid().ToString("N")
$profile = Join-Path $scratch $profileName
$connectionFile = Join-Path $scratch "$profileName-connection.json"
New-Item -ItemType Directory -Force -Path $scratch -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Force -Path $profile -ErrorAction Stop | Out-Null
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
if (-not $Visible) { $chromeArgs += "--headless=new" }
$chromeExe = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $chromeExe) { throw "Chrome not found in a known install location" }
$chrome = Start-Process `
  -FilePath $chromeExe `
  -ArgumentList $chromeArgs `
  -WindowStyle $(if ($Visible) { "Normal" } else { "Hidden" }) `
  -PassThru `
  -ErrorAction Stop

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
  $connection | ConvertTo-Json | Set-Content `
    -LiteralPath $connectionFile `
    -ErrorAction Stop
  Write-Output "Connection manifest: $connectionFile"
  $connection | ConvertTo-Json | Write-Output
} catch {
  Remove-Item -LiteralPath $connectionFile -Force -ErrorAction SilentlyContinue
  Stop-FailedChrome
  throw
}
