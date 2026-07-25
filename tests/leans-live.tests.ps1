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
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
