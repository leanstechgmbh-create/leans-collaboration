# LEANS Live Zusammenarbeit

## Einmalig einrichten

Erstelle den dauerhaften Arbeitsordner aus dem Repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-leans-live.ps1
```

Danach arbeiten ChatGPT/Codex und Claude immer im selben Ordner:

```text
C:\Users\semir\Documents\LEANS-Live
```

GitHub bleibt die gemeinsame Versionshistorie. Der Ordner `.leans-live\` ist nur der lokale Echtzeitstatus und wird nicht in Git gespeichert.

## Start jeder Aufgabe

1. `LEANS-Uebergabe.md` lesen.
2. Den Live-Status lesen.
3. Die eigene Arbeit und betroffene Dateien ankundigen.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 announce -Assistant chatgpt -Activity "Reviewing the workflow guide" -Paths "docs/LEANS-Live.md"
```

Fur Claude wird bei den Befehlen `-Assistant claude` verwendet.

## Gegenseitige Prufung

ChatGPT kann Claude um eine Prufung bitten:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 request-review -Assistant chatgpt -Target claude -Question "Confirm the daily workflow is clear." -Paths "docs/LEANS-Live.md"
```

Claude sieht die Anfrage mit `status`, ubernimmt sie und schliesst sie ab:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 acknowledge-review -Assistant claude -ReviewId "review-id"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 complete-review -Assistant claude -ReviewId "review-id" -Outcome "Approved"
```

Nur der adressierte Assistent darf eine Review ubernehmen oder abschliessen.

## Dateibeobachtung

Dieser Befehl beobachtet gemeinsame Dateianderungen und schreibt sie in den Live-Status. Mit `-Notify` versucht Windows zusatzlich, einen lokalen Hinweis anzuzeigen.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-live.ps1 start -Notify
```

Der Watcher endet mit `Ctrl+C`. Er ignoriert `.git`, `.leans-live` und Obsidian-Zwischendateien.

## Grenze der Automatisierung

Der Live-Status speichert Anderungen und Prufauftrage sofort. Ein geschlossener oder untatiger Chat kann dadurch nicht selbststandig antworten. Sobald ChatGPT/Codex oder Claude die nachste Aufgabe beginnt, liest der Assistent den aktuellen Status und arbeitet offene Ubergaben oder Reviews ab.
