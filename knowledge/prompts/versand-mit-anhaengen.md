# Ablauf: Mail mit Anhängen versenden (für jeden Claude-Chat)

Gilt ab 2026-10-20 für jeden Chat, auch in der Cloud. Werkzeug: Seite **„LEANS Versand“**,
https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU.

Semir hat dort Gmail und Google Drive einmal erlaubt. Die Seite legt die Anhänge selbst in den Gmail-Entwurf, weil ein Chat große Dateien nicht direkt an Gmail geben kann.

## Form (Vorgabe von Semir)

- **Rechnung als PDF**, **alles andere als eine ZIP-Datei**: Fachunternehmererklärungen, Nachweise, Datenblätter.
- **Kurzer Text**, ohne viele Infos. Muster:

  ```text
  Hallo Frau <Name>,

  anbei erhalten Sie unsere Rechnung <Nr> für <Leistung> (<Objekt>). Die Erklärungen, Nachweise und Datenblätter finden Sie in der ZIP-Datei.

  Mit freundlichen Grüßen

  Semir Redzic

  Klima ▪ Lüftung ▪ Sanitär ▪ Heizung
  Wir verstehen unser Handwerk

  Tel: +49 152 16607036
  info@leanstech-gmbh.de
  www.leanstechgmbh-hkls.de
  leanstech-klima.de

  Firmensitz: Berlepschstr. 165, 14165 Berlin
  Geschäftsführer: Semir Redzic
  ```

- Das ist die aktuelle Signatur. In Gmail ist keine hinterlegt, deshalb gehört sie immer direkt in den Text.
- Bei Zahlungserinnerungen (Rechnung schon gestellt, nicht bezahlt): Betreff „Zahlungserinnerung – Rechnung <Nr> – …“, Rechnungsdatum und Betrag nennen, **keine Frist setzen**. Zum Beispiel: „unsere Rechnung <Nr> vom <Datum> über <Betrag> für <Leistung> ist noch nicht bezahlt. Bitte überweisen Sie den offenen Betrag.“

- Alle Unterlagen müssen dabei sein. Fehlt etwas, nicht senden, sondern Semir sagen, was fehlt.

## Schritte

1. **Unterlagen prüfen:**
   - Erklärungen unterschrieben und datiert
   - Beträge, Empfänger und Bank stimmen
   - Rechnungsnummer ist einmalig: im Drive nach der Nummer suchen
2. **Gmail-Entwurf anlegen**, ohne Anhänge: `mcp Gmail create_draft` mit `to`, `subject` und `body` (Kurztext). Die Entwurf-ID notieren.
3. **PDFs auf die Seite hochladen:**
   - Einmal `Artifact action=read url=<Seite>`.
   - Dann `Artifact url=<Seite> asset=true file_paths=[…]`.
   - Jede Datei bekommt eine Adresse `/_blob/<id>`.
4. **Auftrag eintragen:** `ArtifactData action=set`, `collection: "auftraege"`, `doc_id: "JJJJ-MM-TT-<kurz>"`, mit diesen Daten:

   ```json
   {
     "status": "offen",
     "betreff": "…",
     "an": ["…"],
     "entwurfId": "r-…",
     "rechnungen": [{"url": "/_blob/…", "name": "Rechnung 2025-71 - ….pdf"}],
     "zip": {"name": "Anlagen … .zip", "dateien": [{"url": "/_blob/…", "name": "….pdf"}]},
     "insolvenz": [{"url": "/_blob/…", "titel": "JJJJ-MM-TT Rechnung <Nr> – <Firma> – <Betrag> EUR – <Kurzinfo>.pdf", "ordnerId": "<Firmenordner>"}]
   }
   ```

   `insolvenz` folgt der Regel Insolvenzordner (AGENTS.md Nr. 10).
5. **Seite öffnen:** `Artifact action=open url=<Seite>`.
   - Sie arbeitet offene Aufträge von selbst ab und setzt den Status auf `entwurf-fertig` oder `fehler`.
   - Ist die Seite schon offen, nimmt sie neue Aufträge sofort.
   - Status prüfen mit `ArtifactData get auftraege/<id>`.
   - Jeden Schritt und jeden Fehler protokolliert die Seite in der Sammlung `protokoll`.
6. **Anhänge prüfen:**
   - `mcp Gmail get_draft messageFormat=RAW`. Die Ausgabe ist groß und wird in eine Datei gespeichert.
   - Dann `python3 -I scripts/versand/pruefe_entwurf.py <gespeicherte Datei> <Ordner mit den Originalen>` ausführen.
   - Jede Datei, auch die in der ZIP, muss `OK` zeigen.
7. **Semir die Mail zeigen:** Betreff, Empfänger, Text und Anhänge.
8. **Senden nur nach Semirs ausdrücklichem OK:**
   - `mcp Gmail send_message draftId=<id>`.
   - Danach `ArtifactData update` mit `status: "gesendet"`.

## Grenzen

- **Anhänge pro Mail:** Höchstens etwa 750 KB, wegen der Grenze von 1 MiB pro Aufruf. Datei-Argumente gibt es in Semirs Claude-App nicht (`dateiArg: false` im Protokoll). Darüber scheitert der Aufruf mit „tool input is too large“. Ab Version 30 packt die Seite die ZIP verlustfrei (deflate), das spart bei Erklärungen 20–35 %. Passt es trotzdem nicht: zweite Mail „Unterlagen zur Rechnung …“ mit eigener ZIP.
- **Datenblätter aus dem Internet:** In `zip.dateien` statt `url` den Eintrag `higgsfield: {datei, quelle, sha256, groesse}` setzen. Die Seite lädt die Datei in der Higgsfield-Sandbox, holt sie in Stücken, prüft den sha256 und speichert sie als Asset (danach steht `url` im Auftrag). Beim ersten Mal muss Semir „Offene Aufträge ausführen“ drücken und Higgsfield erlauben.
- **Absender info@:** Geht aus der Cloud nicht. IONOS-IMAP/SMTP ist gesperrt, und das Gmail-Werkzeug hat kein Von-Feld. Semir stellt im Gmail-Entwurf oben „Von“ auf info@ um und sendet selbst. Das geht nur, wenn info@ in Gmail unter „Konten → Senden als“ eingerichtet ist. Stand 2026-10-27 gibt es keine gesendete Mail von info@ aus Gmail.
- **Google Drive:** Herunterladen nur bis 10 MB. Größere Dateien, etwa die Betriebszertifizierung mit 13 MB, muss Semir in Gmail selbst anhängen oder verkleinert ins Drive legen.
- **Herstellerseiten** für Datenblätter sind in der Cloud gesperrt, bis sie unter „Allowed domains“ der Umgebung freigegeben sind.
- **Fehler:** Steht im Auftrag `status: "fehler"`, steht der Grund in `fehler`. Zum Wiederholen `status` auf `"offen"` setzen.
- **Absender:** leanstechgmbh@gmail.com. Mails von info@ (IONOS) gehen nur von Semirs PC, siehe `scripts/info-entwuerfe/`.
