# -*- coding: utf-8 -*-
"""Erzeugt LEANS-Angebote im Layout von Angebot 254 (reportlab)."""
import sys, json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

LOGO = sys.argv[1]; SPEC = json.load(open(sys.argv[2], encoding="utf-8")); OUT = sys.argv[3]

pdfmetrics.registerFont(TTFont("LS", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LS-B", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
GREEN = colors.HexColor("#5BAE5B"); LIGHT = colors.HexColor("#E6F2E0"); GREY = colors.HexColor("#444444")

def eur(x): return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"
def num(x): return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

W, H = A4; ML, MR = 18*mm, 18*mm
st = ParagraphStyle("n", fontName="LS", fontSize=8.6, leading=11.5, textColor=colors.black)
stb = ParagraphStyle("b", parent=st, fontName="LS-B")
sth = ParagraphStyle("h", parent=st, fontName="LS-B", fontSize=9, textColor=colors.white)
stt = ParagraphStyle("t", parent=st, fontName="LS-B", fontSize=14, textColor=GREEN, leading=18)
str_ = ParagraphStyle("r", parent=st, alignment=TA_RIGHT)
stbr = ParagraphStyle("br", parent=stb, alignment=TA_RIGHT)

def header_footer(c, doc):
    c.saveState()
    c.drawImage(LOGO, W - MR - 42*mm, H - 16*mm - 29*mm, width=42*mm, height=29*mm, mask="auto")
    if doc.page == 1:
        y = H - 42*mm
        c.setFont("LS-B", 9); c.drawString(ML, y, "LEANS Tech GmbH")
        c.setFont("LS", 8.6); c.drawString(ML, y - 4.2*mm, "Semir Redzic")
        c.drawString(ML, y - 8.4*mm, "Berlepschstr. 165 • 14165 • Berlin")
        yr = H - 55*mm; xl = W - MR - 75*mm; xv = W - MR - 30*mm
        for i, (k, v) in enumerate([("Angebotsnummer:", SPEC["nummer"]), ("Angebotsdatum:", SPEC["datum"]), ("Gültig bis:", SPEC["gueltig"])]):
            c.setFont("LS-B", 8.6); c.drawString(xl, yr - i*5.5*mm, k)
            c.setFont("LS", 8.6); c.drawString(xv, yr - i*5.5*mm, v)
        y2 = H - 70*mm
        c.setFont("LS-B", 9)
        for i, line in enumerate(SPEC["empfaenger"]):
            c.drawString(ML, y2 - i*4.6*mm, line)
    else:
        c.setFillColor(GREEN); c.setFont("LS-B", 14); c.drawString(ML, H - 20*mm, "ANGEBOT")
    # Footer
    c.setStrokeColor(colors.black); c.setLineWidth(0.8); c.line(ML, 28*mm, W - MR, 28*mm)
    c.setFillColor(GREY)
    def row(y, parts):
        total = sum(pdfmetrics.stringWidth(a, "LS-B", 8) + pdfmetrics.stringWidth(b + "     ", "LS", 8) for a, b in parts)
        x = (W - total) / 2
        for a, b in parts:
            c.setFont("LS-B", 8); c.drawString(x, y, a); x += pdfmetrics.stringWidth(a, "LS-B", 8)
            c.setFont("LS", 8); c.drawString(x, y, b); x += pdfmetrics.stringWidth(b + "     ", "LS", 8)
    row(22.5*mm, [("Adresse ", "Berlepschstr. 165 • 14165 • Berlin"), ("HR-Nr ", "HRB 249080 B"), ("USt-IdNr. ", "DE357948720")])
    row(18*mm, [("E-Mail ", "info@leanstech-gmbh.de"), ("Tel. ", "+491708280836"), ("Website ", "www.leanstech-gmbh.de")])
    c.setFont("LS", 8); c.drawCentredString(W/2, 11*mm, f"{doc.page}/{doc.total_pages}")
    c.restoreState()

class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=ML, rightMargin=MR, topMargin=0, bottomMargin=0, **kw)
        self.total_pages = 1
        f1 = Frame(ML, 34*mm, W-ML-MR, H - 34*mm - 96*mm, id="f1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        f2 = Frame(ML, 34*mm, W-ML-MR, H - 34*mm - 50*mm, id="f2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate("first", [f1], onPage=header_footer),
                               PageTemplate("later", [f2], onPage=header_footer)])
    def handle_pageBegin(self):
        self._handle_pageBegin()
        if self.page > 0: self._handle_nextPageTemplate("later")

def build(total_pages):
    doc = Doc(OUT); doc.total_pages = total_pages
    story = [Paragraph("ANGEBOT", stt), Spacer(1, 5*mm)]
    for line in SPEC["kopf"]: story.append(Paragraph(line, st))
    story.append(Spacer(1, 6*mm))
    cw = [10*mm, 72*mm, 14*mm, 15*mm, 21*mm, 15*mm, 15*mm, 22*mm]
    head = [Paragraph(x, ParagraphStyle("hh", parent=stb, alignment=TA_RIGHT if i >= 2 else 0)) for i, x in enumerate(["Nr.", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "USt. %", "USt.", "Betrag"])]
    rows = [head]; netto = 0.0; styles = []
    sts = ParagraphStyle("sec", parent=stb, fontSize=9.2, textColor=GREEN)
    abschnitte = SPEC.get("abschnitte") or [{"titel": None, "positionen": SPEC["positionen"]}]
    for a_i, a in enumerate(abschnitte, 1):
        multi = len(abschnitte) > 1
        if multi:
            r = len(rows); rows.append([Paragraph(f"{a_i}", sts), Paragraph(a["titel"], sts), "", "", "", "", "", ""])
            styles += [("SPAN", (1, r), (-1, r)), ("TOPPADDING", (0, r), (-1, r), 7)]
        sub = 0.0
        for i, p in enumerate(a["positionen"], 1):
            n = round(p["menge"] * p["ep"], 2); ust = round(n * 0.19, 2); sub += n
            nr = f"{a_i}.{i}" if multi else str(i)
            rows.append([Paragraph(nr, st), Paragraph(p["text"], st), Paragraph(num(p["menge"]), str_),
                         Paragraph(p["einheit"], str_), Paragraph(eur(p["ep"]), str_), Paragraph("19,00 %", str_),
                         Paragraph(eur(ust), str_), Paragraph(eur(n), str_)])
        netto += sub
        if multi:
            r = len(rows); rows.append(["", Paragraph(f"Zwischensumme Abschnitt {a_i} ({a['titel']}) netto", stbr), "", "", "", "", "", Paragraph(eur(sub), stbr)])
            styles += [("SPAN", (1, r), (6, r)), ("LINEABOVE", (1, r), (-1, r), 0.4, GREEN), ("BOTTOMPADDING", (0, r), (-1, r), 6)]
    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), LIGHT), ("VALIGN", (0,0), (-1,-1), "TOP"),
                           ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                           ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
                           ("LINEBELOW", (0,-1), (-1,-1), 0.8, GREEN)] + styles))
    story.append(t)
    netto = round(netto, 2); ust = round(netto * 0.19, 2); brutto = round(netto + ust, 2)
    tot = Table([[Paragraph("Nettobetrag", stb), Paragraph(eur(netto), stbr)],
                 [Paragraph("USt. 19,00 %", stb), Paragraph(eur(ust), stbr)],
                 [Paragraph('<font color="#5BAE5B" size="10">Gesamt</font>', stb), Paragraph(f'<font color="#5BAE5B" size="10">{eur(brutto)}</font>', stbr)]],
                colWidths=[30*mm, 32*mm], hAlign="RIGHT")
    tot.setStyle(TableStyle([("LINEABOVE", (0,2), (-1,2), 0.8, GREEN), ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2)]))
    story += [Spacer(1, 5*mm), KeepTogether(tot)]
    if SPEC.get("hinweise"):
        story += [Spacer(1, 8*mm), Paragraph("Hinweise", stb)]
        for h in SPEC["hinweise"]: story.append(Paragraph("• " + h, st))
    doc.build(story)
    return doc.page, netto, ust, brutto

pages, netto, ust, brutto = build(1)
if pages > 1: build(pages)
print(json.dumps({"seiten": pages, "netto": netto, "ust": ust, "brutto": brutto}))
