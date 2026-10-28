# Codex Plugin fuer Claude Code

Direkte Verbindung von Claude Code zu OpenAI Codex ueber das offizielle Plugin
[`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc). Die Entscheidung dazu steht in
`knowledge/decisions/2026-09-29-codex-plugin-cc.md`.

## Was das Plugin ist

- Offizielles Plugin von OpenAI fuer Claude Code.
- Claude Code gibt Reviews und Aufgaben an **Codex** ab und holt die Ergebnisse zurueck.
- Es nutzt die lokale Codex CLI und den Codex App Server auf demselben Rechner, also dieselbe
  Anmeldung, dieselbe Konfiguration und denselben Repository-Checkout.
- Es verbindet mit **Codex**, nicht mit dem ChatGPT-Chat im Browser oder in der App.
- Die Verbindung laeuft in eine Richtung: Claude ruft Codex auf. Uebergaben von ChatGPT/Codex an
  Claude laufen weiter ueber `LEANS-Uebergabe.md` und `scripts/leans-live.ps1`.

## Voraussetzungen

- ChatGPT-Abo (auch Free) oder OpenAI API Key. Die Nutzung zaehlt gegen die Codex-Nutzungslimits.
- Node.js 18.18 oder neuer.
- Claude Code lokal auf dem Rechner, auf dem auch Codex laeuft, fuer LEANS also im Ordner
  `C:\Users\semir\Documents\LEANS-Live`.

In einer Claude-Cloud-Sitzung (claude.ai/code) funktioniert das Plugin nicht, weil dort keine
angemeldete Codex CLI vorhanden ist.

## Einmalig einrichten

Am einfachsten: einen neuen lokalen Claude-Code-Chat im LEANS-Ordner starten und den Block aus
`knowledge/prompts/codex-plugin-einrichten.md` einfuegen. Der Chat erledigt die Schritte unten selbst.

Von Hand: Claude Code im LEANS-Ordner starten und dort eingeben:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Alternativ ohne laufende Claude-Code-Sitzung direkt in PowerShell (danach Claude Code neu starten
und `/codex:setup` ausfuehren):

```powershell
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
```

Marketplace-Name `openai-codex` und Plugin-Name `codex` stammen aus dem Manifest des Plugins
(`.claude-plugin/marketplace.json`, Version 1.0.6, Stand 2026-09-30).

`/codex:setup` prueft, ob Codex installiert und angemeldet ist. Fehlt Codex und ist npm vorhanden,
bietet der Befehl die Installation an. Alternativ selbst installieren:

```powershell
npm install -g @openai/codex
```

Falls Codex installiert, aber nicht angemeldet ist, in Claude Code ausfuehren:

```text
!codex login
```

`codex login` unterstuetzt die Anmeldung mit ChatGPT-Konto oder API Key.

Erfolgreich eingerichtet ist es, wenn die `/codex:`-Befehle erscheinen und `/agents` den Subagent
`codex:codex-rescue` zeigt. Erster Test:

```text
/codex:review --background
/codex:status
/codex:result
```

**Windows-Test am LEANS-PC (2026-10-28):** Laeuft. Node v24.16.0, npm 11.13.0, Codex CLI 0.147.0
waren schon installiert, Codex war bereits mit dem ChatGPT-Konto angemeldet. Plugin 1.0.6 per
PowerShell installiert (`claude plugin marketplace add …` und `claude plugin install …`, beides ohne
Fehler, Scope user). `/codex:setup` meldet `Status: ready` (advanced runtime, Review Gate aus).
Erster Test-Review (`/codex:review --background`) brach ab mit `400 model_not_found`: In
`~/.codex/config.toml` stand `model = "gpt-6-luna"`, das mit ChatGPT-Anmeldung nicht erlaubt ist
(betraf auch `codex exec`, also Codex insgesamt). Behoben durch `model = "gpt-5.6-sol"` (Sicherung:
`config.toml.sicherung-2026-10-28`); erlaubte Modelle stehen in `~/.codex/models_cache.json`.
Zweiter Test-Review lief vollstaendig durch (ca. 15 Min.), `/codex:status` und `/codex:result`
zeigten Ergebnis und Codex-Session-ID. Die Verbindung ist damit fertig.
Hinweise: Node 24 gibt beim Start eine harmlose `DEP0190`-Warnung aus; Codex meldet ausserdem
`failed to load skill …\ugc-factory\styles\01-cinematic\SKILL.md` (fehlender YAML-Kopf), ohne Folgen.
Bei Problemen zuerst `/codex:setup` ausfuehren
und die [Codex-Windows-Doku](https://developers.openai.com/codex/windows) pruefen.

## Befehle

| Befehl | Zweck | Aendert Dateien |
|---|---|---|
| `/codex:review` | Normales Code-Review der aktuellen Aenderungen, mit `--base main` gegen einen Branch. | Nein |
| `/codex:adversarial-review` | Kritisches Review, das Design und Annahmen hinterfragt. Nimmt Fokustext nach den Flags. | Nein |
| `/codex:rescue` | Gibt eine Untersuchung oder Korrektur an Codex ab. Flags: `--background`, `--wait`, `--resume`, `--fresh`, `--model`, `--effort`. | Ja, moeglich |
| `/codex:transfer` | Macht aus der aktuellen Claude-Sitzung einen Codex-Thread und gibt `codex resume <session-id>` aus. | Nein |
| `/codex:status` | Laufende und letzte Codex-Jobs dieses Repositorys. | Nein |
| `/codex:result` | Endergebnis eines fertigen Jobs, inklusive Codex-Session-ID. | Nein |
| `/codex:cancel` | Bricht einen laufenden Hintergrund-Job ab. | Nein |
| `/codex:setup` | Prueft Installation und Anmeldung, verwaltet das Review Gate. | Nein |

Beispiele:

```text
/codex:review --base main
/codex:adversarial-review --background pruefe die Review-Logik in scripts/leans-live.ps1 auf Race Conditions
/codex:rescue --background untersuche, warum tests/leans-live.tests.ps1 fehlschlaegt
```

Delegierte Jobs lassen sich direkt in Codex fortsetzen: `codex resume <session-id>` mit der ID aus
`/codex:result` oder `/codex:status`.

## Einbindung in den LEANS-Ablauf

Das Plugin ergaenzt Board und Live-Status, es ersetzt sie nicht.

| Situation | Bisher | Mit Plugin |
|---|---|---|
| Claude will ein Code-Review von Codex | `leans-live.ps1 request-review -Assistant claude -Target chatgpt -Question "..."`, warten bis ChatGPT/Codex die Review uebernimmt | `/codex:review` oder `/codex:adversarial-review`, Ergebnis sofort in der Claude-Sitzung |
| Claude uebergibt laufende Arbeit an Codex | Eintrag `AN CHATGPT: OFFEN` im Board | `/codex:transfer`, danach Board-Eintrag mit dem ausgegebenen `codex resume <session-id>` unter "Wo liegt es" |
| Claude gibt eine abgegrenzte Teilaufgabe ab | Board-Eintrag | `/codex:rescue --background`, Ergebnis mit `/codex:result` |
| ChatGPT/Codex uebergibt an Claude | Eintrag `AN CLAUDE: OFFEN` im Board | Unveraendert, das Plugin deckt diese Richtung nicht ab |

Regeln:

1. Board und `leans-live.ps1 status` bleiben der Start jeder Aufgabe.
2. Vor `/codex:rescue` die betroffenen Dateien mit `leans-live.ps1 announce -Assistant claude`
   ankuendigen. Codex arbeitet im selben Checkout; Claude bearbeitet diese Dateien nicht, solange
   der Job laeuft.
3. Ergebnisse, die fuer spaeter relevant sind, gehoeren ins Board oder nach `knowledge/`. Die
   Codex-Ausgabe existiert sonst nur in der jeweiligen Claude-Sitzung.
4. Nach `/codex:transfer` immer einen Board-Eintrag schreiben, damit die Uebergabe nachvollziehbar
   bleibt.

## Review Gate

```text
/codex:setup --enable-review-gate
/codex:setup --disable-review-gate
```

Mit aktivem Review Gate prueft Codex ueber einen `Stop`-Hook jede Claude-Antwort und blockiert das
Ende, wenn es Probleme findet. OpenAI warnt, dass daraus eine lange Claude/Codex-Schleife entstehen
kann, die Nutzungslimits schnell verbraucht.

Fuer LEANS standardmaessig **aus**. Nur einschalten, wenn die Sitzung aktiv beobachtet wird, und
danach wieder abschalten.

## Konfiguration

Das Plugin nutzt die normale Codex-Konfiguration:

- Benutzerweit: `~/.codex/config.toml`
- Projektweit: `.codex/config.toml` im Ordner, in dem Claude Code gestartet wurde. Wird nur geladen,
  wenn das Projekt in Codex als vertrauenswuerdig markiert ist.

Beispiel fuer ein festes Modell:

```toml
model = "gpt-5.4-mini"
model_reasoning_effort = "high"
```

Ohne Konfiguration und ohne `--model`/`--effort` waehlt Codex seine eigenen Standardwerte.

## Sicherheit

- Das Plugin registriert Hooks fuer `SessionStart`, `SessionEnd` und `Stop`. Der `Stop`-Hook
  beendet sich sofort, solange das Review Gate aus ist. Hooks laufen mit den Rechten des lokalen
  Benutzers.
- Lizenz des Plugins: Apache 2.0.
- `/codex:transfer` uebertraegt den Claude-Sitzungsverlauf aus `~/.claude/projects` an Codex.
  Keine Sitzungen mit Zugangsdaten oder vertraulichen Daten transferieren.
- `/codex:rescue` kann Dateien aendern. Vor dem Commit den Diff pruefen.

## Quellen

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)
- [Codex auf Windows](https://developers.openai.com/codex/windows)
- [Codex-Preise und Nutzungslimits](https://developers.openai.com/codex/pricing)
