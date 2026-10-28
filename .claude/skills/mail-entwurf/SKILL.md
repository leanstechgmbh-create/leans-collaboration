---
name: mail-entwurf
description: Antwort- oder neue Mail als Gmail-Entwurf im LEANS-Ton anlegen, optional mit Anhängen (PDF, Bilder, ZIP). Aufrufen mit /mail-entwurf <Kunde oder Thema>, oder wenn Semir sagt „schreib dem Kunden“, „antworte auf“, „Mail an … vorbereiten“, „von sr@/info@ schicken“.
---

# Mail-Entwurf anlegen

Regel 11 (`AGENTS.md`): Arbeitsschritte (lesen, Entwurf, Labels, Drive, Board) ohne Erlaubnisfragen erledigen, danach kurz melden. Versand nur nach ausdrücklichem „senden“.

Vorher `knowledge/PROTOKOLL-Zugriff.md` Abschnitte 2, 3 und 3a lesen.

## Ablauf

1. Thread finden: `mcp__Gmail__search_threads` (z. B. `from:<kunde>` oder `subject:<stichwort>`), dann
   `mcp__Gmail__get_thread` mit `PLAIN_TEXT`, um den Verlauf und die ID der letzten Kundennachricht zu haben.
2. Prüfen, ob schon ein Entwurf existiert: `mcp__Gmail__list_drafts` mit `to:<kundenadresse>`.
3. Entwurf anlegen: `mcp__Gmail__create_draft` mit `replyToMessageId` der letzten Kundennachricht.
   Ausnahme Website-Formulare (Absender `submissions@formsubmit.co`): kein Reply, sondern `to` = Kunden-E-Mail
   aus dem Formulartext und eigener Betreff „Ihre Anfrage über leanstech-klima.de – <Thema>“.
4. Ton: „Guten Tag Herr/Frau <Name>, vielen Dank für Ihre Anfrage/Nachricht.“ Kurz bestätigen, was verstanden
   wurde, nächsten Schritt nennen, fehlende Angaben erbitten. Keine Preise ohne Freigabe von Semir.
5. Signatur genau so:

```
Freundliche Grüße
Semir Redzic
LEANS Tech GmbH
Klima ▪ Lüftung ▪ Sanitär ▪ Heizung
Tel: +49 152 16607036
info@leanstech-gmbh.de
www.leanstechgmbh-hkls.de
```

6. Bankverbindung, falls nötig: LEANS Tech GmbH, Berliner Volksbank, IBAN DE21 1009 0000 2911 7280 04, BIC BEVODEBB.
   Kein Adyen.

## Absender sr@ oder info@

Das Werkzeug sendet immer als leanstechgmbh@gmail.com. Wenn Semir „von sr@“ oder „von info@“ sagt:
Entwurf anlegen und im Chat in einem Satz sagen, dass er in Gmail oben im Feld „Von“ die Adresse umstellen muss.

## Anhänge

- Quelle: Drive (`mcp__Google_Drive__download_file_content`), Repo oder Upload in den Chat.
  Gmail-Anhänge anderer Mails sind nicht lesbar; erst „In Drive speichern“.
- Rechnungen: Rechnung als eigene PDF, alle Zusatzdateien in EINE ZIP „Anlagen <Betreff>.zip“
  (`zip -j "Anlagen <Betreff>.zip" datei1 datei2`). Regel in `knowledge/decisions/2026-10-27-rechnungsversand-anhaenge.md`.
- base64 kodieren (`base64 -w0 datei`) und in `attachments` mitgeben: `filename`, `mimeType`, `content`.
- Zusammen max. 25 MB, sonst Datei in Drive ablegen und Link in den Text.

## Senden

Nur wenn Semir ausdrücklich „senden“ sagt: `mcp__Gmail__send_message` mit `draftId`, dann melden, was rausging.
Sonst bleibt es ein Entwurf. Für Absender info@/sr@ den Skill `/senden` nehmen.
