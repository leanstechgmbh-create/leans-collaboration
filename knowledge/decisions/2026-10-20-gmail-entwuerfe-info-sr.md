# Entscheidung: Gmail-Entwuerfe fuer info@ und sr@ (2026-10-20)

## Problem

In Chats wirkte es so, als haetten `info@leanstech-gmbh.de` und `sr@leanstech-gmbh.de`
"keinen Zugang": keine Entwuerfe, keine Anhaenge.

## Befund (geprueft am 2026-10-20 per Gmail-Connector)

- Der Gmail-Connector in Claude ist per OAuth an **genau ein** Konto gebunden:
  `leanstechgmbh@gmail.com`. Es gibt keinen zweiten Connector fuer `info@` oder `sr@`.
- Post an `info@` und `sr@` landet per Weiterleitung/CC in `leanstechgmbh@gmail.com`
  und ist dort lesbar (geprueft: Threads mit `info@leanstech-gmbh.de` als Absender/Empfaenger).
- `create_draft` hat **kein From-/Alias-Feld**. Jeder Entwurf hat als Absender
  `leanstechgmbh@gmail.com` (alle 20 letzten Entwuerfe im Konto bestaetigen das).
- Entwuerfe **mit Anhang** funktionieren: Testentwurf mit `test.txt` wurde erfolgreich
  angelegt und wieder geloescht. Anhaenge werden base64 uebergeben, max. 25 MB,
  groessere Dateien als Drive-Link.
- Nichts ist "kaputt gegangen". Es wurde nie ein Zugang fuer `info@`/`sr@` gebaut,
  der Connector kann das technisch nicht.

## Entscheidung

1. Entwuerfe fuer `info@` / `sr@` werden **immer im Konto `leanstechgmbh@gmail.com`**
   angelegt. Im Entwurf wird oben als erste Zeile vermerkt:
   `[Senden als: info@leanstech-gmbh.de]` bzw. `[Senden als: sr@leanstech-gmbh.de]`.
2. Vor dem Senden waehlt Semir in Gmail im Feld "Von" die passende Adresse
   (Voraussetzung: `info@` und `sr@` sind in Gmail unter
   Einstellungen > Konten und Import > "E-Mail senden als" eingerichtet) und loescht
   die Vermerkzeile.
3. Antworten auf Mails, die an `info@`/`sr@` gingen, werden mit `replyToMessageId`
   als Antwort im selben Thread angelegt; Gmail setzt dann "Von" automatisch auf die
   Empfaengeradresse, wenn "Antworten von derselben Adresse" aktiviert ist.
4. Anhaenge: Datei muss Claude vorliegen (im Chat hochgeladen, in Google Drive, oder
   im Repo/Dateisystem einer Claude-Code-Sitzung). Claude haengt sie direkt an.
   Ueber 25 MB: Datei in Drive ablegen und Link in den Text.

## Was NICHT geht

- Entwurf direkt im Postfach `info@`/`sr@` anlegen (kein Connector dafuer).
- From-Adresse per Connector setzen.
- Aus einem normalen Chat heraus Gmail-Einstellungen ("Senden als") aendern.

## Offene Option

Wenn `info@`/`sr@` eigene Google-Workspace-Postfaecher sind und direkt bedient werden
sollen: in claude.ai unter Einstellungen > Connectors den Gmail-Connector mit dem
jeweiligen Konto verbinden. Pro Claude-Konto ist nur eine Gmail-Verbindung moeglich,
daher ist die Alias-Loesung oben der Standardweg.
