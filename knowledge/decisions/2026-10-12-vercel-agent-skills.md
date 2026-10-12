# Entscheidung: Vercel Labs Agent Skills im Projekt

- Datum: 2026-10-12
- Von: Claude
- Quelle: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), Commit `063bee9`
- Installiert mit: `npx skills@1.7.2 add vercel-labs/agent-skills --skill '*' -a claude-code -a codex --copy -y`

## Entscheidung

Alle 9 Skills liegen projektlokal im Repo, damit Claude und ChatGPT/Codex dieselben Regeln nutzen:

- `.claude/skills/` - Claude Code
- `.agents/skills/` - Codex (und weitere Agenten mit `.agents/skills`)
- `skills-lock.json` - Quelle und Hash je Skill, Grundlage fuer `npx skills update`

`--copy` statt Symlinks, weil Git unter Windows Symlinks standardmaessig als Textdateien auscheckt. Beide Ordner sind deshalb identische Kopien. `.gitattributes` erzwingt LF fuer `*.sh`, sonst brechen die Deploy-Skripte unter Git Bash.

## Skills

| Skill | Zweck |
| --- | --- |
| `vercel-react-best-practices` | React/Next.js Performance-Regeln (Waterfalls, Bundle, Re-Renders) |
| `vercel-composition-patterns` | Komponenten-APIs ohne Boolean-Prop-Wildwuchs |
| `vercel-react-view-transitions` | View Transition API in React/Next.js |
| `vercel-react-native-skills` | React Native/Expo Best Practices |
| `web-design-guidelines` | UI-Review: Barrierefreiheit, UX, Performance |
| `writing-guidelines` | Doku-/Text-Review nach Vercel Writing Handbook |
| `vercel-optimize` | Kosten-/Performance-Audit eines Vercel-Projekts |
| `vercel-cli-with-tokens` | Vercel CLI mit Token statt interaktivem Login |
| `deploy-to-vercel` | Deployment auf Vercel, auch als "claimable" Deployment |

## Sicherheitspruefung (2026-10-12)

- Keine versteckten Unicode-Steuerzeichen, keine Prompt-Injection-Muster gefunden.
- `vercel-optimize` startet Prozesse nur per `execFile` (`vercel`, `rg`), ohne Shell.
- `web-design-guidelines` laedt die Regeln bei jeder Nutzung live von `raw.githubusercontent.com/vercel-labs/web-interface-guidelines`. Der Inhalt kann sich also ohne Commit hier aendern.
- `deploy-to-vercel` laedt ohne Vercel-Login das ganze Projektverzeichnis (ohne `node_modules`, `.git`, `.env`, `.env.*`) an `claude-skills-deploy.vercel.com` bzw. `codex-deploy-skills.vercel.sh` hoch und erzeugt eine oeffentliche Preview-URL. Nur bewusst und nur fuer Ordner ohne vertrauliche Inhalte nutzen, nie fuer dieses Kollaborations-Repo.
- `deploy-to-vercel/Archive.zip` ist eine veraltete Kopie des Skills aus dem Upstream-Repo. Bleibt unveraendert, damit die Kopie dem Upstream entspricht.

## Pflege

```bash
npx skills ls                       # installierte Skills anzeigen
npx skills update -p -y             # auf neuesten Upstream-Stand bringen
npx skills remove <skill> -a '*' -y # einzelnen Skill entfernen
```

Nach einem Update den Diff pruefen, bevor er committet wird. Skills laufen mit vollen Agentenrechten.
