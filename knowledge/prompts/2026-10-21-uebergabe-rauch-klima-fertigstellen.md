# Übergabe: WE 2.2.1 Rauch – Zahlungserinnerungen fertigstellen und senden

- Stand: 2026-10-20, 23:30 Uhr
- Für: neuer Claude-Chat
- Von: Cloud-Chat „Angebot für Rauch“
- Vorher lesen:
  - `AGENTS.md`, besonders Nr. 10 und 11
  - Ablauf für Mails mit Anhängen: `knowledge/prompts/versand-mit-anhaengen.md`

## Auftrag von Semir

1. **Klima-Mail fertig machen.** In die ZIP kommen zusätzlich:
   - Datenblatt Mitsubishi Heavy SCM100ZS-W
   - Datenblatt Mitsubishi Heavy SRK50ZSX-WF
   - Datenblatt Resideo L5 DN20
   - Betriebszertifizierung LEANS Tech GmbH (LAGetSi)
2. **Dann beide Mails senden**, Klima und Sanitär. Semir hat gesagt: „mach Klima fertig und dann schickst du das raus“.
   - Vorher alle Anhänge bitgenau prüfen.
   - Semir die Anhangliste zeigen und sein kurzes „ja“ abwarten.
3. Ein **Tellkamp-Datenblatt wird nicht gebraucht.**

## Was schon fertig ist

| | Stand |
|---|---|
| Gmail-Entwurf Klima | ID `r-2533723722972915561`, Betreff „Zahlungserinnerung – Rechnung 2025-71 – WE 2.2.1 (Herr Rauch) Klimatisierung“, an sb@ und info@crest-investment.com. Kurztext ohne Frist, neue Signatur. Anhänge: Rechnung 2025-71 (PDF) und ZIP mit Fachunternehmererklärung und Sachkundebescheinigung, bitgenau geprüft. |
| Gmail-Entwurf Sanitär | ID `r-248092081824836305`, Betreff „Zahlungserinnerung – Schlussrechnung 2025-106 – WE 2.2.1 (Herr Rauch) Sanitär“. Anhänge: Schlussrechnung 2025-106 (PDF) und ZIP mit Fachunternehmererklärung und Datenblatt Geberit. **Vollständig**, bitgenau geprüft. |
| Insolvenzordner | 2025-71 und 2025-106 liegen als PDF in „CREST Investment GmbH“ (Ordner-ID `1m147RAbQwJszPJ0HBgezFwWzCj-gT20i`). |
| Rechnungsnummer | 2025-106 ist die Rauch-Schlussrechnung. Die Torfstr.-17-Rechnung über 4.000 € wurde auf **2025-107** umgestellt (Drive-Dokument und „00 Übersicht“). |
| LEANS Versand | Aufträge `2026-10-20-rauch-klima` und `2026-10-20-rauch-sanitaer` in der Datenbank der Seite https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU. |
| Unterschriften | Beide Fachunternehmererklärungen sind unterschrieben und gestempelt (12.10.2025 bzw. 24.10.2025). Die Sachkundebescheinigung ist vollständig. |

## Schritte für die Klima-Mail

### A. Datenblätter holen

| Datei | Quelle | sha256 / Größe (geladen am 2026-10-20) |
|---|---|---|
| SCM100ZS-W | https://mhiae.com/units/scm100zs-w/?pdf=4283 | `8fcca554abf7a332fc2910cccaefeef366ac36a9aab5dba3f2d020dcfbf0ef95` / 247003 B |
| SRK50ZSX-WF | https://mhiae.com/units/srk50zsx-wf/?pdf=5187 | `3187136c2416595a629301c52f22c3974743123d89361dc3c7d8714bbc86a72d` / 366237 B |
| Resideo L5 DN20 | https://tbs-online.de/doc/de/en/did.146347/93_254_45--DBL-01-de.pdf | `b75611ce8a666b63e0d7c59f6d20d9b3be51fd12d085af729a1d843e1ed4e82c` / 226816 B |

- **Weg 1 (bevorzugt):** Erst `curl -sI https://mhiae.com` testen. Kommt kein 403, direkt mit `curl -L` laden. Das geht nur, wenn Semir in der Umgebung unter „Allowed domains“ `mhiae.com` und `tbs-online.de` eingetragen hat, und erst ab einem neuen Chat.
- **Weg 2:** Semir lädt die drei PDFs über die Links und legt sie in Google Drive. Der Chat holt sie mit `download_file_content`.
- **Nicht nehmen:** die Higgsfield-Sandbox. Sie hat zwar Internet und konnte die PDFs laden, aber ihre Ausgabe wird gekürzt, die Dateien kommen nicht heil zurück.
- **Prüfen:** Mit pymupdf in den PDF-Text schauen. Die Modellbezeichnung muss SCM100ZS-W, SRK50ZSX-WF bzw. L5 DN20 sein, der sha256 sollte passen.

### B. Betriebszertifizierung

Die Datei liegt in Drive als „Betriebszertifizierung LEANS TECH GMBH.pdf“, ID `1QYjbexbZcxhAFHZnk0F8P3w9yW36PO5o`, 13,4 MB. Das Drive-Tool lädt höchstens 10 MB. Semir fragen, welchen Weg er will:

- **(a) Verkleinerte Kopie:** Semir legt eine Kopie unter 10 MB ins Drive. Der Chat lädt sie und verkleinert sie mit pymupdf weiter (Bilder als JPEG mit etwa 150 dpi neu schreiben). Lesbarkeit prüfen, dann in die ZIP.
- **(b) Von Hand anhängen:** Semir hängt sie zum Schluss in Gmail selbst an. Das muss **nach** dem Lauf der Seite passieren, weil `update_draft` alle Anhänge ersetzt. Sie liegt dann als eigener Anhang neben PDF und ZIP.

### C. Hochladen und Auftrag aktualisieren

1. `Artifact action=read url=https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU`
2. `Artifact url=… asset=true file_paths=[…]` (die neuen PDFs). Ergebnis sind Adressen `/_blob/<id>`.
3. `ArtifactData get auftraege/2026-10-20-rauch-klima`, die `version` merken.
4. `ArtifactData update` mit `if_version`:
   - `zip.dateien` um die neuen Einträge ergänzen. Die bestehenden zwei behalten: `/_blob/1cc08fe5286c4a5931936a44cf9a70e0` Fachunternehmererklärung und `/_blob/133b482088362ea50f56ad315974b348` Sachkundebescheinigung.
   - `status: "offen"` setzen.

### D. Größe

Die Klima-Mail wird mit den Datenblättern etwa 1,5 MB groß. Das ist mehr als 1 MiB pro Aufruf.

- Die Seite (Version 28) schickt dann die ZIP als Datei-Argument, wenn der Viewer das kann.
- Kann er es nicht, setzt sie den Auftrag auf `fehler: zu-gross …`. Dann die Datenblatt-PDFs mit pymupdf verkleinern und den Auftrag wieder auf `offen` setzen.

### E. Seite laufen lassen

1. `Artifact action=open url=…`
2. Status mit `ArtifactData get` prüfen, Protokoll in `protokoll`.
   - Die Seite lädt nicht neu, wenn sie bei Semir schon offen ist. Dann Semir bitten, sie einmal zu schließen und neu zu öffnen.
   - Die Rechte für Gmail und Google Drive sind erteilt.

### F. Prüfen und senden

1. `Gmail get_draft messageFormat=RAW` für beide Entwürfe. Die Ausgabe landet in einer Datei.
2. `python3 -I scripts/versand/pruefe_entwurf.py <Datei> <Ordner mit allen Originalen>`. Jede Datei muss `OK` zeigen.
   - Die bisherigen Originale liegen als published files auf der Seite unter `versand/` und lassen sich mit `Artifact read paths=[…]` holen.
3. Semir die Anhangliste zeigen. Nach seinem „ja“: `Gmail send_message draftId=…` für beide Entwürfe.
4. Danach:
   - Beide Aufträge auf `status: "gesendet"` setzen.
   - In „00 Übersicht – CREST Investment GmbH“ (Drive, ID `181VibPNcD6ZwAj-4UrGvLmas-sup_LSeWtiXLk95Mac`) eintragen: Zahlungserinnerung 2025-71 und 2025-106 versendet am <Datum>.

## Fallen

- `Gmail update_draft` ohne `attachments` **entfernt alle Anhänge**. Nach jeder Textänderung muss der Auftrag wieder auf `offen` und die Seite neu laufen.
- `get_draft` zeigt Anhänge in der normalen Ansicht nicht an. Prüfen geht nur über RAW und das Skript.
- **Absender** ist leanstechgmbh@gmail.com. Die Cloud erreicht info@ (IONOS) nicht.
