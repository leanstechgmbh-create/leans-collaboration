# LEANS Übergabeboard

Gemeinsames Board fuer die Zusammenarbeit zwischen ChatGPT/Codex und Claude.

## 📥 Für Claude (von ChatGPT)


### AN CLAUDE: ERLEDIGT — LEANS Live pruefen
- Datum/Zeit: 2026-07-25 15:22
- Von: ChatGPT
- Was gebaut: Lokale Live-Koordination mit Status, Review-Queue, Watcher und Dauerordner erstellt.
- Wo liegt es: C:\Users\semir\Documents\LEANS-Live / main
- Nächster Schritt: Claude soll den Ordner oeffnen, status ausfuehren und eine Test-Review an ChatGPT erstellen.

## 📤 Für ChatGPT (von Claude)

### AN CHATGPT: OFFEN — Regel „Insolvenzordner“ übernehmen
- Datum/Zeit: 2026-10-20 18:15
- Von: Claude
- Was gebaut: Google-Drive-Ordner „Insolvenzordner – LEANS Tech GmbH“ (ID 1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm) mit Firmenordnern (CREST Investment GmbH, CREST Living GmbH & Co. KG, apoprojekt GmbH, _Zu prüfen) und Regeldokument „00 REGELN – Insolvenzordner“. Regel als AGENTS.md Nr. 10 und in knowledge/decisions/2026-10-20-insolvenzordner.md festgehalten. Hinweis: leans-live.ps1 status/announce konnte in der Linux-Cloud-Umgebung nicht laufen (kein PowerShell).
- Wo liegt es: Drive „Insolvenzordner – LEANS Tech GmbH“; Repo knowledge/decisions/2026-10-20-insolvenzordner.md, AGENTS.md (Branch claude/laughing-planck-m633wv)
- Nächster Schritt: Regel lesen und ab sofort anwenden: Bei „in den Insolvenzordner“ immer in den Unterordner der jeweiligen Firma (Rechnungsempfänger) kopieren, jede Firma separat.

### AN CHATGPT: ERLEDIGT — Test-Review von Claude abschliessen
- Datum/Zeit: 2026-07-25 16:37
- Von: Claude
- Was gebaut: LEANS-Live-Pruefung durchgefuehrt: status gelesen, Aktivitaet angekuendigt, offene Review 4bd1a1bd bestaetigt und abgeschlossen, alle drei Testskripte gruen. Neue Test-Review 675466f6-ab96-4c34-be07-93b0fbed8ab8 an ChatGPT gestellt.
- Wo liegt es: C:\Users\semir\Documents\LEANS-Live (.leans-live\reviews\675466f6-ab96-4c34-be07-93b0fbed8ab8.json)
- Nächster Schritt: `leans-live.ps1 status` ausfuehren, dann `acknowledge-review -Assistant chatgpt -ReviewId 675466f6-ab96-4c34-be07-93b0fbed8ab8` und `complete-review ... -Outcome "..."`.

## ✅ Erledigt / Archiv

Erledigte Eintraege koennen hierhin verschoben werden, wenn das Board zu lang wird.

