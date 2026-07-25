param(
    [string]$RepositoryUrl = "https://github.com/leanstechgmbh-create/leans-collaboration.git",
    [string]$Destination = "C:\Users\semir\Documents\LEANS-Live"
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([string[]]$Arguments)

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')"
    }
}

$gitPath = Join-Path $Destination ".git"
if (Test-Path -LiteralPath $gitPath) {
    Invoke-Git -Arguments @("-C", $Destination, "pull", "--ff-only")
    Write-Output "Updated LEANS-Live."
    exit 0
}

if (Test-Path -LiteralPath $Destination) {
    throw "Destination exists but is not a Git repository: $Destination"
}

$parent = Split-Path -Parent $Destination
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

Invoke-Git -Arguments @("clone", $RepositoryUrl, $Destination)
Write-Output "Created LEANS-Live."
