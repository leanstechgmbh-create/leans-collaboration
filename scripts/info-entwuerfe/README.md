# Entwürfe in info@leanstech-gmbh.de anlegen

`entwuerfe_anlegen.py` legt E-Mails mit allen Anhängen als **Entwurf** im IONOS-Postfach info@leanstech-gmbh.de an.
Es sendet nie. Semir prüft und sendet selbst.

## Einmal einrichten

| Wo | Was |
|---|---|
| PC (Windows) | Passwort als Umgebungsvariable setzen: `setx IONOS_INFO_PASSWORD "…"` und das Terminal neu öffnen. |
| Claude-Cloud | Umgebung bearbeiten (Menü der Cloud-Umgebung oben im Chat → Edit): unter „Allowed domains“ `imap.ionos.de` eintragen und `IONOS_INFO_PASSWORD` als Secret bzw. Umgebungsvariable hinterlegen. Danach einen neuen Chat starten. |

Das Passwort nie in den Chat schreiben und nie ins Repo legen.

## Benutzen

1. Für jeden Versand eine JSON-Datei anlegen, Vorlage: `rauch_we221.json`. Darin stehen Absender, Empfänger, Betreff, Text und die Anhänge.
2. Alle Anhänge in einen Ordner legen. Datenblätter mit `quelle` lädt das Skript selbst aus dem Internet.
3. Erst prüfen. Das schreibt `.eml`-Dateien und lädt nichts hoch:

   ```
   python entwuerfe_anlegen.py rauch_we221.json --dateien ./pdf --probe
   ```

4. Dann anlegen:

   ```
   python entwuerfe_anlegen.py rauch_we221.json --dateien ./pdf
   ```

Optionen:
- `--nur klima sanitaer` legt nur diese Mails an.
- `--ohne-fehlende` legt eine Mail auch an, wenn ein Anhang fehlt.
- Ein Entwurf mit gleichem Betreff wird nicht doppelt angelegt.

## WE 2.2.1 Rauch (Stand 2026-10-20)

Die PDFs liegen auf https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU unter `versand/`. Claude holt sie mit dem Artifact-Tool (`read`, `paths`), oder du lädst sie über „PDF öffnen“ auf der Seite herunter.

Die „Betriebszertifizierung LEANS TECH GMBH.pdf“ (13 MB) kommt aus Google Drive, ID `1QYjbexbZcxhAFHZnk0F8P3w9yW36PO5o`.

Getestet:
- Aufbau der Mails mit `--probe`: Absender, Empfänger, Text, Anhänge bitgenau.

Noch nicht getestet:
- Die Anmeldung bei IONOS. Sie braucht das Passwort und in der Cloud die Domain-Freigabe.
