param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("check-chatgpt", "add-claude", "mark-chatgpt-done")]
    [string]$Command,

    [string]$BoardPath = "LEANS-Uebergabe.md",
    [string]$Title,
    [string]$WhatBuilt,
    [string]$Location,
    [string]$NextStep,
    [string]$DateTime = (Get-Date -Format "yyyy-MM-dd HH:mm")
)

$ErrorActionPreference = "Stop"
$InboxClaudeEmoji = [string][char]0xD83D + [char]0xDCE5
$InboxChatGptEmoji = [string][char]0xD83D + [char]0xDCE4
$InboxClaudeHeading = "## " + $InboxClaudeEmoji + " F" + [char]0x00FC + "r Claude (von ChatGPT)"
$InboxChatGptHeading = "## " + $InboxChatGptEmoji + " F" + [char]0x00FC + "r ChatGPT (von Claude)"
$Dash = [char]0x2014
$Ae = [char]0x00E4

function Read-Board {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Board not found: $Path"
    }

    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
}

function Write-Board {
    param(
        [string]$Path,
        [string]$Content
    )

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Get-Section {
    param(
        [string]$Content,
        [string]$Heading
    )

    $escapedHeading = [regex]::Escape($Heading)
    $match = [regex]::Match($Content, "(?ms)^$escapedHeading\s*\r?\n(?<body>.*?)(?=^##\s|\z)")
    if (-not $match.Success) {
        throw "Section not found: $Heading"
    }

    return $match.Groups["body"].Value
}

function Require-Value {
    param(
        [string]$Value,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value: $Name"
    }
}

function Add-ClaudeHandoff {
    param(
        [string]$Content,
        [string]$Title,
        [string]$WhatBuilt,
        [string]$Location,
        [string]$NextStep,
        [string]$DateTime
    )

    Require-Value $Title "Title"
    Require-Value $WhatBuilt "WhatBuilt"
    Require-Value $Location "Location"
    Require-Value $NextStep "NextStep"

    $heading = $script:InboxClaudeHeading
    $entry = @(
        "### AN CLAUDE: OFFEN $script:Dash $Title"
        "- Datum/Zeit: $DateTime"
        "- Von: ChatGPT"
        "- Was gebaut: $WhatBuilt"
        "- Wo liegt es: $Location"
        "- N$($script:Ae)chster Schritt: $NextStep"
        ""
        ""
    ) -join "`r`n"

    $escapedHeading = [regex]::Escape($heading)
    $pattern = "(?ms)^($escapedHeading\s*\r?\n)(?<body>.*?)(?=^##\s|\z)"

    return [regex]::Replace($Content, $pattern, {
        param($match)
        $body = $match.Groups["body"].Value
        $body = $body -replace "(?m)^_Keine offenen Eintr.ge\._\s*", ""
        return $match.Groups[1].Value + "`r`n" + $entry + $body.TrimStart()
    }, 1)
}

function Mark-ChatGptDone {
    param(
        [string]$Content,
        [string]$Title
    )

    Require-Value $Title "Title"

    $heading = $script:InboxChatGptHeading
    $section = Get-Section -Content $Content -Heading $heading
    $escapedTitle = [regex]::Escape($Title)
    if ($section -notmatch "(?m)^### AN CHATGPT: OFFEN $script:Dash $escapedTitle\s*$") {
        throw "Open ChatGPT handoff not found: $Title"
    }

    return $Content -replace "(?m)^### AN CHATGPT: OFFEN $script:Dash $escapedTitle\s*$", "### AN CHATGPT: ERLEDIGT $script:Dash $Title"
}

$board = Read-Board -Path $BoardPath

switch ($Command) {
    "check-chatgpt" {
        $section = Get-Section -Content $board -Heading $script:InboxChatGptHeading
        $matches = [regex]::Matches($section, "(?m)^### AN CHATGPT: OFFEN $script:Dash .+$")
        if ($matches.Count -eq 0) {
            Write-Output "Keine offenen Eintraege fuer ChatGPT."
            exit 0
        }

        foreach ($match in $matches) {
            Write-Output $match.Value
        }
    }
    "add-claude" {
        $updated = Add-ClaudeHandoff -Content $board -Title $Title -WhatBuilt $WhatBuilt -Location $Location -NextStep $NextStep -DateTime $DateTime
        Write-Board -Path $BoardPath -Content $updated
        Write-Output "Uebergabe an Claude eingetragen: $Title"
    }
    "mark-chatgpt-done" {
        $updated = Mark-ChatGptDone -Content $board -Title $Title
        Write-Board -Path $BoardPath -Content $updated
        Write-Output "ChatGPT-Eintrag erledigt: $Title"
    }
}
