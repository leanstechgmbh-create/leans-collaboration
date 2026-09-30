# LEANS Zusammenarbeit: ChatGPT + Claude

Dieses Projekt ist die gemeinsame Arbeitsbasis fuer ChatGPT und Claude.

## Schnellstart

1. Zu Beginn jeder Aufgabe das Board `LEANS-Uebergabe.md` lesen.
2. Offene Aufgaben im eigenen Eingangsbereich zuerst bearbeiten.
3. Dateien immer am echten Projektort aendern.
4. Uebergaben ueber das Board dokumentieren.
5. Wissen, Entscheidungen und Prompts im Ordner `knowledge/` ablegen.

Falls das Repository noch nicht initialisiert ist:

```powershell
git init
git add .
git commit -m "chore: initialize leans collaboration workspace"
```

## Wichtige Dateien

- `LEANS-Uebergabe.md` - gemeinsames Uebergabeboard.
- `LEANS-Uebergabe-ANLEITUNG.md` - verbindliches Board-Format.
- `.templates/` - kopierbare Uebergabevorlagen.
- `knowledge/` - Obsidian-kompatibler Wissensordner.
- `scripts/leans-board.ps1` - kleine Automatisierung fuer Board-Aktionen.
- `tests/leans-board.tests.ps1` - prueft die wichtigsten Board-Aktionen.
- `docs/Codex-Plugin.md` - direkte Verbindung Claude -> Codex ueber das offizielle OpenAI-Plugin.

## Typischer Ablauf

ChatGPT prueft:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 check-chatgpt
```

ChatGPT uebergibt an Claude:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 add-claude -Title "Kurzer Titel" -WhatBuilt "Was wurde gebaut." -Location "Pfad/Ordner" -NextStep "Konkreter naechster Schritt."
```

ChatGPT markiert eine eigene erledigte Aufgabe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 mark-chatgpt-done -Title "Kurzer Titel"
```

## Regel

Nur eigene erledigte Eingangsaufgaben auf `ERLEDIGT` setzen. Fremde Eintraege bleiben unangetastet.

## Live Zusammenarbeit

Die Live-Koordination ergaenzt das dauerhafte Board um aktuellen Status, Review-Anfragen und Dateibeobachtung im gemeinsamen Windows-Ordner. Die vollstandige Anleitung steht in `docs/LEANS-Live.md`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-leans-live.ps1
```
