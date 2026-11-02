# LEANS Übergabeboard

Gemeinsames Board fuer die Zusammenarbeit zwischen ChatGPT/Codex und Claude.

## 📥 Für Claude (von ChatGPT)

### AN CLAUDE: OFFEN — Rauch WE 2.2.1: Klima-ZIP vervollständigen, dann beide Zahlungserinnerungen senden
- Datum/Zeit: 2026-10-20 23:30
- Von: Claude (Cloud-Chat „Angebot für Rauch“)
- Was gebaut: Beide Zahlungserinnerungen (Klima 2025-71, Sanitär 2025-106) liegen als Gmail-Entwürfe mit Rechnung als PDF und ZIP bereit, bitgenau geprüft. Sanitär ist vollständig. Bei Klima fehlen in der ZIP die Datenblätter Mitsubishi SCM100ZS-W, SRK50ZSX-WF, Resideo L5 und die Betriebszertifizierung.
- Wo liegt es: `knowledge/prompts/2026-10-21-uebergabe-rauch-klima-fertigstellen.md`; Werkzeug „LEANS Versand“ https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU
- Nächster Schritt: Übergabe lesen, fehlende Unterlagen holen, Klima-Auftrag aktualisieren, beide Entwürfe prüfen, nach Semirs „ja“ senden.
- Stand 2026-10-27:
  - Die Datenblätter passen nicht mehr in die Klima-Mail (1 MiB je Aufruf). Deshalb gibt es den neuen Entwurf `r-8334248396302948506` „Unterlagen zur Rechnung 2025-71“ und den Auftrag `2026-10-21-rauch-klima-datenblaetter`. Er ist noch `offen` und wartet auf Semirs Klick auf der Seite (Higgsfield erlauben).
  - Die Betriebszertifizierung hängt Semir in Gmail aus Drive an.
  - Semir will von info@ senden. Das geht nur in Gmail über das Von-Feld.
- Stand 2026-10-27, später:
  - Auf Semirs „Sende bitte das“ sind beide Zahlungserinnerungen von leanstechgmbh@gmail.com rausgegangen: Klima 2025-71 und Sanitär 2025-106. Die Anhänge waren vorher bitgenau geprüft.
  - Aufträge auf `gesendet`, in „00 Übersicht – CREST Investment GmbH“ eingetragen.
  - Offen ist nur noch die Mail „Unterlagen zur Rechnung 2025-71“ mit Datenblättern und Betriebszertifizierung. Sie wartet darauf, dass Semir die Seite öffnet und Higgsfield erlaubt. Ab Version 31 fragt die Seite das beim Öffnen selbst ab.
- Stand 2026-11-02:
  - Die Betriebszertifizierung (13,4 MB) ist als S/W-Scan mit 239 KB fertig, aus „Daikin Unterlagen.pdf“, S. 2–7. Sie liegt als Asset `/_blob/5814404e327d24e0c9357df308499030` auf der Seite.
  - Die Datenblätter verkleinert die Seite ab Version 32 per Ghostscript (`pdfsettings: ebook`).
  - Neuer Text im Entwurf: „Damit liegen Ihnen alle Unterlagen zu dieser Rechnung vor. Bitte überweisen Sie den offenen Betrag von 13.709,26 €.“
  - Der Entwurf hat noch keine Anhänge, weil die Seite seit dem 27.10. nicht gelaufen ist. Vor dem Versand: Anhänge prüfen und Semir „Senden?“ fragen (Regel 12).
  - Versand als info@ geht in der Cloud nicht: Die Secrets für `scripts/leans-mail.py` fehlen, und der PC-Ordner ist für Cloud-Sessions nicht freigegeben.

### AN CLAUDE: ERLEDIGT — Entwürfe in info@ anlegen (WE 2.2.1 Rauch) — ersetzt durch Gmail-Weg, siehe Eintrag darüber
- Datum/Zeit: 2026-10-20 18:45
- Von: Claude (Cloud-Chat „Angebot für Rauch“) an Claude auf Semirs PC
- Was gebaut: Zwei Mails an CREST Investment (Frau Böhnke) fertig: Klima-Rechnung 2025-71 und Sanitär-Schlussrechnung 2025-106, mit Texten und allen Anhängen. Der Cloud-Chat erreicht das IONOS-Postfach info@leanstech-gmbh.de nicht.
- Wo liegt es: `knowledge/prompts/2026-10-20-uebergabe-info-entwuerfe-rauch.md`. Dieselbe Übergabe liegt im Drive-Ordner „Versand WE 2.2.1 Rauch – CREST Investment (2026-10-20)“. PDFs auf https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU unter `versand/`.
- Nächster Schritt: Vier Entwürfe (Klima, Sanitär, Datenblätter Klima, Datenblätter Sanitär) mit allen Anhängen in info@leanstech-gmbh.de anlegen (nicht Gmail). Am schnellsten mit `scripts/info-entwuerfe/entwuerfe_anlegen.py scripts/info-entwuerfe/rauch_we221.json --dateien <Ordner mit den PDFs>`, siehe README dort. Außerdem die Rechnungen 2025-71 und 2025-106 in den Insolvenzordner bei CREST Investment GmbH kopieren, NICHT senden, Semir zeigen.


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
- Was gebaut: Offene Rechnungen an CREST Investment GmbH (23.575,11 €) und CREST Living GmbH & Co. KG (97.749,88 €) nach Regel „00 REGELN – Insolvenzordner“ je Firma abgelegt, mit Übersicht und Zahlungserinnerung. Neu erstellt: 2025-102 bis 2025-105 (Wartungen 2025) und 2025-107 (Torfstr. 17, 4.000 € brutto, an CREST Investment). Alle neuen Dokumente mit Konto Berliner Volksbank DE21 1009 0000 2911 7280 04. Erinnerung CREST Investment (15.005,11 €) am 20.10.2026 an info@crest-investment.com gemailt; CREST Living nicht versendet.
- Wo liegt es: Google Drive „Insolvenzordner – LEANS Tech GmbH“ (ID 1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm), Unterordner „CREST Investment GmbH“ und „CREST Living GmbH & Co. KG“; Details in knowledge/projects/crest-forderungen-2026-10.md
- Nächster Schritt: Nichts versenden. Ausgeschlossen auf Wunsch von Semir: 2025-71, 2025-72 (Kesting), 2025-81 (Rauch), 2024-148 (Amarjeet Singh); Tegeler See (2024-98, 2024-105) wird separat bearbeitet. Im CREST-Investment-Ordner liegen 2025-106 und 2025-71 von dritter Seite – mit Semir klären, ob sie dort bleiben.

### AN CHATGPT: OFFEN — Neuer Ablauf: Mails mit Anhängen über „LEANS Versand“
- Datum/Zeit: 2026-10-20 21:35
- Von: Claude
- Was gebaut: Werkzeug „LEANS Versand“ (https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU). Ein Chat trägt einen Auftrag ein, die Seite legt die Rechnung als PDF und den Rest als ZIP in den Gmail-Entwurf und die Rechnung in den Insolvenzordner. Am 2026-10-20 bei WE 2.2.1 Rauch getestet: Anhänge bitgenau geprüft. AGENTS.md Nr. 11 ist neu gefasst.
- Wo liegt es: `knowledge/prompts/versand-mit-anhaengen.md`, `scripts/versand/pruefe_entwurf.py`, `knowledge/decisions/2026-10-20-mails-nur-von-info.md`
- Nächster Schritt: Ablauf lesen und ab sofort für alle Mails mit Anhängen anwenden. Senden nur nach Semirs OK.

### AN CHATGPT: ERLEDIGT — Mails nur noch als Entwurf in info@ (IONOS) — ersetzt durch `scripts/leans-mail.py` und AGENTS.md Regel 12
- Datum/Zeit: 2026-10-20 19:20
- Von: Claude
- Was gebaut: Neue Regel AGENTS.md Nr. 11. Geschaeftsmails gehen nur als Entwurf in info@leanstech-gmbh.de (IONOS), nicht in Gmail, nie selbst senden. Werkzeug `scripts/info-entwuerfe/entwuerfe_anlegen.py` legt Entwuerfe mit Anhaengen per IMAP an. Der Mailaufbau ist getestet, die IONOS-Anmeldung noch nicht, weil das Passwort fehlt.
- Wo liegt es: `scripts/info-entwuerfe/`, `knowledge/decisions/2026-10-20-mails-nur-von-info.md` (Branch claude/laughing-planck-m633wv)
- Nächster Schritt: Regel lesen und ab sofort anwenden. Auf dem PC mit gesetztem `IONOS_INFO_PASSWORD` erst `--probe`, dann ohne `--probe` ausfuehren.

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

