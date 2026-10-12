# Angebots-PDF-Generator (LEANS-Layout)

Erzeugt Angebote im Layout von Angebot 254 (Logo rechts oben, grüne Tabelle, Fußzeile mit Firmendaten).

## Nutzung

```bash
python3 scripts/angebot-pdf/angebot_pdf.py scripts/angebot-pdf/logo.png scripts/angebot-pdf/vorlagen/angebot-260-waschmaschinenanschluss.json "outputs/ANGEBOT 260 - LEANS Tech GmbH.pdf"
```

Benötigt: Python 3, `reportlab`, Schrift Liberation Sans (`/usr/share/fonts/truetype/liberation/`). Unter Windows den Font-Pfad im Skript auf Arial anpassen.

## JSON-Felder

- `nummer`, `datum`, `gueltig`: Kopfdaten als Text.
- `empfaenger`: Zeilen des Adressblocks.
- `kopf`: Zeilen unter "ANGEBOT" (BV, Gewerk, Kurzbeschreibung).
- `positionen`: Liste mit `text`, `menge`, `einheit`, `ep` (Einzelpreis netto). USt. 19 % und Summen werden berechnet.
- `hinweise`: optionale Aufzählung unter den Summen.

Fertige PDFs gehören nach `outputs/` (gitignored), nicht ins Repo.
