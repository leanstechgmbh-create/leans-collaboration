$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root "scripts/leans-bildschirm.ps1"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-bildschirm-test-" + [guid]::NewGuid().ToString("N"))

function Assert-Equal {
    param(
        [object]$Actual,
        [object]$Expected,
        [string]$Message
    )

    if ($Actual -ne $Expected) {
        throw "$Message (erwartet: '$Expected', erhalten: '$Actual')"
    }
}

# Nur die Funktionen laden, ohne die Bruecke zu starten.
. $Script

try {
    $bildschirme = @(
        [pscustomobject]@{ X = 0; Y = 0; Width = 2560; Height = 1440; Primary = $true },
        [pscustomobject]@{ X = -1920; Y = 200; Width = 1920; Height = 1080; Primary = $false }
    )

    $links = Select-Bereich -Bildschirme $bildschirme -Monitor "links"
    Assert-Equal $links.X -1920 "links should pick the leftmost monitor."
    Assert-Equal $links.Width 1920 "links should keep the monitor width."

    $rechts = Select-Bereich -Bildschirme $bildschirme -Monitor "rechts"
    Assert-Equal $rechts.X 0 "rechts should pick the rightmost monitor."

    $haupt = Select-Bereich -Bildschirme $bildschirme -Monitor "haupt"
    Assert-Equal $haupt.Width 2560 "haupt should pick the primary monitor."

    $alle = Select-Bereich -Bildschirme $bildschirme -Monitor "alle"
    Assert-Equal $alle.X -1920 "alle should start at the leftmost edge."
    Assert-Equal $alle.Y 0 "alle should start at the top edge."
    Assert-Equal $alle.Width 4480 "alle should span all monitors horizontally."
    Assert-Equal $alle.Height 1440 "alle should span all monitors vertically."

    $einzeln = Select-Bereich -Bildschirme @([pscustomobject]@{ X = 0; Y = 0; Width = 1920; Height = 1080; Primary = $false }) -Monitor "haupt"
    Assert-Equal $einzeln.Width 1920 "haupt should fall back to the first monitor."

    Assert-Equal (Get-MonitorAusAnfrage -Inhalt "Rechts`r`n" -Standard "links") "rechts" "request content should select the monitor."
    Assert-Equal (Get-MonitorAusAnfrage -Inhalt "" -Standard "links") "links" "empty request should use the default."
    Assert-Equal (Get-MonitorAusAnfrage -Inhalt $null -Standard "links") "links" "missing request content should use the default."
    Assert-Equal (Get-MonitorAusAnfrage -Inhalt "bitte screenshot" -Standard "haupt") "haupt" "unknown words should use the default."

    $gross = Get-Zielgroesse -Breite 3840 -Hoehe 2160 -MaxBreite 2560
    Assert-Equal $gross.Width 2560 "large screenshots should be scaled to the max width."
    Assert-Equal $gross.Height 1440 "scaling should keep the aspect ratio."
    $klein = Get-Zielgroesse -Breite 1920 -Hoehe 1080 -MaxBreite 2560
    Assert-Equal $klein.Width 1920 "small screenshots should not be scaled."

    Assert-Equal (Test-IstDriveOrdner -Pfad "G:\Meine Ablage\Leans Tech GmbH\Claude-Bildschirm") $true "Meine Ablage path should count as Drive."
    Assert-Equal (Test-IstDriveOrdner -Pfad "G:\My Drive\Claude-Bildschirm") $true "My Drive path should count as Drive."
    Assert-Equal (Test-IstDriveOrdner -Pfad "C:\Users\semir\Documents\LEANS-Live\scripts") $false "repo path should not count as Drive."

    New-Item -ItemType Directory -Path $TempRoot | Out-Null
    $laufwerk = Join-Path $TempRoot "G"
    New-Item -ItemType Directory -Path (Join-Path (Join-Path $laufwerk "Meine Ablage") "Leans Tech GmbH") -Force | Out-Null

    $gefunden = Resolve-BildschirmOrdner -Ordner $null -SkriptOrdner "C:\repo\scripts" -Wurzeln @((Join-Path $TempRoot "C"), $laufwerk)
    $erwartet = Join-Path (Join-Path (Join-Path $laufwerk "Meine Ablage") "Leans Tech GmbH") "Claude-Bildschirm"
    Assert-Equal $gefunden $erwartet "the Drive folder should be found below Leans Tech GmbH."

    Assert-Equal (Resolve-BildschirmOrdner -Ordner "D:\x" -SkriptOrdner "C:\repo" -Wurzeln @()) "D:\x" "an explicit folder should win."
    Assert-Equal (Resolve-BildschirmOrdner -Ordner $null -SkriptOrdner "G:\Meine Ablage\Leans Tech GmbH\Claude-Bildschirm" -Wurzeln @()) "G:\Meine Ablage\Leans Tech GmbH\Claude-Bildschirm" "a script inside Drive should use its own folder."

    $fehler = $null
    try {
        Resolve-BildschirmOrdner -Ordner $null -SkriptOrdner "C:\repo" -Wurzeln @((Join-Path $TempRoot "leer")) | Out-Null
    }
    catch {
        $fehler = $_.Exception.Message
    }
    if ($null -eq $fehler) {
        throw "a missing Drive folder should raise an error."
    }

    $anfrageOrdner = Join-Path $TempRoot "anfragen"
    New-Item -ItemType Directory -Path $anfrageOrdner | Out-Null
    foreach ($name in @("anfrage.txt", "anfrage (1).txt", "bildschirm.jpg", "notiz.txt", "status.txt")) {
        Set-Content -LiteralPath (Join-Path $anfrageOrdner $name) -Value "x"
    }
    $anfragen = @(Get-AnfrageDateien -ZielOrdner $anfrageOrdner)
    Assert-Equal $anfragen.Count 2 "only anfrage*.txt files should count as requests."
    Assert-Equal @(Get-AnfrageDateien -ZielOrdner (Join-Path $TempRoot "fehlt")).Count 0 "a missing folder should yield no requests."

    Write-Output "leans-bildschirm tests passed."
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
