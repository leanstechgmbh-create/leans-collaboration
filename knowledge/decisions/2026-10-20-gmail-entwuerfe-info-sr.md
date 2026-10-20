# Entscheidung: E-Mail-Entwuerfe mit Anhang fuer info@ und sr@ (2026-10-20)

## Problem

In claude.ai-Chats hiess es, `info@leanstech-gmbh.de` und `sr@leanstech-gmbh.de` haetten
"keinen Zugang": keine Entwuerfe, keine Anhaenge. Der Weg war laengst gebaut.

## Befund (geprueft am 2026-10-20)

### Der gebaute Weg: Mail-MCP `mail_leanstech` (Mail-Zentrale)

- Lokaler MCP-Server auf Semirs PC: `C:\Python314\python.exe C:\Users\semir\Documents\MailManager\mail_mcp.py`
  (Handshake "LeansTech Mail 1.27.2"). Kontenschluessel: `ionos_info` = info@leanstech-gmbh.de,
  `ionos_sr` = sr@leanstech-gmbh.de, dazu `gmail`, `gmx`, `webde`. Passwoerter im Windows-Tresor.
- Werkzeuge: `list_accounts`, `list_folders`, `count_folders`, `search_mail`, `read_mail`,
  **`save_draft`** (mit Anhaengen aus freigegebenen Ordnern). `send_mail`/`delete_mail` sind
  am Server bewusst nicht registriert; Versand nur nach Semirs Freigabe per
  `python "C:\Users\semir\Documents\MailManager\send_eml.py" ionos_sr "<eml>"`.
- Zugaenge: Claude Code und Codex auf dem PC per stdio. Fuer claude.ai, Handy und Cloud
  laeuft der Server ueber den Cloudflare-Tunnel `leans-mcp` unter
  `https://mcp.leanstech-klima.de/mail/mcp` (Bearer-Token, `/mail/health` = 200).
- Belege im Live-Board (Drive, `LEANS-Uebergabe.md`): Eintrag 2026-08-04 "Du hast jetzt Zugang
  zu sr@ und info@", 2026-08-09 Remote-Mail-Fix, 17.09.2026 Versand aus info@ mit 10-Seiten-PDF,
  29.09.2026 fuenf Angebots-Entwuerfe in info@, 22.09.2026 Mahnwesen (Entwurf + Anhang -> sr@).

### Warum es in den Chats "nicht geht"

- In claude.ai ist **kein Mail-Connector** installiert (Stand 2026-10-20, `ListConnectors`):
  nur Gmail (leanstechgmbh@gmail.com), Drive, Calendar, Notion, Slack, HubSpot, Higgsfield, Sjinn.
- Der Connector **"AutoCAD MCP"** steht auf `needs_reconnect`. Er ist sehr wahrscheinlich das
  LEANS-Gateway, das frueher AutoCAD + Mail gemeinsam bereitstellte (Autostart hiess
  "MCP Remote (AutoCAD + Mail).vbs"). Ebenfalls `needs_reconnect`: `gbrain`, `n8n MCP`.
- Folge: Cloud-Chats sehen nur den Gmail-Connector. Der ist per OAuth an genau ein Konto
  gebunden (`leanstechgmbh@gmail.com`), `create_draft` hat kein From-Feld. Daher die Antwort
  "kein Zugang zu info@/sr@". Anhaenge ueber Gmail funktionieren (getestet), aber eben nur im Gmail-Konto.
- Der Gateway/Tunnel auf dem PC war zwischendurch aus (Infra-Check 14.10.2026: Gateway :8100,
  Tunnel `leans-mcp`, Board-Waechter alle aus -> per `autostart.ps1` repariert). Der
  claude.ai-Connector blieb danach auf `needs_reconnect` stehen.

## Entscheidung / Regel fuer alle Chats

1. **Entwurf fuer info@ oder sr@ = Mail-MCP `mail_leanstech`, Werkzeug `save_draft`**,
   Konto `ionos_info` bzw. `ionos_sr`, Anhaenge direkt mitgeben, danach mit
   `search_mail(folder=Entwuerfe)` gegenpruefen und UID + Konto melden. Nie "kein Zugang" sagen.
2. **Wenn der Mail-MCP im Chat nicht geladen ist:** nicht aufgeben, sondern
   a) Semir bitten, in claude.ai -> Einstellungen -> Connectors den LEANS-Connector
      ("AutoCAD MCP" bzw. Mail-MCP `https://mcp.leanstech-klima.de/mail/mcp`) neu zu verbinden
      und im Chat zu aktivieren, und
   b) sofort den **Fallback** fahren: Auftragsdokument im Drive-Projektordner anlegen
      (`00 AUFTRAG - Entwuerfe in <konto> anlegen (<Projekt>)`, Format: Konto, An, Von,
      Betreff, Anhaenge mit Drive-IDs, Text) plus Board-Eintrag `AN CLAUDE: OFFEN`.
      Claude Code / Board-Waechter auf dem PC legt den Entwurf dann per `save_draft` an.
   c) Zusaetzlich darf ein Gmail-Entwurf in leanstechgmbh@gmail.com angelegt werden
      (erste Zeile `[Senden als: info@leanstech-gmbh.de]`), damit Semir sofort etwas sehen kann.
3. **Versand** nie automatisch. Nur nach Semirs ausdruecklichem "senden", danach Gegenpruefung
   in "Gesendete Objekte".

## Nachtrag 2026-10-20 abends: ngrok

Beim "Erneut verbinden" von "AutoCAD MCP" erscheint laut Semir ngrok. Der Connector zeigt
also vermutlich noch auf die alte ngrok-Adresse; ngrok ist seit 09.08.2026 aus dem Mail-Weg
entfernt (Cloudflare-Tunnel `leans-mcp`). Der Gateway :8100 liefert nur fs/git/github/obsidian,
keine Mail-Werkzeuge. Loesung: neuer claude.ai-Connector fuer den Mail-MCP ueber Cloudflare
(OAuth oder Geheimpfad "Sicherheit Stufe 2"), Umsetzung nur vom PC aus moeglich. Uebergabe an
Claude (PC)/Board-Waechter liegt in Drive, Ordner "Uebergaben":
`UEBERGABE von Claude-Cloud 2026-10-20 - OFFEN - Mail-MCP fuer claude.ai-Chats wieder anbinden (ohne ngrok).md`.

## Wichtigster Befund (2026-10-20, spaet): Remote Control auf dem PC ist weg

Die App-Chats, die info@/sr@ bedienen konnten, liefen per **Remote Control auf Semirs PC**
(Sitzungstyp "bridge", z. B. "DCO", "Luftmengenmessung Schicklerstrasse"). Seit 20.10.2026
ca. 03:10 meldet der PC `computer_unreachable`. Alle neuen App-Chats laufen seitdem in der
Cloud (`anthropic_cloud`) und sehen nur die claude.ai-Connectors, also nur Gmail.

Fix (nur auf dem PC): PowerShell oeffnen und `claude remote-control` im Arbeitsordner
starten (z. B. `C:\Users\semir\Documents\LEANS-Live`); dann in der App neue Chats auf
diesem Computer starten. Dauerhaft: `claude remote-control` in `autostart.ps1` aufnehmen.

## Monitor (gebaut 2026-10-20)

Geplante Aufgabe "LEANS Mail-Connector Monitor" (claude.ai, taeglich 07:34 Europe/Berlin,
Trigger `trig_01N2MvuSvY6efEPXJx9SsG1N`): prueft per `ListConnectors`, ob der LEANS-Connector
("AutoCAD MCP" bzw. Mail-MCP) in claude.ai auf `connected` steht, meldet Semir per Push/E-Mail
den Status und die Handlungsanweisung, und deaktiviert sich selbst, sobald der Connector
verbunden ist. Legt keine Entwuerfe an, sendet nichts. Hinweis: die Aufgabe laeuft ohne
Connector-Tools (Notion/Drive), schreibt also nicht selbst ins Board.

## Einmalige Aktion fuer Semir

claude.ai -> Einstellungen -> Connectors: "AutoCAD MCP" (und gbrain, n8n MCP) auf
"Erneut verbinden" klicken; pruefen, ob danach Mail-Werkzeuge (`save_draft`, `search_mail`)
im Chat erscheinen. Falls nicht: "Benutzerdefinierten Connector hinzufuegen" mit URL
`https://mcp.leanstech-klima.de/mail/mcp` und dem Bearer-Token vom PC (Token-Datei ist nur
fuer Semir lesbar, steht in `C:\Users\semir\.codex\AGENTS.md`, Abschnitt "Mail-Zugang").
Den Connector in jedem Projekt/Chat einschalten, in dem E-Mails bearbeitet werden.
