# Erzeugung der Villa-Rechnungen (reproduzierbar)

- `data.py`: alle Positionen und Vorrechnungen, abgeschrieben aus den Original-PDFs. `python3 data.py` prüft die Summen.
- `payments.py`: Zahlungsstatus laut Kontoauszug-Abgleich.
- `check2.py`: zweite Prüfung von `data.py` gegen die Original-PDFs (erwartet sie in `./orig/`).
- `make_invoice_leans.py`: Schlussrechnung nur Fußbodenheizung (20.000 € brutto abzgl. 3.000 € = 17.000 € brutto) im LEANS-Layout, dazu Kopf und Fußzeile für alle Rechnungen. Nummer, Datum, Wasserzeichen und Leistungszeitraum sind oben im Skript gesetzt (Platzhalter für Entwürfe).
- `make_invoice_leans_kumuliert.py`: kumulierte Schlussrechnung über alle Villa-Leistungen (Heizung pauschal 20.000 € brutto, abzgl. 3.000 €) mit Zahlungsaufstellung.
- `make_final.py`: erzeugt die **endgültigen** Schlussrechnungen 2026-44 (Villa) und 2026-45 (Neubau) vom 19.10.2026, fällig 29.10.2026, ohne Wasserzeichen.
- `data_neubau.py` / `make_invoice_neubau.py`: kumulierte Schlussrechnung Neubau 19 a + b (beide Häuser zusammen) mit Zahlungsaufstellung. `python3 data_neubau.py` gleicht jede Zahlung mit dem Kontoauszug ab.
- `make_fue.py`: Fachunternehmererklärungen Villa (2) und Neubau (4), Datum/Unterschrift frei.
- `make_erklaerungen.py`: Unternehmererklärung nach § 96 GEG und Fachbauleitererklärung TGA je BV (Layout aus `make_fue.py`).
- `make_mappen.py`: zwei getrennte Mappen (Villa, Neubau) mit Abrechnung nach Gewerken, Schlussrechnung, Originalen, Freistellungsbescheinigung, Erklärungen und Datenblättern; Deckblatt mit anklickbarem Inhaltsverzeichnis und Lesezeichen. Braucht die Freistellungsbescheinigung lokal im Projektordner (nicht im Repo, siehe README).
- `make_pdf.py` / `make_pdf_fbh.py`: ältere Fassungen mit 12 % Rabatt.
- `make_xlsx.py`, `make_mappe.py`, `make_uebersicht.py`: Excel-Aufstellung, Rechnungsmappe, Übersicht Villa + Neubau.

```bash
pip install reportlab openpyxl pymupdf
cd erstellung
python3 make_final.py            # 2026-44 und 2026-45 (endgültig)
# Entwürfe und Alternativen (mit Wasserzeichen und Platzhaltern):
E="../Villa_0200/2_Schlussrechnung/Entwuerfe_und_Alternativen"
python3 make_invoice_leans_kumuliert.py "$E/Schlussrechnung_kumuliert_alle_Villa-Leistungen_17.000_brutto_ENTWURF.pdf"
python3 make_invoice_leans.py "$E/Schlussrechnung_Fussbodenheizung_17.000_brutto_ENTWURF.pdf"
python3 make_pdf.py "$E/Alternative_kumuliert_mit_12-Prozent-Rabatt_ENTWURF.pdf"
python3 make_pdf_fbh.py "$E/Alternative_19.212,26_netto_mit_12-Prozent-Rabatt_ENTWURF.pdf"
python3 make_invoice_neubau.py "../Neubau_19ab_1150/5_Schlussrechnung/Entwuerfe/Schlussrechnung_kumuliert_Neubau_19ab_45.745,31_ENTWURF.pdf"
python3 make_uebersicht.py ../00_Uebersicht_Liesborner_Weg_19_Villa_und_Neubau.pdf
python3 make_fue.py ..
python3 make_erklaerungen.py ..
python3 make_mappen.py   # zuletzt
```
