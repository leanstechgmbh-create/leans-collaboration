<#
LEANS Bildschirm-Bruecke

Legt auf Anfrage einen Screenshot in einen Google-Drive-Ordner, damit Claude
(Cloud) den Bildschirm sehen kann. Nur Lesen: das Skript klickt und tippt nie.

Ablauf:
  1. Claude legt im Drive-Ordner eine Datei "anfrage*.txt" an
     (Inhalt optional: links | rechts | haupt | alle).
  2. Google Drive synchronisiert sie auf den PC.
  3. Dieses Skript sieht die Datei, speichert "bildschirm.jpg" und
     "bildschirm-info.txt" im selben Ordner und loescht die Anfrage.
  4. Google Drive synchronisiert das Bild zurueck, Claude liest es.

Einrichten:  Bildschirm-Freigabe-starten.cmd doppelklicken (-Autostart)
Beenden:     Bildschirm-Freigabe-beenden.cmd doppelklicken (-AutostartEntfernen)
#>
param(
    [string]$Ordner,
    [ValidateSet("links", "rechts", "haupt", "alle")]
    [string]$Monitor = "links",
    [int]$IntervallSekunden = 5,
    [int]$MaxBreite = 2560,
    [int]$JpegQualitaet = 80,
    [switch]$Einmal,
    [switch]$Autostart,
    [switch]$AutostartEntfernen
)

$ErrorActionPreference = "Stop"

$OrdnerName = "Claude-Bildschirm"
$FirmenOrdnerName = "Leans Tech GmbH"
$DriveWurzelNamen = @("Meine Ablage", "My Drive")
$BildName = "bildschirm.jpg"
$InfoName = "bildschirm-info.txt"
$StatusName = "status.txt"
$AnfrageMuster = '^anfrage.*\.txt$'
$MonitorWerte = @("links", "rechts", "haupt", "alle")
$VerknuepfungName = "LEANS Bildschirm-Freigabe.lnk"
$HerzschlagMinuten = 15
$OrdnerWarteMinuten = 15

function Test-IstDriveOrdner {
    param([string]$Pfad)

    if ([string]::IsNullOrWhiteSpace($Pfad)) {
        return $false
    }

    return $Pfad -match '[\\/](Meine Ablage|My Drive)([\\/]|$)'
}

function Find-DriveOrdner {
    param([string[]]$Wurzeln)

    foreach ($wurzel in $Wurzeln) {
        foreach ($driveName in $DriveWurzelNamen) {
            $firma = Join-Path (Join-Path $wurzel $driveName) $FirmenOrdnerName
            if (Test-Path -LiteralPath $firma -PathType Container) {
                return (Join-Path $firma $OrdnerName)
            }
        }
    }

    return $null
}

function Resolve-BildschirmOrdner {
    param(
        [string]$Ordner,
        [string]$SkriptOrdner,
        [string[]]$Wurzeln
    )

    if (-not [string]::IsNullOrWhiteSpace($Ordner)) {
        return $Ordner
    }

    if (Test-IstDriveOrdner -Pfad $SkriptOrdner) {
        return $SkriptOrdner
    }

    $gefunden = Find-DriveOrdner -Wurzeln $Wurzeln
    if ($null -ne $gefunden) {
        return $gefunden
    }

    throw "Google-Drive-Ordner nicht gefunden. Ist Google Drive fuer Desktop gestartet? Alternativ mit -Ordner angeben."
}

function Get-MonitorAusAnfrage {
    param(
        [string]$Inhalt,
        [string]$Standard
    )

    if ([string]::IsNullOrWhiteSpace($Inhalt)) {
        return $Standard
    }

    $wort = ($Inhalt.Trim() -split '\s+')[0].ToLowerInvariant()
    if ($MonitorWerte -contains $wort) {
        return $wort
    }

    return $Standard
}

function Get-AnfrageDateien {
    param([string]$ZielOrdner)

    if (-not (Test-Path -LiteralPath $ZielOrdner -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $ZielOrdner -File | Where-Object { $_.Name -match $AnfrageMuster } | Sort-Object LastWriteTime)
}

function Select-Bereich {
    param(
        [object[]]$Bildschirme,
        [string]$Monitor
    )

    if ($null -eq $Bildschirme -or $Bildschirme.Count -eq 0) {
        throw "Kein Bildschirm gefunden."
    }

    switch ($Monitor) {
        "links" {
            $b = $Bildschirme | Sort-Object X, Y | Select-Object -First 1
        }
        "rechts" {
            $b = $Bildschirme | Sort-Object @{ Expression = { $_.X + $_.Width }; Descending = $true }, Y | Select-Object -First 1
        }
        "haupt" {
            $b = $Bildschirme | Where-Object { $_.Primary } | Select-Object -First 1
            if ($null -eq $b) {
                $b = $Bildschirme | Select-Object -First 1
            }
        }
        "alle" {
            $links = ($Bildschirme | ForEach-Object { $_.X } | Measure-Object -Minimum).Minimum
            $oben = ($Bildschirme | ForEach-Object { $_.Y } | Measure-Object -Minimum).Minimum
            $rechts = ($Bildschirme | ForEach-Object { $_.X + $_.Width } | Measure-Object -Maximum).Maximum
            $unten = ($Bildschirme | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum
            return @{ X = [int]$links; Y = [int]$oben; Width = [int]($rechts - $links); Height = [int]($unten - $oben) }
        }
        default {
            throw "Unbekannter Monitor: $Monitor"
        }
    }

    return @{ X = [int]$b.X; Y = [int]$b.Y; Width = [int]$b.Width; Height = [int]$b.Height }
}

function Get-Zielgroesse {
    param(
        [int]$Breite,
        [int]$Hoehe,
        [int]$MaxBreite
    )

    if ($MaxBreite -le 0 -or $Breite -le $MaxBreite) {
        return @{ Width = $Breite; Height = $Hoehe }
    }

    $faktor = $MaxBreite / [double]$Breite
    return @{ Width = $MaxBreite; Height = [int][Math]::Round($Hoehe * $faktor) }
}

function Write-TextDatei {
    param(
        [string]$Pfad,
        [string]$Text
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Pfad, $Text, $encoding)
}

function Write-Status {
    param(
        [string]$ZielOrdner,
        [string]$Text
    )

    $zeile = "{0}  {1}  (Rechner: {2})" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text, $env:COMPUTERNAME
    try {
        Write-TextDatei -Pfad (Join-Path $ZielOrdner $StatusName) -Text $zeile
    }
    catch {
        # Status ist nur Information; ein Schreibfehler darf die Bruecke nicht beenden.
    }
}

function Get-LokalerOrdner {
    return (Join-Path $env:LOCALAPPDATA "LEANS\Bildschirm")
}

function Get-PowerShellPfad {
    return (Get-Process -Id $PID).Path
}

function Initialize-Grafik {
    if (-not ("LeansDpi" -as [type])) {
        Add-Type -TypeDefinition @"
using System.Runtime.InteropServices;
public static class LeansDpi {
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();
}
"@
    }

    # Ohne DPI-Bewusstsein liefert Windows bei Skalierung >100% verkleinerte Koordinaten.
    [void][LeansDpi]::SetProcessDPIAware()
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
}

function Get-Bildschirme {
    return @([System.Windows.Forms.Screen]::AllScreens | ForEach-Object {
        [pscustomobject]@{
            X       = $_.Bounds.X
            Y       = $_.Bounds.Y
            Width   = $_.Bounds.Width
            Height  = $_.Bounds.Height
            Primary = $_.Primary
        }
    })
}

function Save-Screenshot {
    param(
        [string]$ZielOrdner,
        [string]$Monitor,
        [string]$Anlass
    )

    $bereich = Select-Bereich -Bildschirme (Get-Bildschirme) -Monitor $Monitor
    $groesse = Get-Zielgroesse -Breite $bereich.Width -Hoehe $bereich.Height -MaxBreite $MaxBreite
    $temp = Join-Path ([System.IO.Path]::GetTempPath()) ("leans-bildschirm-" + [guid]::NewGuid().ToString("N") + ".jpg")

    $bild = New-Object System.Drawing.Bitmap -ArgumentList $bereich.Width, $bereich.Height
    $ausgabe = $null
    try {
        $grafik = [System.Drawing.Graphics]::FromImage($bild)
        try {
            $grafik.CopyFromScreen($bereich.X, $bereich.Y, 0, 0, $bild.Size)
        }
        finally {
            $grafik.Dispose()
        }

        $ausgabe = $bild
        if ($groesse.Width -ne $bereich.Width) {
            $ausgabe = New-Object System.Drawing.Bitmap -ArgumentList $groesse.Width, $groesse.Height
            $grafik = [System.Drawing.Graphics]::FromImage($ausgabe)
            try {
                $grafik.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $grafik.DrawImage($bild, 0, 0, $groesse.Width, $groesse.Height)
            }
            finally {
                $grafik.Dispose()
            }
        }

        $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" } | Select-Object -First 1
        $parameter = New-Object System.Drawing.Imaging.EncoderParameters -ArgumentList 1
        $parameter.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter -ArgumentList ([System.Drawing.Imaging.Encoder]::Quality), ([long]$JpegQualitaet)
        $ausgabe.Save($temp, $codec, $parameter)
    }
    finally {
        if ($null -ne $ausgabe -and -not [object]::ReferenceEquals($ausgabe, $bild)) {
            $ausgabe.Dispose()
        }
        $bild.Dispose()
    }

    try {
        # Ueberschreiben statt neu anlegen: Drive behaelt so dieselbe Datei-ID.
        Copy-Item -LiteralPath $temp -Destination (Join-Path $ZielOrdner $BildName) -Force
    }
    finally {
        Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    }

    $info = @(
        "Aufgenommen: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "Monitor: $Monitor",
        "Bereich: $($bereich.Width)x$($bereich.Height) bei X=$($bereich.X), Y=$($bereich.Y)",
        "Gespeichert: $($groesse.Width)x$($groesse.Height)",
        "Anlass: $Anlass",
        "Rechner: $env:COMPUTERNAME"
    ) -join "`r`n"
    Write-TextDatei -Pfad (Join-Path $ZielOrdner $InfoName) -Text $info
}

function Wait-Ordner {
    param([string]$ZielOrdner)

    $bis = (Get-Date).AddMinutes($OrdnerWarteMinuten)
    while (-not (Test-Path -LiteralPath $ZielOrdner -PathType Container)) {
        # Nach dem Windows-Start ist Google Drive oft noch nicht eingebunden.
        if ((Get-Date) -gt $bis) {
            throw "Ordner nicht erreichbar: $ZielOrdner"
        }
        Start-Sleep -Seconds 10
    }
}

function Start-Bruecke {
    param([string]$ZielOrdner)

    $mutex = New-Object System.Threading.Mutex($false, "Local\LEANS-Bildschirm-Bruecke")
    try {
        $erhalten = $mutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        # Vorherige Instanz wurde hart beendet (z. B. durch -AutostartEntfernen); Mutex gehoert jetzt uns.
        $erhalten = $true
    }

    if (-not $erhalten) {
        Write-Output "Die Bildschirm-Bruecke laeuft bereits."
        return
    }

    try {
        Wait-Ordner -ZielOrdner $ZielOrdner
        Initialize-Grafik
        Write-Status -ZielOrdner $ZielOrdner -Text "Bruecke gestartet, wartet auf Anfragen."
        $letzterHerzschlag = Get-Date
        $nichtLoeschbar = @{}

        while ($true) {
            $anfragen = @(Get-AnfrageDateien -ZielOrdner $ZielOrdner | Where-Object { -not $nichtLoeschbar.ContainsKey($_.FullName) })
            if ($anfragen.Count -gt 0) {
                $inhalt = $null
                try {
                    $inhalt = Get-Content -LiteralPath $anfragen[0].FullName -Raw -ErrorAction Stop
                }
                catch {
                    # Datei wird evtl. noch synchronisiert; dann gilt der Standard-Monitor.
                }

                $gewaehlt = Get-MonitorAusAnfrage -Inhalt $inhalt -Standard $Monitor
                try {
                    Save-Screenshot -ZielOrdner $ZielOrdner -Monitor $gewaehlt -Anlass ("Anfrage " + $anfragen[0].Name)
                    Write-Status -ZielOrdner $ZielOrdner -Text "Screenshot ($gewaehlt) gespeichert."
                }
                catch {
                    Write-Status -ZielOrdner $ZielOrdner -Text ("Screenshot fehlgeschlagen (Bildschirm gesperrt?): " + $_.Exception.Message)
                }

                foreach ($anfrage in $anfragen) {
                    try {
                        Remove-Item -LiteralPath $anfrage.FullName -Force -ErrorAction Stop
                    }
                    catch {
                        # Nicht endlos neue Screenshots fuer dieselbe gesperrte Datei machen.
                        $nichtLoeschbar[$anfrage.FullName] = $true
                    }
                }
                $letzterHerzschlag = Get-Date
            }
            elseif (((Get-Date) - $letzterHerzschlag).TotalMinutes -ge $HerzschlagMinuten) {
                Write-Status -ZielOrdner $ZielOrdner -Text "Bruecke aktiv, wartet auf Anfragen."
                $letzterHerzschlag = Get-Date
            }

            Start-Sleep -Seconds $IntervallSekunden
        }
    }
    finally {
        $mutex.ReleaseMutex()
        $mutex.Dispose()
    }
}

function Stop-Bruecke {
    $prozesse = @(Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe' OR Name = 'pwsh.exe'" |
        Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'leans-bildschirm\.ps1' -and $_.CommandLine -notmatch '-Autostart' })
    foreach ($prozess in $prozesse) {
        Stop-Process -Id $prozess.ProcessId -Force -ErrorAction SilentlyContinue
    }
    return $prozesse.Count
}

function Remove-Autostart {
    param([string]$ZielOrdner)

    $verknuepfung = Join-Path ([Environment]::GetFolderPath("Startup")) $VerknuepfungName
    if (Test-Path -LiteralPath $verknuepfung) {
        Remove-Item -LiteralPath $verknuepfung -Force
    }

    $anzahl = Stop-Bruecke
    if (-not [string]::IsNullOrWhiteSpace($ZielOrdner) -and (Test-Path -LiteralPath $ZielOrdner -PathType Container)) {
        Write-Status -ZielOrdner $ZielOrdner -Text "Bruecke beendet und Autostart entfernt."
    }
    return $anzahl
}

function Install-Autostart {
    param([string]$ZielOrdner)

    if (-not (Test-Path -LiteralPath $ZielOrdner -PathType Container)) {
        New-Item -ItemType Directory -Path $ZielOrdner -Force | Out-Null
    }

    # Lokale Kopie: beim Windows-Start ist das Drive-Laufwerk evtl. noch nicht da.
    $lokal = Get-LokalerOrdner
    if (-not (Test-Path -LiteralPath $lokal -PathType Container)) {
        New-Item -ItemType Directory -Path $lokal -Force | Out-Null
    }
    $kopie = Join-Path $lokal "leans-bildschirm.ps1"
    Copy-Item -LiteralPath $PSCommandPath -Destination $kopie -Force

    [void](Remove-Autostart -ZielOrdner $null)

    $powershell = Get-PowerShellPfad
    $argumente = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -Ordner "{1}" -Monitor {2}' -f $kopie, $ZielOrdner, $Monitor
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Startup")) $VerknuepfungName))
    $lnk.TargetPath = $powershell
    $lnk.Arguments = $argumente
    $lnk.WindowStyle = 7
    $lnk.Description = "LEANS: Screenshot auf Anfrage in Google Drive (nur Lesen)"
    $lnk.Save()

    Start-Process -FilePath $powershell -ArgumentList $argumente -WindowStyle Hidden

    Initialize-Grafik
    Save-Screenshot -ZielOrdner $ZielOrdner -Monitor $Monitor -Anlass "Einrichtung (Test)"

    Write-Output "Bildschirm-Freigabe eingerichtet."
    Write-Output "Ordner:    $ZielOrdner"
    Write-Output "Autostart: bei jeder Windows-Anmeldung."
    Write-Output "Ein Test-Screenshot liegt als $BildName im Ordner."
    Write-Output "Beenden:   Bildschirm-Freigabe-beenden.cmd doppelklicken."
}

if ($MyInvocation.InvocationName -eq ".") {
    return
}

if ($AutostartEntfernen) {
    $zielFuerStatus = $null
    try {
        $zielFuerStatus = Resolve-BildschirmOrdner -Ordner $Ordner -SkriptOrdner $PSScriptRoot -Wurzeln @([System.IO.DriveInfo]::GetDrives() | Where-Object { $_.IsReady } | ForEach-Object { $_.RootDirectory.FullName })
    }
    catch {
        # Ohne Drive-Ordner trotzdem beenden.
    }
    $anzahl = Remove-Autostart -ZielOrdner $zielFuerStatus
    Write-Output "Bildschirm-Freigabe beendet ($anzahl Prozess(e) gestoppt). Autostart entfernt."
    exit 0
}

$wurzeln = @([System.IO.DriveInfo]::GetDrives() | Where-Object { $_.IsReady } | ForEach-Object { $_.RootDirectory.FullName })
$ziel = Resolve-BildschirmOrdner -Ordner $Ordner -SkriptOrdner $PSScriptRoot -Wurzeln $wurzeln

if ($Autostart) {
    Install-Autostart -ZielOrdner $ziel
    exit 0
}

if ($Einmal) {
    if (-not (Test-Path -LiteralPath $ziel -PathType Container)) {
        New-Item -ItemType Directory -Path $ziel -Force | Out-Null
    }
    Initialize-Grafik
    Save-Screenshot -ZielOrdner $ziel -Monitor $Monitor -Anlass "Einmalig"
    Write-Output "Screenshot gespeichert: $(Join-Path $ziel $BildName)"
    exit 0
}

Start-Bruecke -ZielOrdner $ziel
