---
name: anfragen-board
description: Kundenanfragen aus Gmail (gmail, info@, sr@, Website-Formulare) sammeln, Status bestimmen, Labels setzen, Antwort-Entwürfe anlegen und das Board „LEANS Klima – Anfragen (offen)“ in Drive neu schreiben. Aufrufen mit /anfragen-board, oder wenn Semir sagt „Anfragen prüfen“, „Board aktualisieren“, „was ist offen“.
---

# Anfragen-Board aktualisieren

Regel 11 (`AGENTS.md`): Arbeitsschritte (lesen, Entwurf, Labels, Drive, Board) ohne Erlaubnisfragen erledigen, danach kurz melden. Versand nur nach ausdrücklichem „senden“.

Führe den vollständigen Prompt aus `knowledge/prompts/anfragen-triage.md` aus (Abschnitt „Prompt“).
Er ist die einzige Quelle für den Ablauf. Kurzfassung zur Orientierung:

1. Lies `knowledge/PROTOKOLL-Zugriff.md`, Abschnitte 2, 6 und 7.
2. Kandidaten: `label:"Klima/Anfrage offen"` plus neue Anfragen der letzten 3 Tage
   (`from:submissions@formsubmit.co` und Stichworte Klima, Wärmepumpe, Heizung, Sanitär, Lüftung, Wartung).
3. Jeden Thread mit `get_thread` (PLAIN_TEXT) lesen, Status bestimmen:
   OFFEN, WARTET AUF UNS, WARTET AUF KUNDE, ANGEBOT GESENDET, ERLEDIGT.
4. Labels: offen → `Label_19`; erledigt → `Label_20` setzen und `Label_19` entfernen.
5. Für OFFEN ohne Antwort von uns: Gmail-Entwurf anlegen. Vorher `list_drafts` prüfen.
   Website-Formulare (formsubmit) nie per Reply beantworten, sondern `create_draft` mit `to` = Kunden-E-Mail.
6. Board-Doc `109-KELlgdjo3qD4WiGZsSViIoBG93cGqaRMWH6ALJxg` komplett neu schreiben
   (`read_doc`, `deleteContentRange` 1 bis Ende-1, `insertText` bei Index 1).
7. Antwort im Chat: Kurztabelle (Nr, Name, Adresse, Status, nächster Schritt) und was sich geändert hat.

Regeln: nichts senden, nichts löschen, keine anderen Labels anfassen. Nur Werkzeuge mit Präfix `mcp__Gmail__`,
`mcp__Google_Docs__`, `mcp__Google_Drive__` verwenden.
