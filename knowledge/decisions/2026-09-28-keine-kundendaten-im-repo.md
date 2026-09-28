# Entscheidung: Keine Kunden- und Rechnungsdaten im Repository

- Datum: 2026-09-28
- Von: Claude
- Status: gilt ab sofort, bis Semir anders entscheidet

## Entscheidung

Rechnungen, Rechnungsentwuerfe, Angebote, Mahnungen, Kundennamen, Adressen, Betraege, Bankdaten und Auszuege aus Kundenkorrespondenz werden nicht in diesem Repository abgelegt. Solche Arbeitsergebnisse gehoeren in das Google Drive der LEANS Tech GmbH. Im Repository steht hoechstens ein Hinweis auf den Drive-Ordner, ohne personenbezogene Daten oder Betraege.

## Begruendung

Das GitHub-Repository `leanstechgmbh-create/leans-collaboration` ist oeffentlich (Stand 2026-09-28). Alles, was hier committet wird, ist fuer jeden lesbar und bleibt in der Git-Historie, auch wenn es spaeter geloescht wird.

## Folgen fuer die Arbeit

- Vor dem Committen pruefen, ob eine Datei Kunden-, Mitarbeiter- oder Finanzdaten enthaelt. Wenn ja: nach Drive, nicht ins Repo.
- Wiederverwendbare Ablaeufe und Prompts duerfen hier liegen, wenn sie allgemein formuliert sind (siehe [[../prompts/rechnungsentwurf-aus-unterlagen]]).
- Offene Frage an Semir: Soll das Repository auf privat umgestellt werden?
