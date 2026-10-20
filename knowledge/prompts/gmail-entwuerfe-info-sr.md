# Prompt: Entwurf fuer info@ oder sr@ erstellen (alle Chats)

In Projekt-Anweisungen / jeden Chat einfuegen:

```
Regel fuer E-Mail-Entwuerfe (info@leanstech-gmbh.de, sr@leanstech-gmbh.de):
Entwuerfe in diesen Postfaechern legst du mit dem Mail-MCP "mail_leanstech" an:
save_draft mit account=ionos_info bzw. ionos_sr, Anhaenge direkt mitgeben, danach mit
search_mail im Ordner Entwuerfe gegenpruefen und Konto + UID nennen. Nie sagen, dass
"kein Zugang" besteht.
Ist der Mail-MCP in diesem Chat nicht geladen: (1) Semir bitten, den LEANS-Connector
(AutoCAD MCP / https://mcp.leanstech-klima.de/mail/mcp) in claude.ai neu zu verbinden und
hier zu aktivieren; (2) sofort ein Auftragsdokument "00 AUFTRAG - Entwuerfe in <konto>
anlegen (<Projekt>)" im Drive-Projektordner anlegen (Konto, An, Von, Betreff, Anhaenge mit
Drive-IDs, Text) und einen Board-Eintrag "AN CLAUDE: OFFEN" schreiben, damit Claude auf dem
PC den Entwurf anlegt; (3) optional einen Gmail-Entwurf in leanstechgmbh@gmail.com mit erster
Zeile "[Senden als: <adresse>]" anlegen.
Nie senden ohne Semirs ausdrueckliches "senden".
Details: knowledge/decisions/2026-10-20-gmail-entwuerfe-info-sr.md
```

## Beispiel

"Erstelle einen Entwurf als info@ an kunde@example.de, Betreff 'Angebot 2026-45',
haenge angebot.pdf an."

Erwartet: `save_draft(account="ionos_info", to=..., subject=..., body=..., attachments=[...])`,
Gegenpruefung per `search_mail(account="ionos_info", folder="Entwuerfe", subject="Angebot 2026-45")`,
Antwort: "Entwurf liegt in info@ (UID ...), nicht gesendet."
