"""Gesamtmappe Liesborner Weg 19: Deckblatt mit anklickbarem Inhaltsverzeichnis, Übersicht, Villa und Neubau
(Schlussrechnungen, Fachunternehmererklärungen, Mailentwurf, alle Original-Belege) in einem PDF mit Lesezeichen."""
import os, sys, glob, tempfile
import pymupdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
import make_invoice_leans as inv

pdfmetrics.registerFont(TTFont("M", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
V, N = "Villa_0200", "Neubau_19ab_1150"

def eintraege():
    """(Ebene, Kürzel, Titel, Pfad oder Sonderseite)"""
    e = [(1, "", "Übersicht Villa und Neubau 19 a + b", "00_Uebersicht_Liesborner_Weg_19_Villa_und_Neubau.pdf"),
         (1, "A", "Villa – BV Liesborner Weg 19 (Projekt 0200)", "#teil:A"),
         (2, "A1", "Schlussrechnung kumuliert, alle Villa-Leistungen – 17.000,00 € brutto (Entwurf)",
          f"{V}/2_Schlussrechnung/Schlussrechnung_kumuliert_alle_Villa-Leistungen_17.000_brutto_ENTWURF.pdf"),
         (2, "A2", "Schlussrechnung nur Fußbodenheizung – 17.000,00 € brutto (Entwurf, alternativ zu A1)",
          f"{V}/2_Schlussrechnung/Schlussrechnung_Fussbodenheizung_17.000_brutto_ENTWURF.pdf"),
         (2, "A3", "Fachunternehmererklärung Heizung (Fußbodenheizung, hydraulischer Abgleich)",
          f"{V}/4_Fachunternehmererklaerungen/FUE_Villa_Heizung_Fussbodenheizung.pdf"),
         (2, "A4", "Fachunternehmererklärung Sanitär", f"{V}/4_Fachunternehmererklaerungen/FUE_Villa_Sanitaer.pdf"),
         (2, "A5", "Mailentwurf an CREST (mit Punkten vor dem Versand)", "#mail")]
    for i, f in enumerate(sorted(glob.glob(os.path.join(ROOT, V, "1_Belege_Original", "*.pdf"))), 6):
        e.append((2, f"A{i}", "Original: " + os.path.basename(f)[3:-4].replace("_", " "), os.path.relpath(f, ROOT)))
    e += [(1, "B", "Neubau Butterfly Houses – Liesborner Weg 19 a + b (Projekt 1150)", "#teil:B"),
          (2, "B1", "Schlussrechnung kumuliert mit Zahlungsaufstellung – Zahlbetrag 45.745,31 € (Entwurf)",
           f"{N}/5_Schlussrechnung/Schlussrechnung_kumuliert_Neubau_19ab_45.745,31_ENTWURF.pdf")]
    fue = [("Heizung inkl. Wärmepumpe und Fußbodenheizung", "Heizung"), ("Sanitär", "Sanitaer"), ("Lüftung", "Lueftung"), ("Klima", "Klima")]
    for i, (t, d) in enumerate(fue, 2):
        e.append((2, f"B{i}", f"Fachunternehmererklärung {t}", f"{N}/6_Fachunternehmererklaerungen/FUE_Neubau_19ab_{d}.pdf"))
    k = 6
    for ordner, praefix in (("1_Auftrag", "Auftrag: "), ("2_Angebote_Endstand", "Angebot: "), ("3_Nachtraege", "Nachtrag: "),
                            ("4_Rechnungen", "Rechnung: ")):
        for f in sorted(glob.glob(os.path.join(ROOT, N, ordner, "*.pdf"))):
            e.append((2, f"B{k}", praefix + os.path.basename(f)[:-4].replace("_", " "), os.path.relpath(f, ROOT))); k += 1
    return e

H1 = ParagraphStyle("h1", fontName="LB", fontSize=18, leading=23, textColor=inv.GREEN)
P = ParagraphStyle("p", fontName="L", fontSize=9, leading=12, textColor=inv.GREY)
T1 = ParagraphStyle("t1", fontName="LB", fontSize=8.5, leading=11, textColor=inv.GREY)
T2 = ParagraphStyle("t2", fontName="L", fontSize=8, leading=10.2, textColor=inv.GREY)

def deckblatt(path, e, seiten):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=14*mm)
    rows = [[Paragraph(x[1], T1 if x[0] == 1 else T2), Paragraph(x[2], T1 if x[0] == 1 else T2), Paragraph(str(seiten.get(i, "")), T2)]
            for i, x in enumerate(e)]
    t = Table(rows, colWidths=[12*mm, 148*mm, 14*mm])
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (2, 0), (2, -1), "RIGHT"),
          ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
          ("LINEBELOW", (0, 0), (-1, -1), 0.2, colors.HexColor("#DDDDDD"))]
    for i, x in enumerate(e):
        if x[0] == 1: st.append(("BACKGROUND", (0, i), (-1, i), inv.HEAD))
    t.setStyle(TableStyle(st))
    E = [Paragraph("Gesamtmappe BV Liesborner Weg 19, 13507 Berlin", H1), Spacer(1, 2*mm),
         Paragraph("Villa (Projekt 0200) und Neubau Butterfly Houses 19 a + b (Projekt 1150) · Auftraggeber CREST Living GmbH &amp; Co. KG · "
                   "LEANS Tech GmbH · Stand 19.10.2026", P), Spacer(1, 2*mm),
         Paragraph("<b>Hinweis:</b> Schlussrechnungen sind Entwürfe (Rechnungsnummer, Datum und Bankverbindung noch offen). "
                   "Fachunternehmererklärungen sind zur Unterschrift vorbereitet. Einträge im Inhaltsverzeichnis sind anklickbar; "
                   "die Lesezeichen im PDF-Viewer führen ebenfalls zu jedem Dokument.", P), Spacer(1, 4*mm), t]
    doc.build(E)

def trennblatt(path, titel, unter):
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=110*mm)
    doc.build([Paragraph(titel, ParagraphStyle("x", parent=H1, fontSize=24, leading=30, alignment=1)), Spacer(1, 6*mm),
               Paragraph(unter, ParagraphStyle("y", parent=P, fontSize=11, leading=15, alignment=1))])

def mailseite(path):
    txt = open(os.path.join(ROOT, V, "3_Versand", "Mail_an_CREST_Schlussrechnung_FBH_ENTWURF.txt"), encoding="utf-8").read()
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=14*mm, topMargin=16*mm, bottomMargin=14*mm)
    doc.build([Paragraph("A5 · Mailentwurf an CREST", ParagraphStyle("h", parent=H1, fontSize=13, leading=17)), Spacer(1, 3*mm),
               Preformatted(txt, ParagraphStyle("m", fontName="M", fontSize=7.6, leading=9.6, textColor=inv.GREY))])

def build(out):
    e = eintraege(); tmp = tempfile.mkdtemp()
    teile = {"#teil:A": ("A · Villa", "BV Liesborner Weg 19 (Projekt 0200)<br/>Schlussrechnung, Fachunternehmererklärungen, Mailentwurf, Original-Belege"),
             "#teil:B": ("B · Neubau 19 a + b", "Butterfly Houses, Liesborner Weg 19 a und b (Projekt 1150)<br/>Schlussrechnung, Fachunternehmererklärungen, Auftrag, Angebote, Nachträge, Rechnungen")}
    docs = []
    for i, (lvl, kz, titel, src) in enumerate(e):
        if src in teile:
            p = os.path.join(tmp, f"t{i}.pdf"); trennblatt(p, *teile[src])
        elif src == "#mail":
            p = os.path.join(tmp, "mail.pdf"); mailseite(p)
        else:
            p = os.path.join(ROOT, src); assert os.path.exists(p), p
        docs.append(pymupdf.open(p))
    # Deckblatt zweimal rendern: erst Seitenzahl des Deckblatts ermitteln, dann mit endgültigen Seitenzahlen
    cover = os.path.join(tmp, "cover.pdf"); deckblatt(cover, e, {}); n_cover = pymupdf.open(cover).page_count
    seiten, s = {}, n_cover + 1
    for i, d in enumerate(docs): seiten[i] = s; s += d.page_count
    deckblatt(cover, e, seiten); assert pymupdf.open(cover).page_count == n_cover
    m = pymupdf.open(cover)
    for d in docs: m.insert_pdf(d)
    # Inhaltsverzeichnis anklickbar machen: Zeile des Kürzels/Titels suchen und auf die Zielseite verlinken
    # Einträge der Reihe nach suchen (gleiche Titel wie „Fachunternehmererklärung Sanitär“ kommen bei A und B vor)
    pos = (0, -1.0)
    for i, (lvl, kz, titel, src) in enumerate(e):
        needle = titel[:60]
        treffer = [(pno, h) for pno in range(n_cover) for h in m[pno].search_for(needle)]
        treffer = [(pno, h) for pno, h in sorted(treffer, key=lambda x: (x[0], x[1].y0)) if (pno, h.y0) > pos]
        if not treffer: raise AssertionError(f"TOC-Eintrag nicht gefunden: {needle}")
        pno, r = treffer[0]; pos = (pno, r.y0)
        r = pymupdf.Rect(15*mm*72/25.4, r.y0 - 1, m[pno].rect.width - 15*mm*72/25.4, r.y1 + 1)
        m[pno].insert_link({"kind": pymupdf.LINK_GOTO, "from": r, "page": seiten[i] - 1})
    m.set_toc([[1, "Deckblatt und Inhaltsverzeichnis", 1]] + [[lvl, (kz + " · " if kz else "") + titel, seiten[i]] for i, (lvl, kz, titel, _) in enumerate(e)])
    m.set_metadata({"title": "Gesamtmappe BV Liesborner Weg 19 – Villa und Neubau 19 a + b", "author": "LEANS Tech GmbH"})
    m.save(out, garbage=3, deflate=True)
    return m.page_count, len(e)

if __name__ == "__main__":
    print("Seiten, Einträge:", build(sys.argv[1]))
