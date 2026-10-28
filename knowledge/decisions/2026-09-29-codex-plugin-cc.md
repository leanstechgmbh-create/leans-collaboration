# Entscheidung: Codex Plugin fuer Claude Code

- Datum: 2026-09-29
- Status: Angenommen
- Von: Claude, auf Anfrage des Nutzers
- Anleitung: `docs/Codex-Plugin.md`

## Kontext

ChatGPT/Codex und Claude arbeiten bisher nur indirekt zusammen: ueber das Board
`LEANS-Uebergabe.md` und den lokalen Live-Status aus `scripts/leans-live.ps1`. Jede Uebergabe und
jede Review muss der andere Assistent erst beim naechsten Aufgabenstart aufgreifen. Gesucht war eine
direkte Verbindung zwischen Claude und ChatGPT.

## Entscheidung

Wir nutzen das offizielle OpenAI-Plugin [`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc)
in Claude Code. Claude kann damit Codex direkt fuer Reviews (`/codex:review`,
`/codex:adversarial-review`), Teilaufgaben (`/codex:rescue`) und Sitzungsuebergaben
(`/codex:transfer`) aufrufen.

Das Review Gate (`/codex:setup --enable-review-gate`) bleibt standardmaessig aus.

## Begruendung

- Offiziell von OpenAI gepflegt, statt eines Community-Plugins.
- Nutzt die vorhandene Codex-Anmeldung per ChatGPT-Abo, kein zusaetzliches Konto noetig.
- Arbeitet im selben lokalen Checkout wie der LEANS-Ordner.
- Reviews sind sofort verfuegbar, statt auf die naechste ChatGPT/Codex-Sitzung zu warten.

## Gepruefte Alternativen

| Alternative | Warum nicht |
|---|---|
| Codex Dispatch, codex-review, session-handoff, Seldon (Anthropic Plugin-Verzeichnis) | Community-Plugins; decken Teilbereiche ab, die das offizielle Plugin ebenfalls abdeckt. |
| [thepushkarp/cc-codex-plugin](https://github.com/thepushkarp/cc-codex-plugin) | Community-Plugin mit aehnlichem Zweck; das offizielle Plugin ist vorzuziehen. |
| [religa/multi_mcp](https://github.com/religa/multi_mcp) | Mehrere Modelle (GPT, Claude, Gemini) ueber API Keys; mehr als gebraucht, kein Codex-Checkout. |
| Nur Board und `leans-live.ps1` | Bleibt bestehen, aber ohne direkte Verbindung. |

## Konsequenzen

- Die Verbindung ist einseitig: Claude ruft Codex auf. ChatGPT/Codex uebergibt weiter ueber das
  Board an Claude.
- Funktioniert nur lokal mit angemeldeter Codex CLI, nicht in Claude-Cloud-Sitzungen.
- Codex-Nutzung zaehlt gegen die Limits des ChatGPT-Abos.
- `/codex:rescue` kann Dateien im gemeinsamen Checkout aendern. Betroffene Dateien vorher mit
  `leans-live.ps1 announce` ankuendigen.
- Relevante Codex-Ergebnisse muessen ins Board oder nach `knowledge/` uebertragen werden, sonst
  bleiben sie nur in der Claude-Sitzung.
- Die Plugin-Anleitung erwaehnt Windows nicht ausdruecklich. Codex selbst laeuft laut OpenAI nativ
  unter Windows. Erster Test auf dem LEANS-Rechner steht noch aus.
