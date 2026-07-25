$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root "scripts/install-leans-live.ps1"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-live-install-test-" + [guid]::NewGuid().ToString("N"))
$SeedPath = Join-Path $TempRoot "seed"
$RemotePath = Join-Path $TempRoot "remote.git"
$DestinationPath = Join-Path $TempRoot "LEANS-Live"

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
    New-Item -ItemType Directory -Path $SeedPath -Force | Out-Null
    Push-Location $SeedPath
    try {
        git init | Out-Null
        git config user.name "LEANS Test"
        git config user.email "leans-test@example.invalid"
        Set-Content -LiteralPath "README.md" -Value "seed" -Encoding UTF8
        git add README.md
        git commit -m "seed" | Out-Null
    }
    finally {
        Pop-Location
    }

    git clone --bare $SeedPath $RemotePath | Out-Null

    $createOutput = & $Script -RepositoryUrl $RemotePath -Destination $DestinationPath | Out-String
    Assert-Contains $createOutput "Created LEANS-Live." "installer should create a missing destination."
    if (-not (Test-Path -LiteralPath (Join-Path $DestinationPath ".git"))) {
        throw "installer should clone a Git working copy."
    }

    $updateOutput = & $Script -RepositoryUrl $RemotePath -Destination $DestinationPath | Out-String
    Assert-Contains $updateOutput "Updated LEANS-Live." "installer should update an existing working copy."

    Write-Host "PASS install-leans-live workflow"
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
