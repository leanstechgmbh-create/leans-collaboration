# Prompt: Codex Plugin auf dem LEANS-Rechner einrichten

Uebergabe an einen neuen, LOKALEN Claude-Code-Chat auf Semirs Windows-PC (nicht Cloud).
Semir kopiert den Block unten in den neuen Chat. Hintergrund: `docs/Codex-Plugin.md`,
Entscheidung `knowledge/decisions/2026-09-29-codex-plugin-cc.md`.

```text
Übergabe: Richte das Codex Plugin für Claude Code auf diesem PC ein und teste es. Mach alles selbst, frag mich nur, wenn ich etwas tun muss, das du nicht kannst (Anmeldung im Browser, Befehl eintippen).

1. Arbeite im LEANS-Repo (leans-collaboration, Ordner C:\Users\semir\Documents\LEANS-Live). Lies AGENTS.md und docs/Codex-Plugin.md. Fehlt die Datei, hol den Branch claude/fervent-gauss-fqkf52 (PR #9).
2. Prüfe per PowerShell: node --version (mind. 18.18) und codex --version. Fehlt Codex: npm install -g @openai/codex.
3. Installiere das Plugin per PowerShell:
   claude plugin marketplace add openai/codex-plugin-cc
   claude plugin install codex@openai-codex
4. Bitte mich, /reload-plugins und danach /codex:setup einzutippen (oder ruf sie selbst auf, falls du kannst). Meldet /codex:setup, dass Codex nicht angemeldet ist: lass mich !codex login eintippen und mich mit meinem ChatGPT-Konto anmelden.
5. Test: /codex:review --background, dann /codex:status und /codex:result. Läuft das Review durch, ist die Verbindung fertig.
6. Trag das Ergebnis mit Datum in docs/Codex-Plugin.md ein (Abschnitt „Einmalig einrichten“, Satz zum Windows-Test ersetzen): was lief, welche Fehler, wie behoben. Committen und pushen wie im Repo üblich.
7. Melde mir am Ende in zwei Sätzen: läuft es ja/nein, und was noch fehlt.

Nichts per Mail versenden.
```
