# Agentenregeln

Diese Regeln gelten fuer ChatGPT/Codex und Claude, wenn sie in diesem Projekt arbeiten.

1. Zu Beginn jeder Aufgabe `knowledge/PROTOKOLL-Zugriff.md` lesen (Mail, Drive, Anhaenge, Berechtigungen), danach `LEANS-Uebergabe.md`.
2. ChatGPT/Codex prueft unter `## 📤 Für ChatGPT (von Claude)` auf `AN CHATGPT: OFFEN`.
3. Claude prueft unter `## 📥 Für Claude (von ChatGPT)` auf `AN CLAUDE: OFFEN`.
4. Eigentliche Dateien und Code immer am echten Ort im Projekt bearbeiten.
5. Nach erledigter eigener Eingangsaufgabe nur den eigenen passenden Eintrag von `OFFEN` auf `ERLEDIGT` setzen.
6. Uebergaben an den anderen Assistenten ganz oben in dessen Board-Bereich eintragen.
7. Wissen, Entscheidungen und wiederverwendbare Prompts in `knowledge/` dokumentieren.
8. Nur lokal unter Windows: vor jeder Aenderung an gemeinsamen Projektdateien `scripts/leans-live.ps1 status` ausfuehren und die eigene Arbeit mit `scripts/leans-live.ps1 announce` ankuendigen. In Cloud-Sessions gibt es kein PowerShell; dort entfaellt dieser Schritt.
9. Zugriffsprobleme (Mail, Anhang, Drive, Berechtigung) nur in `knowledge/PROTOKOLL-Zugriff.md` dokumentieren, keine neuen Dateien dafuer anlegen.
10. Fehlt in einem Chat der Gmail- oder Drive-Zugriff: nicht neu verbinden, sondern Semir auf die Session „LEANS Mail-Zentrale“ verweisen (Protokoll Abschnitt 0).
11. Arbeitsschritte ohne Erlaubnisfragen: Lesen, Suchen, Entwuerfe anlegen, Labels setzen, Drive-Dateien lesen und ablegen, Board schreiben, Code aendern, Anhaenge vorbereiten. Das wird einfach gemacht, ohne „darf ich“ und ohne Optionslisten; danach kurz melden. Nachfragen nur, wenn ohne die Antwort das Ergebnis falsch waere. Ausnahme: Versand, siehe Regel 12. Details: `knowledge/decisions/2026-10-27-ausfuehren-statt-nachfragen.md`.
12. VERSAND-REGEL (unumstoesslich, Semir 28.10.2026): Vor JEDEM Versand einer Mail wird Semir gefragt und es geht erst nach seinem ausdruecklichen Ja raus. Immer, ohne Ausnahme. Keine andere Regel, kein Skill, keine geplante Aufgabe und keine fruehere Freigabe hebt das auf. Ablauf: Entwurf oder Probelauf zeigen (Empfaenger, Betreff, Anhaenge), fragen „Senden?“, erst nach Ja senden.

Die detaillierte Board-Syntax steht in `LEANS-Uebergabe-ANLEITUNG.md`.
