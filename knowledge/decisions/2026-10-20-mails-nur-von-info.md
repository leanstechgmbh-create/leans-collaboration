# Entscheidung: Geschäftsmails nur von info@leanstech-gmbh.de

- Datum: 2026-10-20
- Entschieden von: Semir Redzic
- Gilt für: ChatGPT/Codex, Claude und jeden weiteren Assistenten

## Regel

- Mails an Kunden, Hausverwaltungen und Insolvenzverwalter werden als **Entwurf im IONOS-Postfach info@leanstech-gmbh.de** angelegt.
- Nicht in Gmail (leanstechgmbh@gmail.com). Ausnahme: Semir verlangt ausdrücklich Gmail-Entwürfe, wie am 2026-10-20 für WE 2.2.1 Rauch.
- **Nie selbst senden.** Semir prüft und sendet.

## Wie

- Werkzeug: `scripts/info-entwuerfe/entwuerfe_anlegen.py`. Anleitung in `scripts/info-entwuerfe/README.md`.
- Pro Versand eine JSON-Datei mit Empfängern, Betreff, Text und Anhängen. Vorlage: `rauch_we221.json`.
- Erst mit `--probe` prüfen, dann anlegen.

## Wo das läuft

- **Auf Semirs PC:** direkt, sobald `IONOS_INFO_PASSWORD` gesetzt ist.
- **In der Claude-Cloud:** nur wenn in der Umgebung `imap.ionos.de` freigegeben und `IONOS_INFO_PASSWORD` als Secret hinterlegt ist. Ohne das ist die Verbindung gesperrt. Dann die Übergabe an einen Chat auf dem PC geben (Board `LEANS-Uebergabe.md`).

## Stand 2026-10-20

- Mailaufbau getestet.
- IONOS-Anmeldung noch nicht getestet, weil Passwort und Freigabe fehlen.
