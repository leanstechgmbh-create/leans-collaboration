"""Rechnungsmappe Villa: Deckblatt mit Übersicht + alle Original-Belege (ohne Neubau 19 a+b)."""
import sys, pymupdf as fitz
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
import make_invoice_leans as inv  # registriert Fonts L/LB

P = ParagraphStyle("p", fontName="L", fontSize=8, leading=10)
H = ParagraphStyle("h", fontName="LB", fontSize=14, leading=18, textColor=inv.GREEN)
BELEGE = [  # (Beleg, Datum, an, Gewerk, brutto, Status, Datei)
 ("RE 2024-47", "16.04.2024", "CREST Living GmbH & Co. KG", "Sanitärobjekte / Montage Armaturen", "14.852,39 €", "Zahlung nicht belegbar (Auszüge Apr.–Jul. 2024 fehlen)", "RECHNUNG 2024-47 - LEANS Tech GmbH - 14852.39 EUR.pdf"),
 ("Dok. 159", "03.12.2024", "CREST Investment GmbH", "Heizung – hydraulischer Abgleich", "321,30 €", "OFFEN – keine Rechnungsnummer", "RECHNUNG 159 - LEANS Tech GmbH - 321.3 EUR.pdf"),
 ("Dok. 176 (SR)", "05.01.2025", "CREST Investment GmbH", "Fußbodenheizung", "22.541,30 €", "OFFEN – keine Rechnungsnummer", "044_—_SCHLUSSRECHNUNG 176 - LEANS Tech GmbH - 22541.3 EUR (2).pdf"),
 ("NA 175", "05.01.2025", "CREST Living GmbH & Co. KG", "Nachtragsangebot Sanitärobjekte", "6.669,95 €", "Angebot", "NACHTRAGSANGEBOT 175 - LEANS Tech GmbH - 6669.95 EUR.pdf"),
 ("Dok. 175", "05.01.2025", "CREST Investment", "Sanitärobjekte Nachtrag", "6.669,95 €", "Vorversion von RE 2025-8", "RECHNUNG 175 - LEANS Tech GmbH - 6669.95 EUR.pdf"),
 ("RE 2025-8", "28.03.2025", "CREST Investment", "Sanitärobjekte Nachtrag", "6.669,95 €", "nicht bezahlt, ersetzt durch 2025-17 → stornieren", "RECHNUNG 2025-8 - LEANS Tech GmbH - 6669.95 EUR.pdf"),
 ("RE 2025-17", "14.04.2025", "CREST Living GmbH & Co. KG", "Sanitärobjekte Nachtrag", "5.662,02 €", "bezahlt 19.09.2025", "RECHNUNG 2025-17 - LEANS Tech GmbH - 5662.02 EUR (1).pdf"),
]

def build(out):
    cover = "mappe_cover.pdf"
    doc = SimpleDocTemplate(cover, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=18*mm, bottomMargin=15*mm)
    rows = [["Beleg", "Datum", "Adressiert an", "Gewerk", "Brutto", "Status"]] + \
           [[b[0], b[1], Paragraph(b[2], P), Paragraph(b[3], P), b[4], Paragraph(b[5], P)] for b in BELEGE]
    t = Table(rows, colWidths=[22*mm, 18*mm, 38*mm, 40*mm, 20*mm, 42*mm], repeatRows=1)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "L", 8), ("FONT", (0, 0), (-1, 0), "LB", 8),
                           ("BACKGROUND", (0, 0), (-1, 0), inv.HEAD), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("ALIGN", (4, 0), (4, -1), "RIGHT"), ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#BBBBBB"))]))
    E = [Paragraph("Rechnungsmappe BV Liesborner Weg 19 – Villa (Projekt 0200)", H), Spacer(1, 2*mm),
         Paragraph("Alle in Google Drive gefundenen LEANS-Belege zur Villa, chronologisch. Nicht enthalten: Neubau Butterfly Houses "
                   "19 a+b (Projekt 1150) und alle anderen CREST-Baustellen (z. B. Scharfenberger Str./Tegeler See). "
                   "Zahlungsstand laut Kontoauszügen 02/2024, 08–09/2024, 01/2025–04/2026. Stand 28.09.2026.", P),
         Spacer(1, 4*mm), t, Spacer(1, 4*mm),
         Paragraph("<b>Offen:</b> Dok. 176 (22.541,30 €) und Dok. 159 (321,30 €) – beide ohne Rechnungsnummer an CREST Investment. "
                   "Sie werden durch die neue Schlussrechnung Fußbodenheizung (20.000,00 € netto / 23.800,00 € brutto) an CREST Living ersetzt.", P)]
    doc.build(E)
    m = fitz.open(cover)
    for b in BELEGE:
        m.insert_pdf(fitz.open("orig/" + b[6]))
    m.set_toc([[1, "Übersicht", 1]] + [[1, f"{b[0]} – {b[1]}", 0] for b in BELEGE])  # page nums fixed below
    toc, p = [[1, "Übersicht", 1]], 2
    for b in BELEGE:
        toc.append([1, f"{b[0]} vom {b[1]} – {b[3]}", p]); p += fitz.open("orig/" + b[6]).page_count
    m.set_toc(toc); m.save(out); return m.page_count

if __name__ == "__main__":
    print("Seiten:", build(sys.argv[1]))
