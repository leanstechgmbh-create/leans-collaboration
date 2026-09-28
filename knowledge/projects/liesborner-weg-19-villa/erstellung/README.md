# Erzeugung der Schlussrechnung (reproduzierbar)

- `data.py` – alle Positionen und Vorrechnungen, abgeschrieben aus den Original-PDFs; `python3 data.py` prüft die Summen.
- `payments.py` – Zahlungsstatus laut Kontoauszug-Abgleich.
- `make_pdf.py` / `make_xlsx.py` – erzeugen PDF-Entwurf und Excel-Aufstellung.

```bash
pip install reportlab openpyxl
python3 make_pdf.py ../Schlussrechnung_kumuliert_ENTWURF_BV_Liesborner_Weg_19_Villa.pdf
python3 make_xlsx.py ../Kumulierte_Aufstellung_BV_Liesborner_Weg_19_Villa.xlsx
```
