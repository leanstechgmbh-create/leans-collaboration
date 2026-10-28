---
name: postfach
description: Direkt in die IONOS-Postfächer info@ und sr@leanstech-gmbh.de schauen, Posteingang und Gesendet, inklusive Anhänge herunterladen. Aufrufen mit /postfach, oder wenn Semir fragt „was wurde von info@ geschickt“, „ist die Mail an … rausgegangen“, „was liegt in sr@“, „zeig mir den Gesendet-Ordner“.
---

# Postfach info@ / sr@ lesen

Regel 11 (`AGENTS.md`): Arbeitsschritte (lesen, Entwurf, Labels, Drive, Board) ohne Erlaubnisfragen erledigen, danach kurz melden. VERSAND: vor jedem Senden fragen, erst nach Semirs ausdrücklichem Ja senden, immer, ohne Ausnahme (Regel 12).

Gmail zeigt nur, was IONOS weiterleitet, und nie den Gesendet-Ordner von info@ oder sr@.
Dafür gibt es `scripts/leans-mail.py lesen` (IMAP direkt bei IONOS; `--konto gmail` liest das Gmail-Konto per IMAP).
Voraussetzung: Passwörter `IONOS_INFO_PASSWORD` / `IONOS_SR_PASSWORD` / `GMAIL_APP_PASSWORD`.
Lokal am PC (Weg 1) setzt sie `scripts/mail-einrichten.ps1`; in der Cloud zusätzlich `imap.ionos.de`, `smtp.ionos.de`
unter Allowed domains. Unter Windows `python` statt `python3`. Schnellcheck aller drei Konten:
`python3 scripts/leans-mail.py test` (sendet nichts).
`--ordner Sent` findet den Gesendet-Ordner automatisch (IONOS „Gesendete Objekte“, Gmail „[Gmail]/Gesendet“).

## Befehle

```bash
# Übersicht Posteingang info@, letzte 7 Tage
python3 scripts/leans-mail.py lesen --konto info --ordner INBOX --tage 7

# Was wurde von sr@ gesendet, letzte 30 Tage, Suche nach Stichwort
python3 scripts/leans-mail.py lesen --konto sr --ordner Sent --tage 30 --suche "Angebot 412"

# Eine Nachricht komplett lesen und Anhänge speichern
python3 scripts/leans-mail.py lesen --konto info --ordner INBOX --uid 1234 --volltext --anhang-speichern ./anhaenge

# Ordnernamen bei IONOS nachsehen (falls Sent anders heißt)
python3 scripts/leans-mail.py lesen --konto info --ordner-liste
```

## Ablauf bei „ist die Mail an X rausgegangen?“

1. `lesen --konto info --ordner Sent --tage 30 --suche "<Kundenname oder Betreff>"`, dasselbe für `--konto sr`.
2. Zusätzlich im Gmail-Konto: `mcp__Gmail__search_threads` mit `in:sent <Stichwort>`.
3. Ergebnis als kurze Liste: Datum, Absender, Empfänger, Betreff, Anhänge. Nichts raten; „nicht gefunden“ ist eine Antwort.

Exit-Code 2 = Konfiguration fehlt, 3 = Netz gesperrt, 4 = Passwort falsch. Fehlermeldung wörtlich an Semir geben.
Anhänge, die so gespeichert wurden, können direkt gelesen oder mit `/senden` weitergeschickt werden.
