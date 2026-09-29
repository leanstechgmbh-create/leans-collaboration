"""Schlussrechnung Fußbodenheizung Villa im LEANS-Rechnungslayout (wie RE 2025-17 / Dok. 176).
Pauschalierung auf 20.000,00 € netto über eine Nachlassposition."""
import sys
from decimal import Decimal as D
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from data import HEIZUNG, VAT, r2, line_total

LIB = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("L", LIB + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LB", LIB + "LiberationSans-Bold.ttf"))
GREEN = colors.HexColor("#4CAF50"); HEAD = colors.HexColor("#DCEFDD"); GREY = colors.HexColor("#333333")
LOGO = "logo_leans.png"

ZIEL_NETTO = D("20000.00")
META = dict(nr="2026-___", datum="__.__.2026", ziel="10 Tage", faellig="__.__.2026")
EMPF = ["CREST Living GmbH & Co. KG", "Liesborner Weg 19", "13507 Berlin"]
WATERMARK = True
# FBH OG/UG fertig 04.11.2023 (Protokoll 02.11.2023), Rest EG ab 13.12.2023 (Protokoll 11.12.2023),
# hydraulischer Abgleich 03.12.2024 (Dok. 159). Sanitär 07.01.2024 liegt dazwischen.
LEISTUNGSZEITRAUM = "11.2023 – 03.12.2024"

def eur(x):
    return f"{D(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"
def num(x):
    return f"{D(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

P = ParagraphStyle("p", fontName="L", fontSize=8.5, leading=11, textColor=GREY)
PB = ParagraphStyle("pb", parent=P, fontName="LB")

def page(c, doc):
    W, H = A4
    c.saveState()
    if WATERMARK:
        c.setFont("LB", 60); c.setFillColor(colors.Color(0.8, 0.1, 0.1, alpha=0.08))
        c.translate(W/2, H/2 - 40); c.rotate(35); c.drawCentredString(0, 0, "ENTWURF"); c.restoreState(); c.saveState()
    c.setFillColor(GREY)
    if doc.page == 1:
        c.setFont("LB", 8.5); c.drawString(20*mm, H - 20*mm, "LEANS Tech GmbH")
        c.setFont("L", 8); c.drawString(20*mm, H - 24*mm, "Semir Redzic"); c.drawString(20*mm, H - 28*mm, "Berlepschstr. 165 • 14165 • Berlin")
        c.drawImage(LOGO, 115*mm, H - 37.5*mm, width=36*mm, height=25*mm, mask="auto", preserveAspectRatio=True)
        y = H - 47*mm
        for lab, val in (("Rechnungsnummer:", META["nr"]), ("Rechnungsdatum:", META["datum"]),
                         ("Zahlungsbedingungen:", META["ziel"]), ("Fälligkeitsdatum:", META["faellig"])):
            c.setFont("LB", 8.5); c.drawString(113*mm, y, lab)
            c.setFont("L", 8.5); c.setFillColor(colors.HexColor("#B00000") if "_" in val else GREY)
            c.drawString(160*mm, y, val); c.setFillColor(GREY); y -= 6*mm
        c.setFont("LB", 8.5); y = H - 70*mm
        for line in EMPF: c.drawString(20*mm, y, line); y -= 4.2*mm
    # Fußzeile wie im Original
    c.setStrokeColor(GREEN); c.setLineWidth(0.6); c.line(20*mm, 30*mm, W - 20*mm, 30*mm)
    rows = [[("Adresse", "Berlepschstr. 165 • 14165 • Berlin"), ("HR-Nr", "HRB 249080 B"), ("USt-IdNr.", "DE357948720")],
            [("E-Mail", "info@leanstech-gmbh.de"), ("Tel.", "+491708280836"), ("Website", "www.leanstech-gmbh.de")],
            [("Bank", "Berliner Volksbank"), ("SWIFT/BIC", "BEVODEBB"), ("IBAN", "DE21100900002911728004")]]
    y = 25*mm
    for row in rows:
        parts = [(k, v) for k, v in row]
        width = sum(c.stringWidth(k + " ", "LB", 7.5) + c.stringWidth(v, "L", 7.5) for k, v in parts) + 8*mm*(len(parts)-1)
        x = (W - width) / 2
        for k, v in parts:
            c.setFont("LB", 7.5); c.drawString(x, y, k + " "); x += c.stringWidth(k + " ", "LB", 7.5)
            c.setFont("L", 7.5); c.drawString(x, y, v); x += c.stringWidth(v, "L", 7.5) + 8*mm
        y -= 4*mm
    c.setFont("L", 7.5); c.drawCentredString(W/2, 10*mm, f"{doc.page}")
    c.restoreState()

def build(path):
    fbh = [h for h in HEIZUNG if h[5] == "Dok. 176"]
    abgl = [h for h in HEIZUNG if h[5] == "Dok. 159"]
    items = abgl + fbh
    netto_liste = sum(line_total(q, ep) for _, _, q, _, ep, _ in items)
    brutto_liste = sum(r2(line_total(q, ep) * (1 + VAT)) for _, _, q, _, ep, _ in items)
    nachlass_netto = netto_liste - ZIEL_NETTO
    ust = r2(ZIEL_NETTO * VAT); brutto = ZIEL_NETTO + ust
    nachlass_brutto = brutto_liste - brutto

    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=90*mm, bottomMargin=34*mm,
                          title="Schlussrechnung Fußbodenheizung – BV Liesborner Weg 19 (Villa)", author="LEANS Tech GmbH")
    later = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 54*mm, id="later")
    first = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 124*mm, id="first")
    doc.addPageTemplates([PageTemplate(id="p1", frames=[first], onPage=page, autoNextPageTemplate="pn"),
                          PageTemplate(id="pn", frames=[later], onPage=page)])
    E = [Paragraph("<font color='#4CAF50' size='14'><b>SCHLUSSRECHNUNG</b></font>", ParagraphStyle("t", fontName="LB", fontSize=14, leading=18)),
         Spacer(1, 3*mm),
         Paragraph("BV: Liesborner Weg 19<br/>13507 Berlin (Villa)<br/>Gewerk: Fußbodenheizung und hydraulischer Abgleich<br/>"
                   f"Leistungszeitraum: {LEISTUNGSZEITRAUM}", P),
         Spacer(1, 4*mm)]
    data = [["Nr.", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "USt. %", "USt.", "Betrag"]]
    for i, (p, t, q, u, ep, _) in enumerate(items, 1):
        n = line_total(q, ep); v = r2(n * VAT)
        data.append([str(i), Paragraph(f"{p} {t}", P), num(q), u, eur(ep), "19,00 %", eur(v), eur(n + v)])
    k = len(data)
    data += [["", Paragraph("Zwischensumme (brutto)", P), "", "", "", "", "", eur(brutto_liste)],
             ["", Paragraph(f"Nachlass (Pauschalierung der Schlusssumme auf {eur(ZIEL_NETTO)} netto; netto {eur(nachlass_netto)})", P), "", "", "", "", "", "-" + eur(nachlass_brutto)],
             ["", Paragraph("<b>Nettobetrag</b>", P), "", "", "", "", "", eur(ZIEL_NETTO)],
             ["", Paragraph("USt. 19,00 %", P), "", "", "", "", "", eur(ust)],
             ["", Paragraph("<b>Gesamtsumme</b>", P), "", "", "", "", "", eur(brutto)],
             ["", Paragraph("abzgl. bereits geleistete Zahlungen", P), "", "", "", "", "", eur(0)],
             ["", Paragraph("<b>Zahlbetrag</b>", P), "", "", "", "", "", eur(brutto)]]
    t = Table(data, colWidths=[7*mm, 66*mm, 13*mm, 12*mm, 19*mm, 13*mm, 18*mm, 22*mm], repeatRows=1)
    st = [("FONT", (0, 0), (-1, -1), "L", 8), ("TEXTCOLOR", (0, 0), (-1, -1), GREY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("FONT", (0, 0), (-1, 0), "LB", 8), ("BACKGROUND", (0, 0), (-1, 0), HEAD),
          ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
          ("ALIGN", (2, 0), (-1, -1), "RIGHT"), ("ALIGN", (3, 0), (3, -1), "CENTER"),
          ("LINEABOVE", (0, k), (-1, k), 0.5, GREY), ("LINEABOVE", (0, k+2), (-1, k+2), 0.5, GREY),
          ("LINEABOVE", (0, k+4), (-1, k+4), 0.5, GREY), ("LINEABOVE", (0, k+6), (-1, k+6), 0.8, GREY),
          ("FONT", (7, k+2), (7, k+2), "LB", 8), ("FONT", (7, k+4), (7, k+4), "LB", 8), ("FONT", (7, k+6), (7, k+6), "LB", 8.5)]
    for r in range(k, len(data)): st.append(("SPAN", (1, r), (6, r)))
    t.setStyle(TableStyle(st)); E.append(t)
    E.append(Spacer(1, 4*mm))
    E.append(KeepTogether([
        Paragraph("Diese Schlussrechnung ersetzt die Dokumente Nr. 176 vom 05.01.2025 (Fußbodenheizung) und Nr. 159 vom 03.12.2024 "
                  "(hydraulischer Abgleich). Auf beide Dokumente sind bislang keine Zahlungen eingegangen.", P),
        Spacer(1, 2*mm),
        Paragraph(f"Bitte überweisen Sie den Betrag von <b>{eur(brutto)}</b> bis zum Fälligkeitsdatum ohne Abzug unter Angabe der "
                  "Rechnungsnummer auf das unten genannte Konto.", P)
        ]))
    doc.build(E)
    return dict(netto_liste=netto_liste, brutto_liste=brutto_liste, nachlass_netto=nachlass_netto,
                nachlass_brutto=nachlass_brutto, netto=ZIEL_NETTO, ust=ust, brutto=brutto)

if __name__ == "__main__":
    print(build(sys.argv[1]))
