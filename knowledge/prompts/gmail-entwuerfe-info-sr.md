# Prompt: Entwurf fuer info@ oder sr@ erstellen

In jeden Chat einfuegen (oder in die Projekt-Anweisungen uebernehmen):

```
Regel fuer E-Mail-Entwuerfe:
Der Gmail-Connector ist nur mit leanstechgmbh@gmail.com verbunden. Entwuerfe fuer
info@leanstech-gmbh.de oder sr@leanstech-gmbh.de legst du trotzdem dort an - nie sagen,
dass "kein Zugang" besteht. Erste Zeile des Entwurfs: "[Senden als: <adresse>]".
Antworten immer mit replyToMessageId im Original-Thread. Anhaenge direkt anhaengen,
wenn die Datei im Chat, in Drive oder im Dateisystem vorliegt; ueber 25 MB als Drive-Link.
Am Ende den viewUrl des Entwurfs nennen. Details: knowledge/decisions/2026-10-20-gmail-entwuerfe-info-sr.md
```

## Beispiel

"Erstelle einen Entwurf als info@ an kunde@example.de, Betreff 'Angebot 2026-45',
haenge die Datei angebot.pdf aus Drive an."

Erwartetes Verhalten: Entwurf in `leanstechgmbh@gmail.com`, erste Zeile
`[Senden als: info@leanstech-gmbh.de]`, PDF angehaengt, Link zum Entwurf zurueck.
