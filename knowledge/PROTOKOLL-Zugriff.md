# PROTOKOLL: Zugriff auf Mail, Drive, Kalender und Berechtigungen

Gilt fuer jeden Chat und jeden Assistenten (Claude, ChatGPT/Codex), der in diesem Projekt
fuer die LEANS Tech GmbH arbeitet. Stand: 2026-10-24. Inhaber: Semir Redzic.

Dieses Dokument ist die einzige Anleitung fuer den Zugriff. Aeltere Hinweise dazu gibt es
nicht mehr. Wenn etwas hier nicht steht, wird es hier ergaenzt, nicht an anderer Stelle.

## 1. Was funktioniert, was nicht

| Aufgabe | Funktioniert | Wie |
|---|---|---|
| Mails lesen (Inbox, Gesendet, Threads) | Ja | Werkzeuge `Gmail` (search_threads, get_thread, get_message) |
| Entwuerfe lesen und aendern | Ja | `Gmail` list_drafts, get_draft, update_draft |
| Mails schreiben, antworten, weiterleiten | Ja | `Gmail` create_draft, reply, send_message, forward |
| Anhang-Namen und -Typen sehen | Ja | get_message mit `PLAIN_TEXT` liefert `attachments` |
| Anhang-INHALT direkt aus Gmail lesen | Nein | Gmail-Werkzeug bietet keinen Download. Umweg ueber Drive, siehe Abschnitt 3 |
| Dateien in Google Drive lesen (PDF, Docs, Sheets, Bilder) | Ja | `Google_Drive` search_files, read_file_content |
| Dateien in Drive anlegen, kopieren, ablegen | Ja | `Google_Drive` create_file, copy_file |
| Kalender lesen und Termine anlegen | Ja | `Google_Calendar` |
| Sprach-Ein- und -Ausgabe | Nicht vom Chat aus | Gehoert zur Claude-App auf dem Geraet, siehe Abschnitt 6 |

## 2. Mails: Reihenfolge, die immer klappt

1. Suchen mit `search_threads`, Gmail-Syntax (`from:`, `to:`, `subject:`, `newer_than:7d`, `in:sent`, `in:draft`).
2. Thread komplett lesen mit `get_thread` und `messageFormat: PLAIN_TEXT`. Nie nur die Vorschau nutzen,
   sie zeigt nur die 5 aeltesten Nachrichten.
3. Antwort als Entwurf anlegen mit `create_draft` und `replyToMessageId`, damit die Antwort im Thread bleibt.
4. Senden nur, wenn Semir es ausdruecklich sagt. Standard ist Entwurf.

Es gibt zwei Gmail-Anbindungen. Immer die Werkzeuge mit Praefix `mcp__Gmail__` nehmen.
Die Variante `mcp__plugin_small-business_gmail__` kann nicht senden und nicht antworten.

Grosse Ergebnisse (z. B. 20 Entwuerfe im Volltext) werden in eine Datei ausgelagert.
Dann mit `jq` nur Betreff, Empfaenger und ID herausziehen statt alles zu lesen.

## 3. Anhaenge: der einzige Weg, der geht

Das Gmail-Werkzeug liefert nur Dateiname, Typ und Anhang-ID, nicht den Inhalt. Darum:

1. Semir oeffnet die Mail in Gmail und klickt am Anhang auf „In Drive speichern“.
   Zielordner: der passende Firmen- oder Projektordner, oder `_Zu pruefen (Firma unklar)`.
2. Der Chat sucht die Datei mit `search_files` (`title contains '...'` oder `parentId = '<Ordner-ID>'`).
3. Der Chat liest sie mit `read_file_content`. Das geht fuer PDF, Word, Excel, Google Docs/Sheets, PNG, JPEG.

Alternativ kann Semir die Datei direkt in den Chat hochladen. Dann liegt sie im Arbeitsverzeichnis
und wird mit den normalen Datei-Werkzeugen gelesen.

Anhaenge VERSENDEN geht: `create_draft` nimmt `attachments` mit base64-Inhalt. Dateien ueber 25 MB
in Drive ablegen und den Link in die Mail setzen.

## 4. Drive: feste Orte

| Zweck | Ordner | ID |
|---|---|---|
| Insolvenzordner – LEANS Tech GmbH | Rechnungen, Mahnungen, Insolvenzunterlagen je Firma | `1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm` |
| Regeln dazu | Dokument „00 REGELN – Insolvenzordner“ im selben Ordner | `1CbwLNGmNMnEFJieCwZkLzOa8hglFy8zwlu4e58tGfYY` |

Die Regeln aus „00 REGELN – Insolvenzordner“ gelten weiter (Kopie statt Original, Dateinamen-Schema,
ein Ordner je juristische Person). Bankverbindung in allen Dokumenten und Mails:
LEANS Tech GmbH, Berliner Volksbank, IBAN DE21 1009 0000 2911 7280 04, BIC BEVODEBB. Kein Adyen.

## 5. Berechtigungen: einmal setzen, nie wieder fragen

Die Datei `docs/claude-settings.vorlage.json` enthaelt die fertige Freigabeliste fuer Gmail, Drive,
Kalender, Docs, GitHub, Git und die ueblichen Lese-Befehle. Ein Chat darf diese Datei nicht selbst
nach `.claude/settings.json` schreiben (Selbstaenderung ist gesperrt). Darum einmalig von Hand:

```powershell
# im Projektordner, einmalig
New-Item -ItemType Directory -Force .claude | Out-Null
Copy-Item docs\claude-settings.vorlage.json .claude\settings.json
```

```bash
# Linux/Mac
mkdir -p .claude && cp docs/claude-settings.vorlage.json .claude/settings.json
```

Danach einchecken (`git add .claude/settings.json`), dann gilt es fuer jeden Chat in diesem Repo.

Fuer Cloud-Sessions (claude.ai/code) zusaetzlich: beim Start der Session den Berechtigungsmodus auf
„Auto“ oder „Alle Bearbeitungen akzeptieren“ stellen. Das ist eine Einstellung der Session,
nicht des Repos, und kann nur Semir setzen.

Was trotzdem immer nachfragt, mit Absicht: Senden von Mails an Dritte, Loeschen von Dateien,
Force-Push. Das bleibt so.

## 6. Unsere drei Postfaecher

Alle drei landen im Gmail-Konto `leanstechgmbh@gmail.com`; eine Suche deckt alle ab:

1. `leanstechgmbh@gmail.com` (auch Website-Formulare „Anfrage über die Website“)
2. `info@leanstech-gmbh.de` (Weiterleitung)
3. `sr@leanstech-gmbh.de` (Weiterleitung; bisher nur als CC gesehen, Weiterleitung fuer direkte Mails pruefen)

Suche nach Postfach: `to:info@leanstech-gmbh.de OR cc:info@leanstech-gmbh.de` usw.

## 7. Automatik: Anfragen zweimal taeglich

Geplante Aufgabe „LEANS Klima – Anfragen“ (07:23 und 15:23 Uhr Berlin) legt pro neuer Kundenanfrage
einen Antwort-Entwurf in Gmail an und liefert eine Tabelle mit Name, Adresse, Telefon, Anliegen.
Jede Ausfuehrung erscheint links als eigene Session. Prompt und Aktivierung: `knowledge/prompts/anfragen-triage.md`.

## 8. Sprache

Sprach-Ein- und -Ausgabe laufen in der Claude-App auf dem Geraet, nicht im Chat-Container.
Der Chat kann sie weder einschalten noch reparieren. Pruefen auf dem Geraet:
Mikrofon-Recht fuer die App in den Systemeinstellungen, Browser-Freigabe fuer das Mikrofon,
Lautstaerke und Stummschaltung. In der Terminal-Version von Claude Code gibt es dafuer die
Einstellung `voice` (siehe `/config`).

## 9. Wenn etwas nicht geht

1. Welches Werkzeug wurde aufgerufen und mit welcher Fehlermeldung? Wortgetreu notieren.
2. Steht der Fall in Abschnitt 1? Dann den dort beschriebenen Weg nehmen.
3. Sonst: Fall hier im Protokoll unter „Bekannte Grenzen“ ergaenzen, nicht in eine neue Datei.

### Bekannte Grenzen

- Gmail-Anhaenge sind nur ueber Drive oder Upload lesbar (Stand 2026-10-24).
- Die PowerShell-Skripte unter `scripts/` laufen nur lokal unter Windows. In Cloud-Sessions
  gibt es kein `pwsh`; dort entfallen die Schritte `leans-live.ps1 status` und `announce`.
