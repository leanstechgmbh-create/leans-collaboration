$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root "scripts/leans-live.ps1"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-live-test-" + [guid]::NewGuid().ToString("N"))

function Assert-Contains {
    param(
        [string]$Haystack,
        [string]$Needle,
        [string]$Message
    )

    if (-not $Haystack.Contains($Needle)) {
        throw $Message
    }
}

try {
    New-Item -ItemType Directory -Path $TempRoot | Out-Null

    & $Script announce -WorkspacePath $TempRoot -Assistant chatgpt -Activity "Writing tests" -Paths "tests/leans-live.tests.ps1" | Out-Null

    $status = & $Script status -WorkspacePath $TempRoot | Out-String
    Assert-Contains $status "chatgpt" "status should show the announcing assistant."
    Assert-Contains $status "Writing tests" "status should show the current activity."

    $statePath = Join-Path $TempRoot ".leans-live\state.json"
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.assistants.chatgpt.paths[0] -ne "tests/leans-live.tests.ps1") {
        throw "announce should persist the affected path."
    }

    $eventsPath = Join-Path $TempRoot ".leans-live\events.jsonl"
    $events = Get-Content -LiteralPath $eventsPath -Encoding UTF8
    if ($events.Count -ne 1) {
        throw "announce should append exactly one event."
    }
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
