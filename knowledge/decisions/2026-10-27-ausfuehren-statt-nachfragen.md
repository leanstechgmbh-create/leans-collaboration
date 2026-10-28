# Entscheidung: Arbeitsschritte ohne Erlaubnisfragen

- Datum: 2026-10-27, praezisiert 2026-10-28
- Von: Semir Redzic
- Gilt für: jeden Chat und jeden Assistenten (Claude, ChatGPT/Codex)

## Regel

1. Arbeitsschritte werden einfach gemacht, ohne „darf ich“: Mails lesen und suchen, Entwürfe anlegen, Labels setzen,
   Drive-Dateien lesen und ablegen, Board schreiben, Code ändern, Anhänge vorbereiten, Kontoauszüge prüfen.
2. Keine Optionslisten, keine Bestätigungsschleifen für solche Schritte. Ergebnis zeigen, danach ein bis drei Sätze Meldung.
3. Nachfragen nur, wenn ohne die Antwort das Ergebnis falsch wäre (Empfängeradresse fehlt, zwei Kunden mit gleichem Namen).
   Dann genau eine konkrete Frage.
4. Fehlt eine Voraussetzung (Secret, Netzfreigabe, Connector): Fehlertext und Stelle nennen (Protokoll 3b, 5, 9), nicht
   fragen, ob Semir sie setzen möchte.

## Ausnahme: Versand

Mails an Dritte gehen nur raus, wenn Semir ausdrücklich „senden“ / „verschick es“ sagt. Vorher Entwurf oder Probelauf
zeigen. Das ist keine Erlaubnisfrage, sondern die Freigabe des Inhalts. Nichts löschen ohne Anweisung.

## Was weiterhin stoppt

- Sicherheitsschranke von Claude Code (Selbständerung von `.claude/settings.json`, Force-Push, Direktverbindungen am
  Proxy vorbei, Freigaben an Externe). Der Chat meldet den Hinweis und den Weg außenrum.
- Berechtigungsabfragen der Session: Modus „Auto“ beim Start und Vorlage `docs/claude-settings.vorlage.json` nach
  `.claude/settings.json` kopieren (Protokoll Abschnitt 5).

## Umsetzung

- `AGENTS.md` Regel 11, `knowledge/PROTOKOLL-Zugriff.md` Abschnitte 0, 2, 5, alle Skills unter `.claude/skills/`.
