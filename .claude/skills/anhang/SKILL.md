---
name: anhang
description: Einen Mail-Anhang lesen oder weiterverarbeiten (PDF, Bild, Rechnung), obwohl Gmail den Inhalt nicht liefert. Aufrufen mit /anhang <Mail oder Datei>, oder wenn Semir sagt „lies den Anhang“, „was steht in der PDF“, „die Datei aus der Mail“.
---

# Anhang lesen

Regel 11 (`AGENTS.md`): Eine klare Anweisung von Semir wird sofort ausgeführt, ohne Rückfrage. Erst machen, dann in einem Satz melden.

Das Gmail-Werkzeug liefert nur Dateiname, Typ und ID eines Anhangs, nie den Inhalt. Der Weg, der geht:

1. Mail finden und Anhangsnamen zeigen: `mcp__Gmail__get_message` mit `PLAIN_TEXT`, Feld `attachments`.
2. In Drive suchen, ob die Datei schon da ist: `mcp__Google_Drive__search_files` mit
   `title contains '<Dateiname ohne Endung>'` oder `parentId = '<Ordner-ID>'`.
3. Gefunden: `mcp__Google_Drive__read_file_content` (PDF, Word, Excel, Google Docs/Sheets, PNG, JPEG).
4. Nicht gefunden: Semir in einem Satz bitten, in Gmail am Anhang „In Drive speichern“ zu klicken
   (Zielordner nennen, z. B. Firmenordner im Insolvenzordner `1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm`
   oder „LEANS Klima“ `1yrVbxZnRy7p4_yzYUt4EKZXXjJZU1VAB`), oder die Datei direkt in den Chat hochzuladen.
   Danach Schritt 2 wiederholen.
5. Ablage nach Regel „00 REGELN – Insolvenzordner“: Kopie, Dateiname
   „JJJJ-MM-TT Rechnung <Nr> – <Firma> – <Betrag> EUR – <Kurzinfo>.pdf“, ein Ordner je juristische Person.

Nie raten, was in einem Anhang steht. Wenn der Inhalt nicht lesbar ist, das sagen und den Weg oben anbieten.
