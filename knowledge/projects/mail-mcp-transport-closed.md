# Mail-MCP `mail_leanstech`: „Transport closed“ diagnostizieren

Stand: 27.09.2026. Anlass ist der Board-Eintrag „AN CLAUDE: OFFEN — Mail-MCP mail_leanstech wieder verfügbar machen“.

Ausgangslage laut Codex:
- `list_accounts` und `search_mail` liefern `Transport closed`.
- Der Server wird mit `C:\Python314\python.exe C:\Users\semir\Documents\MailManager\mail_mcp.py` gestartet, das Start-Timeout beträgt 60 s.
- Ein Pythonprozess mit diesem Befehl läuft (PID 43432).
- Zusätzlich läuft ein HTTP-Prozess auf Port 8787 (PID 31640).

## Was „Transport closed“ bedeutet

- Codex spricht mit einem stdio-MCP-Server über stdin/stdout des Prozesses, den **die aktuelle Codex-Sitzung selbst gestartet hat**. `Transport closed` heißt: Diese Verbindung ist zu. Entweder ist der Prozess beendet, oder er hat stdout geschlossen, oder der Client hat die Verbindung verworfen.
- Ist die Verbindung einmal zu, scheitern **alle** Tools dieses Servers, bis Codex ihn neu startet. Dass `list_accounts` und `search_mail` beide scheitern, beweist also nicht, dass beide Tools defekt sind.
- Der laufende Prozess PID 43432 beweist ebenfalls nichts. Er kann eine ältere oder verwaiste Instanz sein, mit der die aktuelle Sitzung gar nicht verbunden ist. Entscheidend ist sein Elternprozess (Schritt 1).

## Werkzeug

`scripts/mcp_stdio_probe.py` nutzt nur die Standardbibliothek. Deshalb läuft es mit demselben Interpreter wie der Server. Die Probe startet den Server genau so, wie er in der Codex-`config.toml` steht, und führt dann `initialize` → `notifications/initialized` → `tools/list` aus. Optional folgt ein lesender Tool-Aufruf. Am Ende meldet sie den ersten Absturz, das Timeout oder den Protokollfehler, jeweils mit den letzten stderr-Zeilen. Zugangsdaten sind darin maskiert.

Bezug, solange der Branch nicht gemergt ist:

```powershell
git clone --branch claude/clever-albattani-cat3a8 https://github.com/leanstechgmbh-create/leans-collaboration.git C:\Users\semir\Documents\LEANS-Probe
cd C:\Users\semir\Documents\LEANS-Probe
```

Nach dem Merge genügt `git -C C:\Users\semir\Documents\LEANS-Live pull --ff-only`.

## Schritt 1: Prozesse zuordnen (nur lesend)

```powershell
Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
  Where-Object CommandLine -match 'mail_mcp' |
  Select-Object ProcessId, ParentProcessId, CreationDate, CommandLine | Format-List
Get-CimInstance Win32_Process -Filter "ProcessId = <ParentProcessId aus der Ausgabe>" | Select-Object Name, CommandLine
Get-NetTCPConnection -LocalPort 8787 -State Listen | Select-Object OwningProcess
Get-CimInstance Win32_Process -Filter "ProcessId = 31640" | Select-Object Name, ParentProcessId, CreationDate, CommandLine
```

Existiert der Elternprozess von 43432 nicht mehr oder ist er keine laufende Codex-Instanz, dann ist 43432 verwaist und nicht die Verbindung der aktuellen Sitzung. Prüfe Kommandozeilen vor dem Teilen auf Zugangsdaten.

## Schritt 2: Handshake mit der echten Konfiguration

```powershell
C:\Python314\python.exe scripts\mcp_stdio_probe.py --codex-server mail_leanstech --show-schemas
```

Ohne `--call` ruft die Probe kein Tool auf. Die Konfiguration liest sie aus `%CODEX_HOME%\config.toml`, sonst aus `%USERPROFILE%\.codex\config.toml`. Mit `--codex-config` lässt sich ein anderer Pfad angeben. Werte aus `env` zeigt sie nie an, nur deren Namen.

## Schritt 3: Live-Verifikation (nur lesend)

```powershell
C:\Python314\python.exe scripts\mcp_stdio_probe.py --codex-server mail_leanstech --call list_accounts
C:\Python314\python.exe scripts\mcp_stdio_probe.py --codex-server mail_leanstech --call search_mail --arg query=Herrmann --arg limit=1
```

Übernimm die Parameternamen aus der `--show-schemas`-Ausgabe von Schritt 2. `query` und `limit` sind nur Beispiele. Werte werden als JSON gelesen, sonst als Text (`--arg folder="S Klima"`). Tools mit Namensteilen wie `move`, `send`, `delete`, `sort`, `mark` oder `update` verweigert die Probe grundsätzlich.

## Schritt 4: Umgebungsunterschiede ausschließen

| Aufruf zusätzlich mit | Scheitert nur so → Ursache | Behebung |
|---|---|---|
| `--cwd $env:TEMP` | Server nutzt relative Pfade | Pfade über `Path(__file__).resolve().parent` bilden oder `cwd` im Config-Eintrag setzen |
| `--clean-env` | Server braucht eine Variable, die nur in der eigenen Shell gesetzt ist | Nicht geheime Variable in `[mcp_servers.mail_leanstech].env` eintragen, Zugangsdaten nie in `config.toml` |
| `--env PYTHONUTF8=1` | Behebt den Fehler → Encoding-Problem | `env = { PYTHONUTF8 = "1" }` dauerhaft im Config-Eintrag |

## Befund → Ursache → Behebung

| Befund der Probe | Typische Ursache | Behebung |
|---|---|---|
| `SPAWN_FAILED` | Pfad zu `python.exe` oder `mail_mcp.py` falsch | Pfad in `config.toml` korrigieren |
| `SERVER_EXITED` bei `initialize` + `No module named 'mcp.server.fastmcp'` | `mcp`-SDK auf 2.x aktualisiert; `FastMCP` heißt dort `MCPServer` (`mcp.server.mcpserver`) | Sofort: `C:\Python314\python.exe -m pip install "mcp<2"`. Dauerhaft: Import auf 2.x migrieren |
| `SERVER_EXITED` + anderes `No module named ...` | Paket ist für einen anderen Interpreter installiert als `C:\Python314` | `C:\Python314\python.exe -m pip install <paket>` |
| `SERVER_EXITED` + `WinError 10048` / „address already in use“ | Neue Instanz will Port 8787 binden, den PID 31640 hält | HTTP-Teil vom stdio-Server trennen oder die alte Instanz nach Schritt 1 gezielt beenden |
| `SERVER_EXITED` + `UnicodeEncodeError` oder `INVALID_UTF8` | stdout-Pipe läuft unter Windows in cp1252; Umlaute/Emoji in Betreffzeilen | `PYTHONUTF8=1` im Config-Eintrag bzw. `sys.stdout.reconfigure(encoding="utf-8")` |
| `SERVER_EXITED` während `tools/call` | Unbehandelte Exception im Tool (Login, IMAP-Timeout …) | Exceptions im Tool-Handler abfangen und als `isError` zurückgeben, statt den Prozess zu beenden |
| `STDOUT_NOT_JSON` | `print()` auf stdout; stdout ist exklusiv für JSON-RPC | Ausgaben nach stderr (`print(..., file=sys.stderr)`, `logging`) |
| `STDOUT_CLOSED` | Server oder Kindprozess schließt stdout | stdout offen lassen |
| `TIMEOUT` bei `initialize`, `SLOW_STARTUP` | Verbindungsaufbau zu allen Postfächern vor dem Handshake | Verbindungen erst beim ersten Tool-Aufruf aufbauen; notfalls `startup_timeout_sec` erhöhen |
| `TOOL_ERROR` | Server läuft, das Tool meldet einen fachlichen Fehler | Meldung lesen; kein Transportproblem |
| `NO_EXIT_ON_STDIN_EOF` (Warnung) | Server endet nicht, wenn der Client die Pipe schließt | Erklärt verwaiste Prozesse; der Server muss bei stdin-EOF enden |
| Alles `OK`, Codex meldet weiter `Transport closed` | Die Codex-Sitzung hält noch die tote Verbindung | Codex neu starten (siehe unten) |

## Codex-Neustart: wann und wie

Codex startet stdio-MCP-Server beim Sitzungsstart. Nach einem Absturz hilft deshalb verlässlich nur eine neue Sitzung. Das gilt, sobald die Probe `OK` meldet oder ein Fix eingespielt ist.

1. Alle laufenden Codex-Sitzungen beenden.
2. Nur die `mail_mcp.py`-Prozesse aus Schritt 1 beenden, deren Elternprozess nicht mehr existiert: `Stop-Process -Id <PID>`. PID 31640 (Port 8787) nicht blind beenden, solange unklar ist, wer ihn nutzt.
3. Codex neu starten, `list_accounts` aufrufen und danach eine eng begrenzte Suche ausführen.

## Sicherheitsgrenzen der Probe

- Sie verschiebt, sendet und löscht nichts und speichert keine Daten. Den eigenen Serverprozess beendet sie am Ende wieder.
- Muster wie Passwort, Token, `Bearer …` und `LOGIN user pass` maskiert sie in stderr und in der Tool-Ausgabe. Die Maskierung arbeitet musterbasiert, deshalb vor dem Weitergeben kurz über die Ausgabe schauen.
- Exit-Code `0` = OK, `1` = Befund, `2` = Aufruf- oder Konfigurationsfehler.

## Tests

```powershell
C:\Python314\python.exe -m unittest discover -s tests
```

Ein Fake-Server deckt alle Fehlermodi ab. Zusätzlich wurde die Probe gegen echte SDK-Server geprüft: `mcp` 1.30 (`FastMCP`) und `mcp` 2.2 (`MCPServer`).
