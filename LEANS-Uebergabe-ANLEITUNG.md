# LEANS Übergabeboard Anleitung

## Zweck

`LEANS-Uebergabe.md` ist die gemeinsame Schnittstelle zwischen ChatGPT/Codex und Claude. Sie enthaelt keine langen Diskussionen, sondern konkrete Arbeitsuebergaben.

## Bereiche

### `## 📥 Für Claude (von ChatGPT)`

Hier traegt ChatGPT/Codex Aufgaben ein, die Claude als Naechstes sehen soll.

### `## 📤 Für ChatGPT (von Claude)`

Hier traegt Claude Aufgaben ein, die ChatGPT/Codex als Naechstes sehen soll.

## Vorlage fuer Uebergaben

```markdown
### AN CLAUDE: OFFEN — <kurzer Titel>
- Datum/Zeit: <JJJJ-MM-TT HH:MM>
- Von: ChatGPT
- Was gebaut: <1-3 Saetze>
- Wo liegt es: <Dateipfad / Ordner / Repo / Branch>
- Nächster Schritt: <konkret>
```

```markdown
### AN CHATGPT: OFFEN — <kurzer Titel>
- Datum/Zeit: <JJJJ-MM-TT HH:MM>
- Von: Claude
- Was gebaut: <1-3 Saetze>
- Wo liegt es: <Dateipfad / Ordner / Repo / Branch>
- Nächster Schritt: <konkret>
```

## Statusregeln

- `OFFEN` bedeutet: Der andere Assistent soll handeln.
- `ERLEDIGT` bedeutet: Der adressierte Assistent hat die Aufgabe abgeschlossen.
- Nur eigene erledigte Eingangsaufgaben auf `ERLEDIGT` setzen.
- Keine fremden Eintraege auf `ERLEDIGT` setzen.
- Neue Eintraege immer ganz oben im passenden Bereich eintragen.

## Skript

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 check-chatgpt
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 add-claude -Title "Titel" -WhatBuilt "Gebaut." -Location "Pfad" -NextStep "Naechster Schritt."
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\leans-board.ps1 mark-chatgpt-done -Title "Titel"
```
