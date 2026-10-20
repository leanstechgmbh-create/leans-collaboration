# Agentenregeln

Diese Regeln gelten fuer ChatGPT/Codex und Claude, wenn sie in diesem Projekt arbeiten.

1. Zu Beginn jeder Aufgabe `LEANS-Uebergabe.md` lesen.
2. ChatGPT/Codex prueft unter `## 📤 Für ChatGPT (von Claude)` auf `AN CHATGPT: OFFEN`.
3. Claude prueft unter `## 📥 Für Claude (von ChatGPT)` auf `AN CLAUDE: OFFEN`.
4. Eigentliche Dateien und Code immer am echten Ort im Projekt bearbeiten.
5. Nach erledigter eigener Eingangsaufgabe nur den eigenen passenden Eintrag von `OFFEN` auf `ERLEDIGT` setzen.
6. Uebergaben an den anderen Assistenten ganz oben in dessen Board-Bereich eintragen.
7. Wissen, Entscheidungen und wiederverwendbare Prompts in `knowledge/` dokumentieren.
8. Vor jeder Aenderung an gemeinsamen Projektdateien `scripts/leans-live.ps1 status` ausfuehren.
9. Vor jeder Aenderung die eigene Arbeit mit `scripts/leans-live.ps1 announce` und den betroffenen Dateipfaden ankundigen.
10. Insolvenzordner: Sagt der Nutzer „in den Insolvenzordner“ / „in den Ordner“, gehoert die Sache in den Google-Drive-Ordner „Insolvenzordner – LEANS Tech GmbH“ (ID `1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm`), dort in den Unterordner der jeweiligen Firma (Rechnungsempfaenger). Jede juristische Person separat, z. B. CREST Investment GmbH und CREST Living GmbH & Co. KG getrennt. Immer als Kopie ablegen. Details: `knowledge/decisions/2026-10-20-insolvenzordner.md` und das Dokument „00 REGELN – Insolvenzordner“ im Ordner.
11. Mails mit Anhaengen: immer ueber das Werkzeug „LEANS Versand“ (https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU) – Rechnung als PDF, alle uebrigen Unterlagen (Erklaerungen, Nachweise, Datenblaetter) als eine ZIP, kurzer Text. Ablauf Schritt fuer Schritt: `knowledge/prompts/versand-mit-anhaengen.md`. Anhaenge vor dem Senden mit `scripts/versand/pruefe_entwurf.py` bitgenau pruefen. Senden nur nach ausdruecklichem OK von Semir. Entwuerfe im IONOS-Postfach info@ nur vom PC aus (`scripts/info-entwuerfe/`).

Die detaillierte Board-Syntax steht in `LEANS-Uebergabe-ANLEITUNG.md`.
