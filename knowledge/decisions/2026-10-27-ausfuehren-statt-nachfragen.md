# Entscheidung: Anweisung ausführen, nicht nachfragen

- Datum: 2026-10-27
- Von: Semir Redzic
- Gilt für: jeden Chat und jeden Assistenten (Claude, ChatGPT/Codex), jede Aufgabe (Mail, Drive, Board, Code)

## Regel

1. Sagt Semir, was zu tun ist, wird es gemacht. Punkt. Beispiele: „sende“, „verschick es“, „erledige den Chat
   <Kunde>“, „mach die Anhänge rein“, „lösch die Testmails“, „setz das Label“, „schreib das ins Board“.
2. Keine Rückfrage wie „soll ich wirklich senden?“, „bist du sicher?“, „möchtest du vorher den Entwurf sehen?“.
   Keine Liste mit Optionen, wenn die Anweisung schon klar ist. Ergebnis zeigen, nicht Erlaubnis holen.
3. Erst machen, dann melden: ein bis drei Sätze, was rausging, an wen, mit welchen Anhängen.
4. Nur ein Grund zum Nachfragen: Ohne die Antwort wäre das Ergebnis falsch oder geht an die falsche Person.
   Beispiele: Empfängeradresse fehlt und ist nirgends zu finden; zwei Kunden mit gleichem Namen; Rechnungsnummer
   unklar. Dann genau eine konkrete Frage, nicht fünf.
5. Fehlt eine Voraussetzung (Secret, Netzfreigabe, Connector), nicht fragen, ob Semir sie setzen möchte,
   sondern den genauen Fehlertext und die Stelle nennen, wo er sie setzt (Protokoll Abschnitt 3b, 5, 9).
6. „Entwurf“ bleibt Entwurf, „senden“ heißt senden. Was Semir nicht gesagt hat, wird nicht gemacht
   (nichts löschen, nichts an Dritte senden, keine Preise erfinden). Das ist keine Rückfrage, das ist Umfang.

## Was weiterhin stoppt, und warum

- Die Sicherheitsschranke von Claude Code selbst (Selbständerung von `.claude/settings.json`, Force-Push,
  Direktverbindungen am Proxy vorbei). Das ist kein Nachfragen des Chats, das ist die Plattform. Der Chat
  meldet dann den genauen Hinweis und den Weg außenrum (z. B. Vorlage `docs/claude-settings.vorlage.json`).
- Die Berechtigungsabfragen der Session (Permission-Modus). Dagegen hilft nur: Modus „Auto“ beim Start
  der Session und die Vorlage einmal nach `.claude/settings.json` kopieren (Protokoll Abschnitt 5).

## Umsetzung

- `AGENTS.md` Regel 11.
- `knowledge/PROTOKOLL-Zugriff.md` Abschnitt 0 (Kasten „Anweisung = Auftrag“) und Abschnitt 5.
- Alle Skills unter `.claude/skills/` tragen die Zeile „Regel 11: ausführen, nicht nachfragen“.
- Geplante Aufgabe „Klima-Postfach prüfen + neue Anfragen zu Chats“ (legt die Kunden-Chats an): Prompt ergänzt,
  damit jeder neue Kunden-Chat die Regel von Anfang an kennt.
