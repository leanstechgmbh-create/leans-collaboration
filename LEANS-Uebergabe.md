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

### AN CHATGPT: OFFEN — Zugriffsprotokoll und Anfragen-Automatik eingerichtet
- Datum/Zeit: 2026-10-24 12:30
- Von: Claude
- Was gebaut: Einziges Protokoll fuer Mail/Drive/Anhaenge/Berechtigungen (`knowledge/PROTOKOLL-Zugriff.md`), Freigabeliste (`docs/claude-settings.vorlage.json`), geplante Aufgabe „LEANS Klima – Anfragen“ (zweimal taeglich, Prompt in `knowledge/prompts/anfragen-triage.md`). AGENTS.md Regel 1 verweist jetzt zuerst auf das Protokoll; die PowerShell-Schritte gelten nur noch lokal.
- Wo liegt es: Branch `claude/fixealle-3-mails-von-un-ce9itw`, Dateien wie oben
- Nächster Schritt: Protokoll lesen und bei eigenen Zugriffsproblemen nur dort ergaenzen. Keine weiteren Anleitungen zu Mail oder Drive anlegen.

### AN CHATGPT: OFFEN — CREST-Forderungen im Insolvenzordner abgelegt
- Datum/Zeit: 2026-10-20 23:15
- Von: Claude
- Was gebaut: Offene Rechnungen an CREST Investment GmbH (23.575,11 €) und CREST Living GmbH & Co. KG (86.749,88 €; Erinnerung alte Rechnungen 85.313,71 €) nach Regel „00 REGELN – Insolvenzordner“ je Firma abgelegt, mit Übersicht und Zahlungserinnerung. Neu erstellt: 2025-102 bis 2025-105 (Wartungen 2025) und 2025-107 (Torfstr. 17, 4.000 € brutto, an CREST Investment). Alle neuen Dokumente mit Konto Berliner Volksbank DE21 1009 0000 2911 7280 04. Erinnerung CREST Investment (15.005,11 €) am 20.10.2026 an info@crest-investment.com gemailt; CREST Living nicht versendet.
- Wo liegt es: Google Drive „Insolvenzordner – LEANS Tech GmbH“ (ID 1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm), Unterordner „CREST Investment GmbH“ und „CREST Living GmbH & Co. KG“; Details in knowledge/projects/crest-forderungen-2026-10.md
- Nächster Schritt: Nichts versenden. Ausgeschlossen auf Wunsch von Semir: Villa (2026-44), Neubau (2026-45 inkl. 2025-98), Kesting (2025-72), Rauch (2025-71, 2025-106, 2025-81), 2024-148 (Amarjeet Singh); deren Dateien liegen im Drive-Ordner „CREST separat – Villa, Neubau, Kesting, Rauch“. Tegeler See (2024-98, 2024-105) wird separat bearbeitet.

### AN CHATGPT: ERLEDIGT — Test-Review von Claude abschliessen
- Datum/Zeit: 2026-07-25 16:37
- Von: Claude
- Was gebaut: LEANS-Live-Pruefung durchgefuehrt: status gelesen, Aktivitaet angekuendigt, offene Review 4bd1a1bd bestaetigt und abgeschlossen, alle drei Testskripte gruen. Neue Test-Review 675466f6-ab96-4c34-be07-93b0fbed8ab8 an ChatGPT gestellt.
- Wo liegt es: C:\Users\semir\Documents\LEANS-Live (.leans-live\reviews\675466f6-ab96-4c34-be07-93b0fbed8ab8.json)
- Nächster Schritt: `leans-live.ps1 status` ausfuehren, dann `acknowledge-review -Assistant chatgpt -ReviewId 675466f6-ab96-4c34-be07-93b0fbed8ab8` und `complete-review ... -Outcome "..."`.

## ✅ Erledigt / Archiv

Erledigte Eintraege koennen hierhin verschoben werden, wenn das Board zu lang wird.

