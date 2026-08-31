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

$sharedSkills = @(
    "drive-agent-orchestrator",
    "google-developer-style",
    "steward-research"
)
$codexSkills = @(
    "babysit",
    "browser-evidence",
    "land",
    "prompt-agent-orchestrator",
    "publish"
)
$claudeSkills = @(
    "babysit",
    "browser-evidence",
    "prompt-agent-orchestrator",
    "publish",
    "publish-slack"
)
$allSkills = @(
    "publish",
    "publish-slack",
    "babysit",
    "land",
    "prompt-agent-orchestrator",
    "drive-agent-orchestrator",
    "browser-evidence",
    "steward-research",
    "google-developer-style"
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
$codexSource = Get-SkillSource ".codex\skills"
$claudeSource = Get-SkillSource ".claude\skills"

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
        Invoke-SkillsCli @("add", $codexSource, "--skill", "*", "--agent", "codex", "--yes")
        Invoke-SkillsCli @("add", $claudeSource, "--skill", "*", "--agent", "claude-code", "--copy", "--yes")

        foreach ($skill in $sharedSkills) {
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

        foreach ($skill in $codexSkills) {
            $codex = Join-Path $projectRoot ".agents\skills\$skill"
            Assert-PathExists $codex
            if ((Get-Item -LiteralPath $codex -Force).LinkType) {
                throw "Codex install must be a real universal directory: $codex"
            }
        }

        foreach ($skill in $claudeSkills) {
            $claude = Join-Path $projectRoot ".claude\skills\$skill"
            Assert-PathExists $claude
            if ((Get-Item -LiteralPath $claude -Force).LinkType) {
                throw "Claude variant must be an independent CLI copy: $claude"
            }
        }

        foreach ($skill in @("babysit", "browser-evidence", "prompt-agent-orchestrator", "publish")) {
            $codexHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $projectRoot ".agents\skills\$skill\SKILL.md")).Hash
            $claudeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill\SKILL.md")).Hash
            if ($codexHash -eq $claudeHash) {
                throw "Host-specific variants collapsed to identical content: $skill"
            }
        }

        if (Test-Path -LiteralPath (Join-Path $projectRoot ".claude\skills\land")) {
            throw "Codex-only land skill was installed for Claude."
        }
        if (Test-Path -LiteralPath (Join-Path $projectRoot ".agents\skills\publish-slack")) {
            throw "Claude-only publish-slack skill was installed for Codex."
        }

        if (-not (Test-Path -LiteralPath $RepositoryRoot)) {
            Invoke-SkillsCli (@("update", "--project") + $sharedSkills + @("--yes"))
            foreach ($skill in $sharedSkills) {
                $claudeItem = Get-Item -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill") -Force
                if ($claudeItem.LinkType -ne "Junction") {
                    throw "Update did not preserve the Claude junction: $skill"
                }
            }
        }

        Invoke-SkillsCli ($(@("remove") + $sharedSkills + @("--agent", "claude-code", "--yes")))
        foreach ($skill in $sharedSkills) {
            Assert-PathExists (Join-Path $projectRoot ".agents\skills\$skill")
            if (Test-Path -LiteralPath (Join-Path $projectRoot ".claude\skills\$skill")) {
                throw "Claude junction still exists after targeted removal: $skill"
            }
        }

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
