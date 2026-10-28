---
name: senden
description: Mail wirklich verschicken, auf Wunsch als info@ oder sr@leanstech-gmbh.de, mit Anhängen aus Drive, Repo oder Chat-Upload. Aufrufen mit /senden, oder wenn Semir sagt „verschick es“, „sende das“, „mach die Anhänge rein und schick es“, „von info@/sr@ senden“.
---

# Mail senden

Regel 11 (`AGENTS.md`): Arbeitsschritte (lesen, Entwurf, Labels, Drive, Board) ohne Erlaubnisfragen erledigen, danach kurz melden. Versand nur nach ausdrücklichem „senden“.

Zwei Wege. Immer zuerst Weg A prüfen, dann Weg B.

## Weg A: Skript im Repo, als info@, sr@ oder gmail (einziger Weg für echte Anhänge)

Voraussetzung, einmalig von Semir in der Cloud-Umgebung gesetzt (Umgebung → Edit):
- `--von gmail`: Allowed domain `smtp.gmail.com`, Secret `GMAIL_APP_PASSWORD` (Google-Konto → Sicherheit → App-Passwörter).
- `--von info` / `--von sr`: Allowed domain `smtp.ionos.de`, Secrets `IONOS_INFO_PASSWORD` / `IONOS_SR_PASSWORD`.
Fehlt etwas, sagt das Skript genau was (Exit 2). Anhänge über ca. 20 KB gehen NUR über diesen Weg,
das Gmail-Werkzeug (Weg B) kann sie nicht tragen (Protokoll, Bekannte Grenzen).

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

- Senden nur nach ausdrücklichem „senden“ / „verschick es“ von Semir. Vorher Entwurf oder dry-run zeigen.
  Danach melden: an wen, Absender, Anhänge.
- Einzige erlaubte Frage: Empfängeradresse oder Anhang fehlt und ist nirgends zu finden. Dann genau eine Frage.
- Fehlt Secret oder Netzfreigabe: Fehlertext und Stelle nennen (Protokoll 3b), nicht fragen, ob Semir sie setzen möchte.
- Website-Formular-Mails (formsubmit) nie per Reply beantworten, sondern an die Kunden-E-Mail aus dem Text.
- Bankverbindung in Mails: LEANS Tech GmbH, Berliner Volksbank, IBAN DE21 1009 0000 2911 7280 04, BIC BEVODEBB.
