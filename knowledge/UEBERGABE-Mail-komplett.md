# ÜBERGABE: Mail komplett zum Laufen bringen (Stand 28.10.2026)

Für den nächsten Chat. Erst `AGENTS.md` und `knowledge/PROTOKOLL-Zugriff.md` lesen.

## Was Semir will (Ziel, in seinen Worten zusammengefasst)

In JEDEM Chat, ohne Einstellungen, ohne Nachfragen bei Arbeitsschritten:
1. In alle drei Postfächer reinschauen: leanstechgmbh@gmail.com, info@leanstech-gmbh.de, sr@leanstech-gmbh.de
   (Posteingang UND Gesendet).
2. Mails schreiben und beantworten, wahlweise als Gmail, info@ oder sr@.
3. Anhänge setzen: PDFs, Bilder, ZIP, auch große Dateien (z. B. 13 MB) aus Drive oder vom PC.
4. Rechnungen: Rechnung als PDF, Zusatzdateien in eine ZIP (`knowledge/decisions/2026-10-27-rechnungsversand-anhaenge.md`).
5. Versand IMMER erst nach Rückfrage „Senden?“ und Semirs Ja (AGENTS.md Regel 12, unumstößlich).

## Was heute schon geht (Cloud-Session „LEANS Mail-Zentrale“)

- Gmail lesen, suchen, Entwürfe, Labels, Senden ohne Anhang: ja (Gmail-Connector).
- Drive lesen und ablegen, Board, Anfragen-Monitor 2x täglich: ja.
- info@-Mails: nur, was IONOS an Gmail weiterleitet. sr@: Weiterleitung unbewiesen.

## Was NICHT geht und warum (Cloud)

| Wunsch | Blockiert durch |
|---|---|
| Anhänge über ca. 20 KB senden | Gmail-Connector braucht Base64 durch den Chat, zu groß |
| Drive-Dateien über 10 MB laden | Grenze des Drive-Connectors |
| Als info@/sr@ senden, deren Gesendet lesen | `scripts/leans-mail.py` fertig, aber Umgebung hat keine Passwörter und kein Netz zu smtp/imap |
| Auf Semirs PC klicken | Cloud-Session hat keine Verbindung zum PC |

## Die Lösung: Arbeit am PC statt in der Cloud

Semir hat die Claude-Desktop-App unter Windows. Ein Chat dort läuft auf seinem PC, mit seinem Netz und seinen Dateien.
Dort fallen alle Cloud-Grenzen weg.

### Weg 1 (empfohlen): Claude Code lokal am PC
1. Claude-Desktop-App → Bereich „Code“ → neue Session → statt Cloud „Lokal“ wählen, Ordner:
   der lokale Klon von `leans-collaboration` (sonst einmal `git clone https://github.com/leanstechgmbh-create/leans-collaboration`).
2. Passwörter einmalig mit dem Einrichtungs-Skript setzen (PowerShell im Repo-Ordner, NICHT im Chat):
   ```powershell
   git pull
   powershell -ExecutionPolicy Bypass -File scripts\mail-einrichten.ps1
   ```
   Das Skript fragt die drei Passwörter verdeckt ab (`GMAIL_APP_PASSWORD`, `IONOS_INFO_PASSWORD`, `IONOS_SR_PASSWORD`),
   speichert sie als Windows-Benutzervariablen und testet sofort alle drei Konten (sendet nichts).
   App-Passwort: https://myaccount.google.com/apppasswords (das am 28.10. im Chat genannte ist verbrannt: löschen!).
   Fehlt Python: `winget install Python.Python.3.12`. Danach Claude-App komplett beenden und neu starten.
3. Test im lokalen Chat (ohne Versand):
   ```
   python scripts/leans-mail.py test
   python scripts/leans-mail.py lesen --konto sr --ordner Sent --tage 7
   python scripts/leans-mail.py --von gmail --an leanstechgmbh@gmail.com --betreff Test --text Test --anhang <pdf> --dry-run
   ```
   `test` prüft je Konto: Anmeldung, Posteingang, Gesendet, SMTP-Anmeldung. Ohne `--dry-run` erst nach Semirs „Ja“.
4. Große Drive-Dateien: Google Drive für Desktop ist installiert (Laufwerk G:), Dateien direkt von dort anhängen.

### Weg 2: Computer use (Claude bedient Gmail/Outlook im Browser)
Claude-Desktop-App → Einstellungen → Dieser Computer → Computer use einschalten, neuer Chat.
Claude öffnet Gmail, hängt per „Aus Drive einfügen“ an, zeigt die Mail, fragt „Senden?“.

## Offene Aufräumpunkte

- App-Passwort vom 28.10. bei Google löschen; Chat mit dem Titel aus vier Buchstabengruppen links löschen.
- Entwurf an gieseke@munio-bau.de (Unterlagen, 5 PDFs im Drive-Ordner „Versand munio – Unterlagen Patrick Gieseke“) wartet.
- Entwurf an Gabelmann/Daimler (Termin Heizregister) wartet auf „Senden?“.
- mkk-Anfrage gesendet 27.10., Antwort abwarten; Entwurf an Almira (MINEM) wartet.

## Werkzeuge im Repo

- `scripts/leans-mail.py`: senden (`--von gmail|info|sr`, `--anhang`, `--zusatz` → ZIP) und `lesen` (IMAP).
- Skills: `/senden`, `/postfach`, `/mail-entwurf`, `/anhang`, `/anfragen-board`.
