param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("start", "status", "announce", "request-review", "acknowledge-review", "complete-review")]
    [string]$Command,

    [string]$WorkspacePath = ".",
    [ValidateSet("chatgpt", "claude")]
    [string]$Assistant,
    [ValidateSet("chatgpt", "claude")]
    [string]$Target,
    [string]$Activity,
    [string[]]$Paths = @(),
    [string]$Question,
    [string]$ReviewId,
    [string]$Outcome,
    [int]$DurationSeconds = 0,
    [switch]$Notify
)

$ErrorActionPreference = "Stop"
$ResolvedWorkspacePath = (Resolve-Path -LiteralPath $WorkspacePath).Path
$RuntimePath = Join-Path $ResolvedWorkspacePath ".leans-live"
$StatePath = Join-Path $RuntimePath "state.json"
$EventsPath = Join-Path $RuntimePath "events.jsonl"
$ReviewsPath = Join-Path $RuntimePath "reviews"
$WatcherLockPath = Join-Path $RuntimePath "watcher.lock"

function Require-Value {
    param(
        [string]$Value,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value: $Name"
    }
}

function Ensure-Runtime {
    foreach ($path in @($RuntimePath, $ReviewsPath)) {
        if (-not (Test-Path -LiteralPath $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
}

function Write-JsonAtomically {
    param(
        [string]$Path,
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 8
    $tempPath = "$Path.$([guid]::NewGuid().ToString('N')).tmp"
    $encoding = New-Object System.Text.UTF8Encoding($false)

    try {
        [System.IO.File]::WriteAllText($tempPath, $json, $encoding)
        Move-Item -LiteralPath $tempPath -Destination $Path -Force
    }
    finally {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force
        }
    }
}

function Read-State {
    if (-not (Test-Path -LiteralPath $StatePath)) {
        return $null
    }

    return Get-Content -LiteralPath $StatePath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-State {
    param([object]$State)

    Write-JsonAtomically -Path $StatePath -Value $State
}

function Add-Event {
    param(
        [string]$Type,
        [string]$From,
        [string]$To,
        [string]$Message,
        [string[]]$EventPaths = @(),
        [string]$EventReviewId
    )

    $event = [ordered]@{
        id = [guid]::NewGuid().ToString()
        timestamp = (Get-Date).ToString("o")
        type = $Type
        from = $From
        to = $To
        message = $Message
        paths = @($EventPaths)
        reviewId = $EventReviewId
    }

    $line = $event | ConvertTo-Json -Compress
    Add-Content -LiteralPath $EventsPath -Value $line -Encoding UTF8
}

function Add-Announcement {
    Require-Value -Value $Assistant -Name "Assistant"
    Require-Value -Value $Activity -Name "Activity"

    Ensure-Runtime
    $state = Read-State
    if ($null -eq $state) {
        $state = [pscustomobject]@{
            version = 1
            updatedAt = $null
            assistants = [pscustomobject]@{}
        }
    }

    $timestamp = (Get-Date).ToString("o")
    $entry = [pscustomobject]@{
        activity = $Activity
        paths = @($Paths)
        updatedAt = $timestamp
    }

    $state.assistants | Add-Member -MemberType NoteProperty -Name $Assistant -Value $entry -Force
    $state.updatedAt = $timestamp
    Write-State -State $state
    Add-Event -Type "announce" -From $Assistant -To $null -Message $Activity -EventPaths $Paths -EventReviewId $null

    Write-Output "Live activity recorded for $Assistant."
}

function Get-ReviewPath {
    param([string]$Id)

    Require-Value -Value $Id -Name "ReviewId"
    return Join-Path $ReviewsPath ("$Id.json")
}

function Read-Review {
    param([string]$Id)

    $reviewPath = Get-ReviewPath -Id $Id
    if (-not (Test-Path -LiteralPath $reviewPath)) {
        throw "Review not found: $Id"
    }

    return Get-Content -LiteralPath $reviewPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-Review {
    param(
        [string]$Id,
        [object]$Review
    )

    Write-JsonAtomically -Path (Get-ReviewPath -Id $Id) -Value $Review
}

function Require-ReviewOwner {
    param(
        [object]$Review,
        [string]$Owner
    )

    Require-Value -Value $Owner -Name "Assistant"
    if ($Review.to -ne $Owner) {
        throw "Only the addressed assistant can update this review."
    }
}

function Request-Review {
    Require-Value -Value $Assistant -Name "Assistant"
    Require-Value -Value $Target -Name "Target"
    Require-Value -Value $Question -Name "Question"
    if (@($Paths).Count -eq 0) {
        throw "Missing required value: Paths"
    }
    if ($Assistant -eq $Target) {
        throw "A review must target the other assistant."
    }

    Ensure-Runtime
    $timestamp = (Get-Date).ToString("o")
    $id = [guid]::NewGuid().ToString()
    $review = [ordered]@{
        id = $id
        from = $Assistant
        to = $Target
        status = "open"
        question = $Question
        paths = @($Paths)
        createdAt = $timestamp
        updatedAt = $timestamp
    }

    Write-Review -Id $id -Review $review
    Add-Event -Type "review-request" -From $Assistant -To $Target -Message $Question -EventPaths $Paths -EventReviewId $id
    Write-Output "Review requested: $id"
}

function Acknowledge-Review {
    Require-Value -Value $Assistant -Name "Assistant"
    $review = Read-Review -Id $ReviewId
    Require-ReviewOwner -Review $review -Owner $Assistant
    if ($review.status -eq "completed") {
        throw "Completed reviews cannot be acknowledged."
    }

    $review.status = "acknowledged"
    $review.updatedAt = (Get-Date).ToString("o")
    Write-Review -Id $review.id -Review $review
    Add-Event -Type "review-acknowledged" -From $Assistant -To $review.from -Message $review.question -EventPaths $review.paths -EventReviewId $review.id
    Write-Output "Review acknowledged: $($review.id)"
}

function Complete-Review {
    Require-Value -Value $Assistant -Name "Assistant"
    Require-Value -Value $Outcome -Name "Outcome"
    $review = Read-Review -Id $ReviewId
    Require-ReviewOwner -Review $review -Owner $Assistant
    if ($review.status -eq "completed") {
        throw "Review is already completed: $($review.id)"
    }

    $review.status = "completed"
    $review | Add-Member -MemberType NoteProperty -Name "outcome" -Value $Outcome -Force
    $review.updatedAt = (Get-Date).ToString("o")
    Write-Review -Id $review.id -Review $review
    Add-Event -Type "review-completed" -From $Assistant -To $review.from -Message $Outcome -EventPaths $review.paths -EventReviewId $review.id
    Write-Output "Review completed: $($review.id)"
}

function Show-Status {
    Write-Output "Current activity"
    $state = Read-State
    if ($null -eq $state -or $state.assistants.PSObject.Properties.Count -eq 0) {
        Write-Output "No current activity."
    }
    else {
        foreach ($property in $state.assistants.PSObject.Properties) {
            $pathsText = @($property.Value.paths) -join ", "
            Write-Output ("{0}: {1} [{2}]" -f $property.Name, $property.Value.activity, $pathsText)
        }
    }

    Write-Output ""
    Write-Output "Open reviews"
    if (-not (Test-Path -LiteralPath $ReviewsPath)) {
        Write-Output "No open reviews."
    }
    else {
        $openReviews = Get-ChildItem -LiteralPath $ReviewsPath -Filter "*.json" -File |
            ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } |
            Where-Object { $_.status -ne "completed" }

        if (@($openReviews).Count -eq 0) {
            Write-Output "No open reviews."
        }
        else {
            foreach ($review in $openReviews) {
                Write-Output ("{0}: {1} -> {2} ({3})" -f $review.id, $review.from, $review.to, $review.status)
            }
        }
    }

    Write-Output ""
    Write-Output "Recent events"
    if (-not (Test-Path -LiteralPath $EventsPath)) {
        Write-Output "No events."
    }
    else {
        $lines = Get-Content -LiteralPath $EventsPath -Encoding UTF8 | Select-Object -Last 10
        if (@($lines).Count -eq 0) {
            Write-Output "No events."
        }
        else {
            foreach ($line in $lines) {
                $event = $line | ConvertFrom-Json
                Write-Output ("{0}: {1} from {2} - {3}" -f $event.timestamp, $event.type, $event.from, $event.message)
            }
        }
    }
}

switch ($Command) {
    "announce" { Add-Announcement }
    "status" { Show-Status }
    "request-review" { Request-Review }
    "acknowledge-review" { Acknowledge-Review }
    "complete-review" { Complete-Review }
    default { throw "Command not implemented yet: $Command" }
}
