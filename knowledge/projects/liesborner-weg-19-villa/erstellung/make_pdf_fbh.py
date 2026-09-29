"""Eigenständige Schlussrechnung Fußbodenheizung Villa (ersetzt Dok. 176 und Dok. 159)."""
import sys
from decimal import Decimal as D
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
from data import HEIZUNG, FBH_RABATT, VAT, r2, line_total
from make_pdf import on_page, grid, eur, qty, st, small, h1, h2

def build(path):
    fbh = [h for h in HEIZUNG if h[5] == "Dok. 176"]
    abgl = [h for h in HEIZUNG if h[5] == "Dok. 159"]
    s_fbh = sum(line_total(q, ep) for _, _, q, _, ep, _ in fbh)
    rabatt = r2(s_fbh * FBH_RABATT)
    s_abgl = sum(line_total(q, ep) for _, _, q, _, ep, _ in abgl)
    netto = s_fbh - rabatt + s_abgl
    ust = r2(netto * VAT); brutto = netto + ust

    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=20*mm,
                          title="Schlussrechnung Fußbodenheizung BV Liesborner Weg 19 (Villa) – ENTWURF", author="LEANS Tech GmbH")
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)], onPage=on_page)])
    E = [Paragraph("LEANS Tech GmbH · Semir Redzic · Berlepschstr. 165 · 14165 Berlin", small), Spacer(1, 3*mm)]
    head = Table([[Paragraph("CREST Living GmbH &amp; Co. KG<br/>Liesborner Weg 19<br/>13507 Berlin", st),
                   Paragraph("<b>Rechnungsnummer:</b> 2026-____ <font color='#b00000'>(vergeben)</font><br/>"
                             "<b>Rechnungsdatum:</b> __.__.2026<br/><b>Zahlungsziel:</b> 10 Tage netto<br/>"
                             "<b>Projekt-Nr. LEANS:</b> 0200 (Liesborner Weg ALT)", st)]], colWidths=[95*mm, 82*mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    E += [head, Spacer(1, 6*mm), Paragraph("SCHLUSSRECHNUNG Fußbodenheizung", h1)]
    E.append(Paragraph("<b>BV:</b> Liesborner Weg 19, 13507 Berlin – Villa &nbsp;·&nbsp; <b>Gewerk:</b> Heizung / Fußbodenheizung<br/>"
                       "<b>Leistungszeitraum:</b> 11/2023 – 03.12.2024 (Verlegung OG/UG bis 04.11.2023, EG ab 13.12.2023, Befüllung, Aufheizen; hydraulischer Abgleich am 03.12.2024)", st))
    E.append(Spacer(1, 2*mm))
    E.append(Paragraph("Diese Schlussrechnung <b>ersetzt</b> die Dokumente „Schlussrechnung 176“ vom 05.01.2025 (22.541,30 €) und "
                       "„Rechnung 159“ vom 03.12.2024 (321,30 €), die ohne Rechnungsnummer an CREST Investment GmbH gingen. "
                       "Auf beide Dokumente ist keine Zahlung eingegangen.", st))
    E.append(Paragraph("Leistungen", h2))
    rows = [["Pos.", "Beschreibung", "Menge", "Einh.", "EP netto", "GP netto"]]
    for p, t, q, u, ep, _ in fbh:
        rows.append([p, Paragraph(t, st), qty(q), u, eur(ep), eur(line_total(q, ep))])
    rows.append(["", "Zwischensumme Fußbodenheizung", "", "", "", eur(s_fbh)])
    rows.append(["", f"abzgl. {int(FBH_RABATT*100)} % Rabatt (wie vereinbart)", "", "", "", "-" + eur(rabatt)])
    for p, t, q, u, ep, _ in abgl:
        rows.append([p, Paragraph(t, st), qty(q), u, eur(ep), eur(line_total(q, ep))])
    n = len(rows)
    rows += [["", "Nettobetrag", "", "", "", eur(netto)],
             ["", "zzgl. 19 % USt", "", "", "", eur(ust)],
             ["", "Rechnungsbetrag brutto", "", "", "", eur(brutto)],
             ["", "abzgl. bereits geleistete Zahlungen", "", "", "", eur(0)],
             ["", "Zu zahlender Betrag", "", "", "", eur(brutto)]]
    E.append(grid(rows, [15*mm, 99*mm, 15*mm, 12*mm, 18*mm, 21*mm], bold_rows=(len(fbh)+1, n, n+2, n+4), right_cols=(2, 4, 5)))
    E.append(Spacer(1, 4*mm))
    E.append(KeepTogether([
        Paragraph(f"Bitte überweisen Sie <b>{eur(brutto)}</b> innerhalb von 10 Tagen unter Angabe der Rechnungsnummer auf das unten genannte Konto.", st),
        Spacer(1, 2*mm),
        Paragraph("Rundungshinweis: Dok. 176 rundete die USt je Position (22.541,30 €); hier wird die USt auf den Nettobetrag gerechnet "
                  "(Fußbodenheizung 22.541,29 €).", small)]))
    doc.build(E)
    return netto, ust, brutto

if __name__ == "__main__":
    print(build(sys.argv[1]))
