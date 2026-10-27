---
name: senden
description: Mail wirklich verschicken, auf Wunsch als info@ oder sr@leanstech-gmbh.de, mit Anhängen aus Drive, Repo oder Chat-Upload. Aufrufen mit /senden, oder wenn Semir sagt „verschick es“, „sende das“, „mach die Anhänge rein und schick es“, „von info@/sr@ senden“.
---

# Mail senden

Regel 11 (`AGENTS.md`): Eine klare Anweisung von Semir wird sofort ausgeführt, ohne Rückfrage. Erst machen, dann in einem Satz melden.

Zwei Wege. Immer zuerst Weg A prüfen, dann Weg B.

## Weg A: als info@ oder sr@ (IONOS-Mailserver, Skript im Repo)

Voraussetzung, einmalig von Semir in der Cloud-Umgebung gesetzt: `smtp.ionos.de` unter Allowed domains
und die Secrets `IONOS_INFO_PASSWORD` / `IONOS_SR_PASSWORD`. Fehlt etwas, sagt das Skript genau was.

1. Mailtext in eine Datei schreiben (Arbeitsverzeichnis), ohne Signatur, die hängt das Skript an.
2. Anhänge in den Container holen: aus Drive mit `mcp__Google_Drive__download_file_content`, aus dem Repo,
   oder Upload im Chat.
   REGEL RECHNUNGEN (Semir, 27.10.2026, `knowledge/decisions/2026-10-27-rechnungsversand-anhaenge.md`):
   Rechnung als eigene PDF per `--anhang`, alle Zusatzdateien (Aufmaß, Fotos, Nachweise) per `--zusatz`,
   das Skript packt sie in EINE ZIP „Anlagen <Betreff>.zip“. Gilt auch für Angebote mit vielen Beilagen.
3. Probelauf: `python3 scripts/leans-mail.py --von info --an <kunde> --betreff "<Betreff>" --text-datei mail.txt --anhang rechnung.pdf --zusatz aufmass.pdf --zusatz foto.jpg --dry-run`
4. Wenn Semir „senden“ gesagt hat: gleicher Befehl ohne `--dry-run`. Ausgabe „GESENDET als …“ im Chat nennen.
5. Danach in Gmail den Kunden-Thread labeln (Label_19 „Klima/Anfrage offen“ bleibt, bis erledigt) und das Board
   aktualisieren (`/anfragen-board`), falls es eine Kundenanfrage ist.

Exit-Code 2 = Konfiguration fehlt, 3 = Netz gesperrt, 4 = Passwort falsch. Den Hinweis aus der Fehlermeldung
wörtlich an Semir geben, nichts umgehen.

## Weg B: als leanstechgmbh@gmail.com (Gmail-Werkzeug)

Wenn Weg A nicht geht oder Semir ausdrücklich Gmail will:
`mcp__Gmail__send_message` mit `to`, `subject`, `body`, `attachments` (base64, `filename`, `mimeType`),
oder mit `draftId`, wenn der Entwurf schon in Gmail liegt. Absender ist dann immer das Gmail-Konto.
Rechnungsregel gilt auch hier: Rechnung als PDF, Zusatzdateien vorher mit
`zip -j "Anlagen <Betreff>.zip" datei1 datei2` bündeln, beide anhängen.

## Regeln

- Ohne Anweisung bleibt es beim Entwurf oder dry-run. Sagt Semir „senden“ / „verschick es“, wird sofort gesendet:
  keine Rückfrage, kein „bist du sicher“, keine Optionen. Danach melden: an wen, Absender, Anhänge (Regel 11).
- Einzige erlaubte Frage: Empfängeradresse oder Anhang fehlt und ist nirgends zu finden. Dann genau eine Frage.
- Fehlt Secret oder Netzfreigabe: Fehlertext und Stelle nennen (Protokoll 3b), nicht fragen, ob Semir sie setzen möchte.
- Website-Formular-Mails (formsubmit) nie per Reply beantworten, sondern an die Kunden-E-Mail aus dem Text.
- Bankverbindung in Mails: LEANS Tech GmbH, Berliner Volksbank, IBAN DE21 1009 0000 2911 7280 04, BIC BEVODEBB.
