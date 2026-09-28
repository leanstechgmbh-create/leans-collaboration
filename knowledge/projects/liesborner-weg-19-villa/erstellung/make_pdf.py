import sys
from decimal import Decimal as D
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from data import SANITAER, HEIZUNG, VORRECHNUNGEN, FBH_RABATT, totals, line_total
from payments import ZAHLUNGEN

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

def eur(x):
    s = f"{D(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def qty(x):
    return f"{D(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

S = lambda **kw: ParagraphStyle("s", fontName="DV", fontSize=8.5, leading=11, **kw)
st, stb = S(), ParagraphStyle("b", fontName="DVB", fontSize=8.5, leading=11)
small = ParagraphStyle("sm", fontName="DV", fontSize=7, leading=9, textColor=colors.HexColor("#444444"))
h1 = ParagraphStyle("h1", fontName="DVB", fontSize=15, leading=19, spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="DVB", fontSize=10, leading=13, spaceBefore=8, spaceAfter=3)

FOOT1 = "LEANS Tech GmbH · Berlepschstr. 165 · 14165 Berlin · HRB 249080 B · USt-IdNr. DE357948720 · Steuernummer 29/414/31448"
FOOT2 = "info@leanstech-gmbh.de · Tel. +49 170 8280836 · Berliner Volksbank · IBAN DE21 1009 0000 2911 7280 04 · BIC BEVODEBBXXX"

def on_page(c, doc):
    c.saveState()
    c.setFont("DVB", 36); c.setFillColor(colors.Color(0.85, 0.1, 0.1, alpha=0.10))
    c.translate(105*mm, 150*mm); c.rotate(35); c.drawCentredString(0, 0, "ENTWURF – NICHT VERSENDEN")
    c.restoreState()
    c.saveState(); c.setFont("DV", 6.5); c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(105*mm, 11*mm, FOOT1); c.drawCentredString(105*mm, 7.5*mm, FOOT2)
    c.drawRightString(195*mm, 15*mm, f"Seite {doc.page}")
    c.restoreState()

def grid(data, widths, bold_rows=(), right_cols=(), header=True, shade_rows=()):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("FONT", (0, 0), (-1, -1), "DV", 8), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black) if header else ("TOPPADDING", (0, 0), (-1, -1), 1),
             ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]
    if header: style.append(("FONT", (0, 0), (-1, 0), "DVB", 8))
    for c in right_cols: style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    for r in bold_rows: style += [("FONT", (0, r), (-1, r), "DVB", 8), ("LINEABOVE", (0, r), (-1, r), 0.4, colors.black)]
    for r in shade_rows: style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#EEF2F7")))
    t.setStyle(TableStyle(style)); return t

def build(path):
    t = totals()
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=20*mm,
                          title="Kumulierte Schlussrechnung BV Liesborner Weg 19 (Villa) – ENTWURF",
                          author="LEANS Tech GmbH")
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=on_page)])
    E = []
    E.append(Paragraph("LEANS Tech GmbH · Semir Redzic · Berlepschstr. 165 · 14165 Berlin", small))
    E.append(Spacer(1, 3*mm))
    head = Table([[Paragraph("CREST Living GmbH &amp; Co. KG<br/>Liesborner Weg 19<br/>13507 Berlin", st),
                   Paragraph("<b>Rechnungsnummer:</b> 2026-____ <font color='#b00000'>(vergeben)</font><br/>"
                             "<b>Rechnungsdatum:</b> __.__.2026<br/><b>Zahlungsziel:</b> 10 Tage netto<br/>"
                             "<b>Projekt-Nr. LEANS:</b> 0200 (Liesborner Weg ALT)", st)]],
                 colWidths=[95*mm, 82*mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    E += [head, Spacer(1, 6*mm)]
    E.append(Paragraph("SCHLUSSRECHNUNG (kumuliert)", h1))
    E.append(Paragraph("<b>BV:</b> Liesborner Weg 19, 13507 Berlin – Villa (Bestandsgebäude) &nbsp;·&nbsp; "
                       "<b>Gewerke:</b> Sanitärobjekte/Armaturenmontage, Heizung (Fußbodenheizung, hydraulischer Abgleich)<br/>"
                       "<b>Leistungszeitraum:</b> 07.01.2024 – 03.12.2024 &nbsp;·&nbsp; <b>Grundlage:</b> Beauftragung durch CREST Living "
                       "(Baustellensitzungen BV Liesborner Weg 19 Villa, Jan. 2024 ff.), Nachtragsangebot 175 vom 05.01.2025", st))
    E.append(Spacer(1, 2*mm))
    E.append(Paragraph("Diese Schlussrechnung fasst sämtliche Leistungen am BV zusammen. Sie <b>ersetzt die Dokumente „Schlussrechnung 176“ vom 05.01.2025</b> (Fußbodenheizung, 22.541,30 € brutto) "
                       "<b>und „Rechnung 159“ vom 03.12.2024</b> (hydraulischer Abgleich, 321,30 € brutto), die beide an CREST Investment GmbH "
                       "gingen und nur eine Angebots-, aber keine Rechnungsnummer trugen. Bereits gestellte Rechnungen werden unten abgezogen.", st))

    # --- Leistungsaufstellung
    E.append(Paragraph("A. Leistungsaufstellung (gesamt)", h2))
    hdr = ["Pos.", "Beschreibung", "Menge", "Einh.", "EP netto", "GP netto", "Beleg"]
    W = [15*mm, 83*mm, 13*mm, 11*mm, 18*mm, 20*mm, 17*mm]
    rows, bold, shade = [hdr], [], []
    rows.append(["1", Paragraph("<b>Sanitärobjekte liefern und montieren, bauseits gelieferte Armaturen montieren</b>", st), "", "", "", "", ""])
    shade.append(len(rows)-1)
    for p, txt, q, u, ep, b in SANITAER:
        if q is None:
            rows.append([p, Paragraph(f"<i>{txt}</i>", st), "", "", "", "", ""]); continue
        rows.append([p, Paragraph(txt, st), qty(q), u, eur(ep), eur(line_total(q, ep)), b])
    rows.append(["", "Summe Titel 1 Sanitär", "", "", "", eur(t["san"]), ""]); bold.append(len(rows)-1)
    rows.append(["2", Paragraph("<b>Heizung</b>", st), "", "", "", "", ""]); shade.append(len(rows)-1)
    for p, txt, q, u, ep, b in HEIZUNG:
        rows.append([p, Paragraph(txt, st), qty(q), u, eur(ep), eur(line_total(q, ep)), b])
    rows.append(["", f"abzgl. {int(FBH_RABATT*100)} % Rabatt auf Pos. 2.7.0–2.11 (wie Dok. 176)", "", "", "", "-" + eur(t["rabatt"]), ""])
    rows.append(["", "Summe Titel 2 Heizung", "", "", "", eur(t["hz_abgleich"] + t["fbh_netto"]), ""]); bold.append(len(rows)-1)
    E.append(grid(rows, W, bold_rows=bold, right_cols=(2, 4, 5), shade_rows=shade))
    E.append(Paragraph("* Pos.-Nr. 1.1.1 wurde in RE 2025-17 ein zweites Mal vergeben; zur Unterscheidung mit * gekennzeichnet.", small))

    # --- Zusammenstellung
    E.append(Paragraph("B. Zusammenstellung", h2))
    z = [["", "netto", "USt 19 %", "brutto"],
         ["Gesamtleistung (Titel 1 + 2)", eur(t["gesamt_netto"]), eur(t["ust"]), eur(t["gesamt_brutto"])]]
    for nr, dat, emp, gew, n, u, b in VORRECHNUNGEN:
        z.append([Paragraph(f"abzgl. RE {nr} vom {dat} ({gew}; an {emp})", st), "-" + eur(n), "-" + eur(u), "-" + eur(b)])
    z.append(["Restbetrag dieser Schlussrechnung", eur(t["rest_netto"]), eur(t["rest_ust"]), eur(t["rest_brutto"])])
    E.append(grid(z, [95*mm, 27*mm, 27*mm, 28*mm], bold_rows=(1, len(z)-1), right_cols=(1, 2, 3)))

    # --- Zahlungsstand
    secC = [Paragraph("C. Zahlungsstand und Zahlbetrag", h2)]
    zr = [["Beleg", "Rechnungsbetrag", "gezahlt", "Zahlung / Quelle", "offen"]]
    offen_sum = D("0"); pending = []
    for nr, dat, emp, gew, n, u, b in VORRECHNUNGEN:
        paid, info = ZAHLUNGEN.get(nr, (D("0"), "keine Zahlung gefunden"))
        if paid is None:
            zr.append([f"RE {nr}", eur(b), "in Prüfung", Paragraph(info, st), "?"]); pending.append(nr); continue
        offen = b - paid; offen_sum += offen
        zr.append([f"RE {nr}", eur(b), eur(paid), Paragraph(info, st), eur(offen)])
    zr.append(["diese Schlussrechnung", eur(t["rest_brutto"]), eur(0), Paragraph("ersetzt Dok. 159 + Dok. 176 (beide unbezahlt)", st), eur(t["rest_brutto"])])
    offen_sum += t["rest_brutto"]
    zr.append(["Zu zahlender Gesamtbetrag" + (" *" if pending else ""), "", "", "", eur(offen_sum)])
    secC.append(grid(zr, [30*mm, 26*mm, 24*mm, 73*mm, 24*mm], bold_rows=(len(zr)-1,), right_cols=(1, 2, 4)))
    E.append(KeepTogether(secC))
    if pending:
        E.append(Paragraph("* ohne RE " + ", ".join(pending) + " – Zahlungseingang noch nicht verifiziert; falls unbezahlt, erhöht sich der Betrag entsprechend.", small))
    E.append(Spacer(1, 3*mm))
    E.append(KeepTogether([Paragraph(
        f"Bitte überweisen Sie <b>{eur(offen_sum)}</b> innerhalb von 10 Tagen unter Angabe der Rechnungsnummer auf das unten "
        "genannte Konto.", st),
        Spacer(1, 2*mm),
        Paragraph("Hinweis Rundung: Im Dok. 176 wurde die USt je Position brutto gerundet (22.541,30 €); hier wird die USt auf die "
                  "Nettosumme gerechnet (FBH 22.541,29 €), daher 1 Cent Differenz.", small)]))
    doc.build(E)
    return offen_sum

if __name__ == "__main__":
    print("Zahlbetrag:", build(sys.argv[1]))
