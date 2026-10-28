<#
.SYNOPSIS
  Einmalige Einrichtung der drei LEANS-Postfaecher fuer Claude Code lokal am PC (Weg 1).

.DESCRIPTION
  Fragt die drei Passwoerter verdeckt ab (Eingabe erscheint nicht am Bildschirm, nichts landet im Chat),
  speichert sie als Windows-Benutzervariablen und testet danach alle drei Konten mit
  `leans-mail.py test`: Anmeldung, Posteingang, Gesendet, SMTP-Anmeldung. Es wird KEINE Mail gesendet.

  GMAIL_APP_PASSWORD   App-Passwort von leanstechgmbh@gmail.com (https://myaccount.google.com/apppasswords)
  IONOS_INFO_PASSWORD  Passwort von info@leanstech-gmbh.de
  IONOS_SR_PASSWORD    Passwort von sr@leanstech-gmbh.de

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\mail-einrichten.ps1
  powershell -ExecutionPolicy Bypass -File scripts\mail-einrichten.ps1 -NurTest
#>
param(
    [switch]$NurTest
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$skript = Join-Path $PSScriptRoot 'leans-mail.py'

function Finde-Python {
    foreach ($kandidat in @('py', 'python', 'python3')) {
        $befehl = Get-Command $kandidat -ErrorAction SilentlyContinue
        if (-not $befehl) { continue }
        # Der Microsoft-Store-Platzhalter "python" ist vorhanden, startet aber kein Python.
        try {
            $version = & $kandidat --version 2>&1
            if ($LASTEXITCODE -eq 0 -and "$version" -match 'Python 3') { return $kandidat }
        } catch {
            continue
        }
    }
    return $null
}

function Setze-Passwort([string]$Name, [string]$Beschreibung) {
    $vorhanden = [Environment]::GetEnvironmentVariable($Name, 'User')
    if ($vorhanden) {
        $antwort = Read-Host "$Name ist schon gesetzt. Neu eingeben? (j/N)"
        if ($antwort -notmatch '^[jJyY]') {
            [Environment]::SetEnvironmentVariable($Name, $vorhanden, 'Process')
            return
        }
    }
    Write-Host ""
    Write-Host $Beschreibung -ForegroundColor Cyan
    $geheim = Read-Host "$Name eingeben (Eingabe bleibt unsichtbar, leer = ueberspringen)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($geheim)
    try {
        $klar = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ([string]::IsNullOrEmpty($klar)) {
        Write-Host "  uebersprungen" -ForegroundColor Yellow
        return
    }
    [Environment]::SetEnvironmentVariable($Name, $klar, 'User')
    [Environment]::SetEnvironmentVariable($Name, $klar, 'Process')
    $klar = $null
    Write-Host "  gespeichert" -ForegroundColor Green
}

$python = Finde-Python
if (-not $python) {
    Write-Host "Python 3 fehlt. Installieren mit:  winget install Python.Python.3.12" -ForegroundColor Red
    Write-Host "Danach PowerShell neu oeffnen und dieses Skript erneut starten."
    exit 2
}

if (-not $NurTest) {
    Write-Host "LEANS Mail-Einrichtung: drei Passwoerter, jeweils verdeckt. Nie in den Chat schreiben." -ForegroundColor White
    Setze-Passwort 'GMAIL_APP_PASSWORD' 'Gmail: App-Passwort (16 Zeichen) von https://myaccount.google.com/apppasswords. Leerzeichen sind egal.'
    Setze-Passwort 'IONOS_INFO_PASSWORD' 'IONOS: Passwort des Postfachs info@leanstech-gmbh.de'
    Setze-Passwort 'IONOS_SR_PASSWORD' 'IONOS: Passwort des Postfachs sr@leanstech-gmbh.de'
}

Write-Host ""
Write-Host "Test aller drei Konten (es wird keine Mail gesendet) ..." -ForegroundColor White
Push-Location $repo
try {
    & $python $skript test
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Host ""
if ($code -eq 0) {
    Write-Host "Fertig. Jetzt die Claude-App komplett beenden (auch im Infobereich) und neu starten," -ForegroundColor Green
    Write-Host "damit lokale Claude-Code-Sessions die Passwoerter sehen."
} else {
    Write-Host "Nicht alles bereit. Die FEHLER-Zeilen oben nennen Konto und Grund." -ForegroundColor Yellow
    Write-Host "Falsches Passwort: Skript erneut starten und nur dieses Konto mit 'j' neu eingeben."
    Write-Host "Nur testen ohne Eingabe:  powershell -ExecutionPolicy Bypass -File scripts\mail-einrichten.ps1 -NurTest"
}
exit $code
