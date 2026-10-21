# Bildschirm-Bruecke: Claude (Cloud) sieht den PC-Bildschirm

Datum: 2026-10-08
Status: aktiv

## Problem

Semir arbeitet mit Claude-Sitzungen in der Cloud. Diese koennen seinen
Bildschirm nicht sehen. "Computer use" / Remote Control muesste pro Sitzung
eingeschaltet und verbunden werden, was im Alltag zu umstaendlich ist.

## Entscheidung

Eine einfache, dauerhafte Bruecke ueber Google Drive. Google Drive fuer Desktop
ist auf dem PC ohnehin installiert und synchronisiert einen Ordner beidseitig.

Ablauf:

1. Claude legt im Drive-Ordner `Leans Tech GmbH/Claude-Bildschirm` eine
   Datei `anfrage.txt` an (Inhalt optional: `links`, `rechts`, `haupt`, `alle`).
2. Google Drive synchronisiert sie auf den PC.
3. Das Skript `scripts/leans-bildschirm.ps1` laeuft im Hintergrund, sieht die
   Anfrage, speichert `bildschirm.jpg` + `bildschirm-info.txt` im selben Ordner
   und loescht die Anfrage.
4. Google Drive synchronisiert das Bild zurueck, Claude liest es ueber den
   Google-Drive-Connector.

## Sicherheitsgrenze (wichtig)

Das Skript ist **nur lesend**: es macht ausschliesslich Screenshots. Es klickt
nicht, tippt nicht und steuert nichts. Damit ist es deutlich unkritischer als
volle Fernsteuerung. Es laeuft nur, wenn der PC an und angemeldet ist; ein
gesperrter Bildschirm kann keinen Inhalt liefern.

## Einrichtung durch Semir (einmalig)

1. LEANS-Live aktualisieren (holt die neuen Skripte):
   `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-leans-live.ps1`
2. Im Ordner `scripts` die Datei **Bildschirm-Freigabe-starten.cmd**
   doppelklicken. Sie richtet den Autostart ein, startet die Bruecke im
   Hintergrund und legt einen Test-Screenshot im Drive-Ordner ab.

Beenden: **Bildschirm-Freigabe-beenden.cmd** doppelklicken.

## Technische Punkte

- `SetProcessDPIAware`, damit bei Windows-Skalierung >100% der volle Bereich
  erfasst wird.
- Autostart ueber eine Verknuepfung im Autostart-Ordner; das Skript wird nach
  `%LOCALAPPDATA%\LEANS\Bildschirm` kopiert, da beim Login das Drive-Laufwerk
  noch nicht eingebunden sein kann.
- Nur eine Instanz gleichzeitig (benannter Mutex).
- JPEG statt PNG und Begrenzung auf `MaxBreite`, damit die Datei klein bleibt
  und schnell synchronisiert.
- Bild wird per `Copy-Item -Force` ueberschrieben, damit Drive dieselbe Datei
  behaelt.

Tests: `tests/leans-bildschirm.tests.ps1` (Monitorauswahl, Skalierung,
Ordnererkennung, Anfrage-Filter).
