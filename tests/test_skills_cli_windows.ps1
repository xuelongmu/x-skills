param(
    [Alias("Source")]
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$CliVersion = "1.5.23"
)

$ErrorActionPreference = "Stop"

if (-not $IsWindows) {
    throw "This lifecycle check is Windows-specific."
}

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    throw "npx is required."
}

$canonicalSkills = @(
    "babysit",
    "browser-evidence",
    "capture-learning",
    "design-architecture",
    "drive-agent-orchestrator",
    "google-developer-style",
    "land",
    "prompt-agent-orchestrator",
    "publish",
    "review-architecture",
    "review-change",
    "review-complexity",
    "steward-research"
)
$allSkills = @(
    "publish",
    "babysit",
    "land",
    "prompt-agent-orchestrator",
    "drive-agent-orchestrator",
    "browser-evidence",
    "review-complexity",
    "steward-research",
    "capture-learning",
    "review-change",
    "google-developer-style",
    "design-architecture",
    "review-architecture"
)
$tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$testRoot = Join-Path $tempBase ("x-skills-cli-" + [guid]::NewGuid().ToString("N"))
$projectRoot = Join-Path $testRoot "project"
$fakeProfile = Join-Path $testRoot "profile"
$previousHomeEnv = $env:HOME
$previousProfileEnv = $env:USERPROFILE
$previousCodexEnv = $env:CODEX_HOME
$previousClaudeEnv = $env:CLAUDE_CONFIG_DIR
$previousTelemetryEnv = $env:DISABLE_TELEMETRY

function Invoke-SkillsCli {
    param([string[]]$Arguments)

    & npx --yes "skills@$CliVersion" @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "skills CLI failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')"
    }
}

function Assert-PathExists {
    param([string]$LiteralPath)

    if (-not (Test-Path -LiteralPath $LiteralPath)) {
        throw "Expected path to exist: $LiteralPath"
    }
}

function Get-SkillSource {
    param([string]$Subtree)

    if (Test-Path -LiteralPath $RepositoryRoot) {
        return Join-Path $RepositoryRoot $Subtree
    }

    $normalizedSubtree = $Subtree.Replace("\", "/")
    $fragmentIndex = $RepositoryRoot.IndexOf("#")
    if ($fragmentIndex -ge 0) {
        $sourceBase = $RepositoryRoot.Substring(0, $fragmentIndex).TrimEnd("/")
        $sourceFragment = $RepositoryRoot.Substring($fragmentIndex + 1)
        return "$sourceBase/$normalizedSubtree#$sourceFragment"
    }
    return $RepositoryRoot.TrimEnd("/") + "/" + $normalizedSubtree
}

$canonicalSource = Get-SkillSource ".agents\skills"

try {
    New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fakeProfile ".codex") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fakeProfile ".claude") | Out-Null

    $env:HOME = $fakeProfile
    $env:USERPROFILE = $fakeProfile
    $env:CODEX_HOME = Join-Path $fakeProfile ".codex"
    $env:CLAUDE_CONFIG_DIR = Join-Path $fakeProfile ".claude"
    $env:DISABLE_TELEMETRY = "1"

    Push-Location $projectRoot
    try {
        Invoke-SkillsCli @("add", $canonicalSource, "--skill", "*", "--agent", "codex", "claude-code", "--yes")

        foreach ($skill in $canonicalSkills) {
            $canonical = Join-Path $projectRoot ".agents\skills\$skill"
            $claude = Join-Path $projectRoot ".claude\skills\$skill"
            Assert-PathExists $canonical
            Assert-PathExists $claude

            $canonicalItem = Get-Item -LiteralPath $canonical -Force
            $claudeItem = Get-Item -LiteralPath $claude -Force
            if ($canonicalItem.LinkType) {
                throw "Canonical install must be a real directory: $canonical"
            }
            if ($claudeItem.LinkType -ne "Junction") {
                throw "Claude install must be a Windows junction: $claude"
            }
            if (Test-Path -LiteralPath (Join-Path $projectRoot ".codex\skills\$skill")) {
                throw "Codex must discover the universal path without a host link: $skill"
            }

            $canonicalHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $canonical "SKILL.md")).Hash
            $claudeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $claude "SKILL.md")).Hash
            if ($canonicalHash -ne $claudeHash) {
                throw "Canonical and Claude contents differ: $skill"
            }
        }

        $landWatcher = Join-Path $projectRoot ".agents\skills\land\scripts\land_watch.py"
        Assert-PathExists $landWatcher
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\land\scripts\land_watch.py")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\publish\..\land\references\pr-workflow.md")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\babysit\..\land\references\watcher.md")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\browser-evidence\scripts\launch-chrome.ps1")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\browser-evidence\scripts\launch-chrome.sh")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\capture-learning\references\destination-routing.md")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\review-change\references\risk-lenses.md")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\review-complexity\references\review-archaeology.md")
        Assert-PathExists (Join-Path $projectRoot ".claude\skills\review-complexity\references\transition-semantics.md")

        if (-not (Test-Path -LiteralPath $RepositoryRoot)) {
            Invoke-SkillsCli (@("update", "--project") + $canonicalSkills + @("--yes"))
            foreach ($skill in $canonicalSkills) {
                $claudeItem = Get-Item -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill") -Force
                if ($claudeItem.LinkType -ne "Junction") {
                    throw "Update did not preserve the Claude junction: $skill"
                }
            }
            Assert-PathExists $landWatcher
        }

        Invoke-SkillsCli ($(@("remove") + $canonicalSkills + @("--agent", "claude-code", "--yes")))
        foreach ($skill in $canonicalSkills) {
            Assert-PathExists (Join-Path $projectRoot ".agents\skills\$skill")
            if (Test-Path -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill")) {
                throw "Claude junction still exists after targeted removal: $skill"
            }
        }
        Assert-PathExists $landWatcher

        Invoke-SkillsCli @("add", $canonicalSource, "--skill", "*", "--agent", "codex", "claude-code", "--yes")
        Invoke-SkillsCli ($(@("remove") + $allSkills + @("--agent", "codex", "claude-code", "--yes")))
        foreach ($skill in $allSkills) {
            if (Test-Path -LiteralPath (Join-Path $projectRoot ".agents\skills\$skill")) {
                throw "Canonical directory still exists after full removal: $skill"
            }
            if (Test-Path -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill")) {
                throw "Claude junction still exists after full removal: $skill"
            }
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:HOME = $previousHomeEnv
    $env:USERPROFILE = $previousProfileEnv
    $env:CODEX_HOME = $previousCodexEnv
    $env:CLAUDE_CONFIG_DIR = $previousClaudeEnv
    $env:DISABLE_TELEMETRY = $previousTelemetryEnv

    $resolvedTestRoot = [System.IO.Path]::GetFullPath($testRoot)
    $expectedPrefix = Join-Path $tempBase "x-skills-cli-"
    if (-not $resolvedTestRoot.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove unexpected test path: $resolvedTestRoot"
    }
    if (Test-Path -LiteralPath $resolvedTestRoot) {
        Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force
    }
}

Write-Output "Windows skills CLI lifecycle passed."
