# Erzeugung der Villa-Rechnungen (reproduzierbar)

- `data.py`: alle Positionen und Vorrechnungen, abgeschrieben aus den Original-PDFs. `python3 data.py` prüft die Summen.
- `payments.py`: Zahlungsstatus laut Kontoauszug-Abgleich.
- `check2.py`: zweite Prüfung von `data.py` gegen die Original-PDFs (erwartet sie in `./orig/`).
- `make_invoice_leans.py`: Schlussrechnung Fußbodenheizung, 20.000 € netto, im LEANS-Layout. Nummer, Datum, Wasserzeichen und Leistungszeitraum sind oben im Skript gesetzt.
- `make_invoice_leans_kumuliert.py`: kumulierte Schlussrechnung über alle Villa-Leistungen im LEANS-Layout (Heizung pauschal 20.000 € netto). Nutzt Kopf und Fußzeile aus `make_invoice_leans.py`.
- `data_neubau.py` / `make_invoice_neubau.py`: kumulierte Schlussrechnung Neubau 19 a + b (beide Häuser zusammen) mit Zahlungsaufstellung. `python3 data_neubau.py` gleicht jede Zahlung mit dem Kontoauszug ab.
- `make_fue.py`: Fachunternehmererklärungen Villa (2) und Neubau (4), Datum/Unterschrift frei.
- `make_gesamtmappe.py`: Gesamtmappe mit Deckblatt, anklickbarem Inhaltsverzeichnis und Lesezeichen.
- `make_pdf.py` / `make_pdf_fbh.py`: ältere Fassungen mit 12 % Rabatt.
- `make_xlsx.py`, `make_mappe.py`, `make_uebersicht.py`: Excel-Aufstellung, Rechnungsmappe, Übersicht Villa + Neubau.

```bash
pip install reportlab openpyxl pymupdf
cd erstellung
python3 make_invoice_leans_kumuliert.py "../Villa_0200/2_Schlussrechnung/Schlussrechnung_kumuliert_alle_Villa-Leistungen_17.000_brutto_ENTWURF.pdf"
python3 make_invoice_leans.py "../Villa_0200/2_Schlussrechnung/Schlussrechnung_Fussbodenheizung_17.000_brutto_ENTWURF.pdf"
python3 make_pdf.py "../Villa_0200/2_Schlussrechnung/Alternative_kumuliert_mit_12-Prozent-Rabatt_ENTWURF.pdf"
python3 make_pdf_fbh.py "../Villa_0200/2_Schlussrechnung/Alternative_19.212,26_netto_mit_12-Prozent-Rabatt_ENTWURF.pdf"
python3 make_invoice_neubau.py "../Neubau_19ab_1150/5_Schlussrechnung/Schlussrechnung_kumuliert_Neubau_19ab_45.745,31_ENTWURF.pdf"
python3 make_uebersicht.py ../00_Uebersicht_Liesborner_Weg_19_Villa_und_Neubau.pdf
python3 make_fue.py ..
python3 make_gesamtmappe.py ../00_Gesamtmappe_Liesborner_Weg_19_Villa_und_Neubau.pdf   # zuletzt
```
