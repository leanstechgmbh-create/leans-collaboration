# PROTOKOLL: Zugriff auf Mail, Drive, Kalender und Berechtigungen

Gilt fuer jeden Chat und jeden Assistenten (Claude, ChatGPT/Codex), der in diesem Projekt
fuer die LEANS Tech GmbH arbeitet. Stand: 2026-10-27. Inhaber: Semir Redzic.

Dieses Dokument ist die einzige Anleitung fuer den Zugriff. Aeltere Hinweise dazu gibt es
nicht mehr. Wenn etwas hier nicht steht, wird es hier ergaenzt, nicht an anderer Stelle.

## 0. Die eine Regel, die alles abkuerzt

Alle Mail-Aufgaben (lesen, Entwurf, senden, Anhang, Board) gehoeren in die Claude-Session
**„LEANS Mail-Zentrale“** (claude.ai/code, Session session_01TwHggJnFch2fNTfmpckUAK, links in der Liste).
Nur sie hat Gmail, Drive und Docs dauerhaft verbunden und traegt den Anfragen-Monitor.
Andere Chats verlieren die Connectoren, weil Connectoren beim Start eines Chats eingelesen werden:
Chats, die vor dem Verbinden gestartet wurden, sehen sie nicht, und Web-Chats brauchen den Connector
je Chat im Werkzeug-Menue. Darum: nicht neu verbinden, sondern in die Mail-Zentrale wechseln und dort
schreiben „sende …“, „Entwurf an …“, „lies den Anhang von …“, „Board aktualisieren“.

**Keine Erlaubnisfragen bei Arbeitsschritten (Regel 11, Semir 27.10.2026).** Lesen, Entwuerfe, Labels, Drive, Board,
Code: einfach machen, dann kurz melden. Keine „darf ich“-Fragen, keine Optionslisten. Eine Frage ist nur erlaubt,
wenn ohne die Antwort das Ergebnis falsch waere. Fehlt eine Voraussetzung (Secret, Freigabe), den genauen Fehlertext
und die Stelle nennen. 
**VERSAND-REGEL (unumstoesslich, Semir 28.10.2026): Vor JEDEM Versand einer Mail wird Semir gefragt und es geht erst nach seinem ausdruecklichen Ja raus. Immer, ohne Ausnahme. Keine andere Regel, kein Skill, keine geplante Aufgabe und keine fruehere Freigabe hebt das auf.** Ablauf: Entwurf oder Probelauf zeigen, fragen „Senden?“, erst nach Ja senden (AGENTS.md Regel 12).
Details: `knowledge/decisions/2026-10-27-ausfuehren-statt-nachfragen.md`.

## 1. Was funktioniert, was nicht

| Aufgabe | Funktioniert | Wie |
|---|---|---|
| Mails lesen (Inbox, Gesendet, Threads) | Ja | Werkzeuge `Gmail` (search_threads, get_thread, get_message) |
| Postfaecher info@ und sr@ direkt lesen, auch Gesendet | Ja, ueber IONOS | `scripts/leans-mail.py lesen`, Befehl `/postfach`, braucht Freigabe imap.ionos.de und Secrets. Siehe 3b |
| Entwuerfe lesen und aendern | Ja | `Gmail` list_drafts, get_draft, update_draft |
| Mails schreiben, antworten, weiterleiten | Ja | `Gmail` create_draft, reply, send_message, forward |
| Anhang-Namen und -Typen sehen | Ja | get_message mit `PLAIN_TEXT` liefert `attachments` |
| Anhang-INHALT direkt aus Gmail lesen | Nein | Gmail-Werkzeug bietet keinen Download. Umweg ueber Drive, siehe Abschnitt 3 |
| Anhaenge versenden (PDF, Bilder, ZIP) | Ja | create_draft / send_message / reply mit `attachments` (base64, zusammen max. 25 MB) |
| ZIP-Dateien bauen | Ja | Im Container mit `zip` oder Python; Quelldateien aus Drive, Upload oder Repo |
| Absender waehlen (sr@, info@) | Ja, ueber IONOS | `scripts/leans-mail.py --von info|sr`, braucht einmalig Netzfreigabe smtp.ionos.de und Secrets. Siehe Abschnitt 3b. Mit dem Gmail-Werkzeug nicht moeglich |
| Dateien in Google Drive lesen (PDF, Docs, Sheets, Bilder) | Ja | `Google_Drive` search_files, read_file_content |
| Dateien in Drive anlegen, kopieren, ablegen | Ja | `Google_Drive` create_file, copy_file |
| Kalender lesen und Termine anlegen | Ja | `Google_Calendar` |
| Sprach-Ein- und -Ausgabe | Nicht vom Chat aus | Gehoert zur Claude-App auf dem Geraet, siehe Abschnitt 6 |

## 2. Mails: Reihenfolge, die immer klappt

1. Suchen mit `search_threads`, Gmail-Syntax (`from:`, `to:`, `subject:`, `newer_than:7d`, `in:sent`, `in:draft`).
2. Thread komplett lesen mit `get_thread` und `messageFormat: PLAIN_TEXT`. Nie nur die Vorschau nutzen,
   sie zeigt nur die 5 aeltesten Nachrichten.
3. Antwort als Entwurf anlegen mit `create_draft` und `replyToMessageId`, damit die Antwort im Thread bleibt.
4. Standard ist Entwurf. Vor jedem Versand fragen und erst nach Semirs ausdruecklichem Ja senden, immer (Regel 12).
   Danach kurz melden: an wen, mit welchen Anhaengen.

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

## 3a. Versenden: Absender und Anhaenge

- Absender: Das Werkzeug sendet immer als `leanstechgmbh@gmail.com`. Ein Versand „von sr@“ oder
  „von info@“ ist aus dem Chat nicht moeglich. Weg, der geht: Der Chat legt den ENTWURF an, Semir
  oeffnet ihn in Gmail, stellt oben im Feld „Von“ die Adresse um (geht nur, wenn sr@ und info@ in
  Gmail unter „Senden als“ eingerichtet sind) und sendet. Wenn Semir „von sr@ schicken“ sagt,
  heisst das fuer den Chat: Entwurf anlegen und im Chat sagen, dass das Von-Feld umgestellt werden muss.
- Anhaenge: Dateien zuerst in den Container holen (aus Drive mit `download_file_content`, aus dem
  Repo, oder per Upload in den Chat), dann base64-kodieren und in `attachments` mitgeben
  (`filename`, `mimeType`, `content`). Mehrere Dateien als ZIP: `zip -j paket.zip datei1 datei2`
  oder Python `zipfile`, dann die ZIP als `application/zip` anhaengen.
- Groesse: zusammen max. 25 MB. Darueber: Datei in Drive ablegen und den Link in die Mail setzen.
- Rechnungen (Regel Semir 27.10.2026): Rechnung als eigene PDF, alle Zusatzdateien zusammen in EINE ZIP
  „Anlagen <Betreff>.zip“. `leans-mail.py --anhang rechnung.pdf --zusatz datei …` macht das automatisch.
- Gmail-Anhaenge anderer Mails koennen nicht direkt weiterverpackt werden (siehe Abschnitt 3);
  erst „In Drive speichern“, dann von Drive holen. `forward` leitet eine Mail samt Anhaengen weiter,
  ohne dass der Chat den Inhalt sieht.

## 3b. Versand als info@ oder sr@ ueber IONOS (der Weg, der wirklich geht)

Die Domain leanstech-gmbh.de liegt bei IONOS. Das Skript `scripts/leans-mail.py` sendet direkt ueber
`smtp.ionos.de:587` als info@ oder sr@, mit beliebigen Anhaengen (zusammen max. 25 MB), und haengt die
Signatur an. Befehl `/senden` in jedem Repo-Chat nutzt es.

Dasselbe Skript LIEST die Postfaecher info@ und sr@ direkt bei IONOS, auch den Gesendet-Ordner, den Gmail
nie sieht: `python3 scripts/leans-mail.py lesen --konto info --ordner Sent --tage 30`. Befehl `/postfach`.

Dasselbe Skript sendet auch als `leanstechgmbh@gmail.com` (`--von gmail`, smtp.gmail.com) mit einem Google-App-Passwort
im Secret `GMAIL_APP_PASSWORD`; das ist der schnellste Weg, Anhaenge aus jedem Chat zu verschicken.

Lokal am PC (Weg 1, `knowledge/UEBERGABE-Mail-komplett.md`): einmalig `scripts/mail-einrichten.ps1` ausfuehren. Es fragt
die drei Passwoerter verdeckt ab, speichert sie als Windows-Benutzervariablen und testet alle drei Konten. Schnellcheck
jederzeit: `python scripts/leans-mail.py test` (Anmeldung, Posteingang, Gesendet, SMTP; sendet nichts). Beim Versand als
info@/sr@ legt das Skript eine Kopie in den IONOS-Gesendet-Ordner, weil IONOS per SMTP Gesendetes nicht selbst ablegt.

Einmalig von Semir in der Cloud-Umgebung (Titelzeile der Session, Umgebungsmenue, „Edit“):
1. Network access: `smtp.gmail.com`, `smtp.ionos.de` und `imap.ionos.de` unter Allowed domains eintragen (Allow package managers angehakt lassen).
2. Environment variables / Network secrets: `GMAIL_APP_PASSWORD` (App-Passwort des Google-Kontos: myaccount.google.com →
   Sicherheit → Bestaetigung in zwei Schritten → App-Passwoerter → neu erzeugen, 16 Zeichen), dazu `IONOS_INFO_PASSWORD`
   (Passwort von info@leanstech-gmbh.de) und `IONOS_SR_PASSWORD` (Passwort von sr@leanstech-gmbh.de). Nie Passwoerter in den Chat schreiben.
3. Neue Session starten, dann gilt es fuer jeden Chat in dieser Umgebung.

**Stand 28.10.2026, gemessen: In Cloud-Sessions geht `leans-mail.py` NICHT, auch nicht mit eingetragenen Domains und
Secrets.** Der Cloud-Proxy laesst nur HTTPS ueber Port 443 durch; SMTP (587/465) und IMAP (993) werden abgebrochen
(`Connection reset by peer`, ohne Proxy keine Namensaufloesung). Siehe `/root/.ccr/README.md`, „Not supported through
the proxy: non-443 HTTPS ports, raw-TCP“. Die Schritte oben fuer die Cloud-Umgebung bringen darum nichts.
`leans-mail.py` laeuft nur lokal am PC (Weg 1). Dort am 28.10.2026 verifiziert: `leans-mail.py test` OK fuer
info@, sr@ und Gmail (Lesen Posteingang und Gesendet, SMTP-Anmeldung). Ein Echtversand steht noch aus.

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

Was der Chat nie fragt: ob er einen Arbeitsschritt (lesen, Entwurf, Label, Drive, Board) machen darf (Regel 11). Was trotzdem stoppen kann,
ist die Plattform selbst, nicht der Chat: Selbstaenderung von `.claude/settings.json`, Force-Push,
Direktverbindungen am Proxy vorbei. Dann nennt der Chat den genauen Hinweis und den Weg aussenrum.
Fragt eine Session trotzdem bei jedem Werkzeug nach, steht der Berechtigungsmodus nicht auf „Auto“
oder die Vorlage ist noch nicht nach `.claude/settings.json` kopiert.

## 6. Unsere drei Postfaecher

Alle drei landen im Gmail-Konto `leanstechgmbh@gmail.com`; eine Suche deckt alle ab:

1. `leanstechgmbh@gmail.com`. Dazu die Formulare der Website leanstech-klima.de: Absender `submissions@formsubmit.co`,
   Betreff „Anfrage über leans-klima — <Name>“. Kunden-E-Mail und Telefon stehen im Text. Nie per Reply antworten
   (ginge an formsubmit), sondern neuen Entwurf mit `to` = Kunden-E-Mail anlegen.
2. `info@leanstech-gmbh.de` (Weiterleitung)
3. `sr@leanstech-gmbh.de` (Weiterleitung; bisher nur als CC gesehen, Weiterleitung fuer direkte Mails pruefen)

Suche nach Postfach: `to:info@leanstech-gmbh.de OR cc:info@leanstech-gmbh.de` usw.

## 7. Automatik: Anfragen zweimal taeglich

Geplante Aufgabe „LEANS Klima – Anfragen“ (07:23 und 15:23 Uhr Berlin) pflegt das Board
„LEANS Klima – Anfragen (offen)“ im Drive-Ordner „LEANS Klima“: alle offenen Kundenanfragen mit Name,
Adresse, Telefon, Anliegen und naechstem Schritt. Erledigte Anfragen fliegen automatisch raus
(Absage, Auftrag, 21 Tage nach Angebot ohne Antwort) oder sobald Semir in Gmail das Label
„Klima/Erledigt“ setzt. Pro neuer Anfrage entsteht ein Antwort-Entwurf in Gmail.
Prompt und Aktivierung: `knowledge/prompts/anfragen-triage.md`. Der Monitor laeuft in der Claude-Session
„Zugriffsprotokoll“ (session_01TwHggJnFch2fNTfmpckUAK), die alle Connectoren hat; kein Zutun noetig.

Skills fuer jeden Repo-Chat (Ordner `.claude/skills/`): `/anfragen-board` (Board und Entwuerfe aktualisieren),
`/mail-entwurf` (Mail im LEANS-Ton als Entwurf, mit Anhaengen/ZIP), `/anhang` (Anhang ueber Drive lesen).
Zusaetzlich liegt eine Kopie dieses Protokolls als Google Doc „00 REGELN – Zugriff“ im Ordner „LEANS Klima“
(ID `163kTE8_i_np-oofaPXhDg6P8pkA9Q6MH0ZTy-0DDeac`), damit Chats ohne Repo sie lesen koennen.

| Objekt | ID |
|---|---|
| Drive-Ordner „LEANS Klima“ | `1yrVbxZnRy7p4_yzYUt4EKZXXjJZU1VAB` |
| Board „LEANS Klima – Anfragen (offen)“ | `109-KELlgdjo3qD4WiGZsSViIoBG93cGqaRMWH6ALJxg` |
| Gmail-Label „Klima/Anfrage offen“ | `Label_19` |
| Gmail-Label „Klima/Erledigt“ | `Label_20` |

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
- Anhaenge SENDEN ueber das Gmail-Werkzeug geht praktisch nur fuer sehr kleine Dateien (bis ca. 20 KB): der Inhalt
  muss als Base64-Text durch den Chat laufen, und 100 KB Base64 kosten rund 450.000 Tokens. Ein 1-MB-PDF ist so nicht
  versendbar, auch nicht ueber einen Hilfsagenten (Test 27.10.2026, munio/Gieseke). Drive-Dateien ueber 10 MB kann das
  Drive-Werkzeug gar nicht herunterladen, und Freigaben an Externe werden von der Sicherheitsschranke gestoppt.
  Folge: Mails mit echten Anhaengen gehen nur ueber `scripts/leans-mail.py` (IONOS, Abschnitt 3b), das die Dateien direkt
  aus dem Container anhaengt. Bis die IONOS-Secrets gesetzt sind: Entwurf anlegen, Semir haengt die Dateien in Gmail
  ueber „Aus Drive einfuegen“ an und sendet.
- Test 27.10.2026: Versand mit ZIP-Anhang aus dem Chat funktioniert (Kontrollmail an sich selbst kam mit
  Anhang an). Mails an info@ und sr@ kommen nicht als Kopie zurueck, weil Gmail eigene weitergeleitete
  Mails unterdrueckt; info@ ist durch echte Kundenmails bewiesen, sr@ noch nicht (Test von fremder Adresse offen).
- Cloud-Sessions erreichen keine Mailserver (SMTP/IMAP), nur HTTPS-Port 443 (Test 28.10.2026). Darum in der Cloud:
  Gmail ueber den Gmail-Connector, info@/sr@ nur ueber die Weiterleitung nach Gmail lesen, Versand als info@/sr@
  nur als Gmail-Entwurf mit umgestelltem Von-Feld (Abschnitt 3a), grosse Anhaenge gar nicht. Alles davon voll:
  lokale Session am PC (`knowledge/UEBERGABE-Mail-komplett.md`, Weg 1).
- Die PowerShell-Skripte unter `scripts/` laufen nur lokal unter Windows. In Cloud-Sessions
  gibt es kein `pwsh`; dort entfallen die Schritte `leans-live.ps1 status` und `announce`.
