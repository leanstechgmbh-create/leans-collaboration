$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root "scripts/leans-board.ps1"
$Temp = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-board-test-" + [guid]::NewGuid().ToString("N") + ".md")
$InboxClaudeEmoji = [string][char]0xD83D + [char]0xDCE5
$InboxChatGptEmoji = [string][char]0xD83D + [char]0xDCE4
$InboxClaude = "## " + $InboxClaudeEmoji + " F" + [char]0x00FC + "r Claude (von ChatGPT)"
$InboxChatGpt = "## " + $InboxChatGptEmoji + " F" + [char]0x00FC + "r ChatGPT (von Claude)"
$DoneHeading = "## " + [char]0x2705 + " Erledigt / Archiv"
$Dash = [char]0x2014
$Ae = [char]0x00E4

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
    @"
# LEANS Uebergabeboard

$InboxClaude

_Keine offenen Eintraege._

$InboxChatGpt

### AN CHATGPT: OFFEN $Dash API pruefen
- Datum/Zeit: 2026-07-25 10:00
- Von: Claude
- Was gebaut: Beispiel.
- Wo liegt es: repo/backend
- N$($Ae)chster Schritt: Tests ausfuehren.

$DoneHeading

"@ | Set-Content -LiteralPath $Temp -Encoding UTF8

    $checkOutput = & $Script check-chatgpt -BoardPath $Temp | Out-String
    Assert-Contains $checkOutput "API pruefen" "check-chatgpt should list the open ChatGPT handoff."

    & $Script add-claude -BoardPath $Temp -Title "UI fertig" -WhatBuilt "Startseite angelegt." -Location "app/" -NextStep "Claude soll Layout pruefen." -DateTime "2026-07-25 11:00" | Out-Null
    $afterAdd = Get-Content -LiteralPath $Temp -Raw -Encoding UTF8
    Assert-Contains $afterAdd "### AN CLAUDE: OFFEN $Dash UI fertig" "add-claude should prepend an open Claude handoff."
    Assert-Contains $afterAdd "- N$($Ae)chster Schritt: Claude soll Layout pruefen." "add-claude should include the next step."

    & $Script mark-chatgpt-done -BoardPath $Temp -Title "API pruefen" | Out-Null
    $afterDone = Get-Content -LiteralPath $Temp -Raw -Encoding UTF8
    Assert-Contains $afterDone "### AN CHATGPT: ERLEDIGT $Dash API pruefen" "mark-chatgpt-done should mark the matching ChatGPT handoff as done."

    Write-Host "PASS leans-board workflow"
}
finally {
    if (Test-Path -LiteralPath $Temp) {
        Remove-Item -LiteralPath $Temp -Force
    }
}
