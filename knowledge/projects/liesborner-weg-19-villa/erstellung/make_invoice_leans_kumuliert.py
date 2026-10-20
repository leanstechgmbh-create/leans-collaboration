"""Kumulierte Schlussrechnung Villa im LEANS-Rechnungslayout: alle Leistungen, die bisher einzeln
abgerechnet wurden (RE 2024-47, RE 2025-17, Dok. 159, Dok. 176), in einer Rechnung. Heizung pauschaliert
auf 20.000,00 € netto wie in der Schlussrechnung Fußbodenheizung; die gestellten Rechnungen werden mit
Netto- und Steuerbetrag abgezogen (§ 14 Abs. 5 UStG)."""
import sys
from decimal import Decimal as D
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from data import SANITAER, HEIZUNG, VORRECHNUNGEN, VAT, r2, line_total
from make_invoice_leans import (page, P, eur, num, GREY, HEAD, LEISTUNGSZEITRAUM, ABZUG_TEXT,
                                ZIEL_BRUTTO, ZIEL_NETTO, ABZUG_BRUTTO, ABZUG_NETTO, REST_BRUTTO, REST_NETTO, REST_UST)

PS = ParagraphStyle("ps", parent=P, fontSize=7, leading=9, textColor="#777777")
PT = ParagraphStyle("pt", parent=P, fontSize=7.5, leading=9.5)
# Zahlungseingänge laut Kontoauszug Berliner Volksbank. 2024-47 gilt laut Semir als bezahlt; das Datum ist nicht
# belegt, weil die Kontoauszüge April–Juli 2024 nicht in Drive liegen → rot markierter Platzhalter bis zur Bestätigung.
ZAHLUNGSDATUM = {"2025-17": "19.09.2025"}
ZAHLUNGSDATUM_OFFEN = "__.__.2024"
SHADE = "#F1F7F1"

def gruppen():
    """Titel in Abrechnungsreihenfolge: (titel, beleg-text, [(stockwerk|None, orig_pos, text, menge, einheit, ep)])."""
    def sanitaer(beleg):
        rows, etage = [], None
        for p, t, q, u, ep, b in SANITAER:
            if q is None: etage = t; continue
            if b == beleg: rows.append((etage, p.rstrip("*"), t, q, u, ep))
        return rows
    heiz = lambda beleg: [(None, p, t, q, u, ep) for p, t, q, u, ep, b in HEIZUNG if b == beleg]
    vr = {v[0]: v for v in VORRECHNUNGEN}
    return [
        ("Sanitärobjekte liefern und montieren, Armaturen montieren", f"abgerechnet mit RE 2024-47 vom {vr['2024-47'][1]}", "RE 2024-47", sanitaer("RE 2024-47")),
        ("Sanitär-Nachtrag", f"abgerechnet mit RE 2025-17 vom {vr['2025-17'][1]}", "RE 2025-17", sanitaer("RE 2025-17")),
        ("Heizung: hydraulischer Abgleich", "bisher Dok. Nr. 159 vom 03.12.2024, wird ersetzt", "Dok. 159", heiz("Dok. 159")),
        ("Heizung: Fußbodenheizung", "bisher Dok. Nr. 176 vom 05.01.2025, wird ersetzt", "Dok. 176", heiz("Dok. 176")),
    ]

def werte():
    g = gruppen()
    titel = [sum(line_total(q, ep) for *_, q, u, ep in rows) for *_, rows in g]
    liste = sum(titel)
    heizung_liste = titel[2] + titel[3]
    nachlass = heizung_liste - ZIEL_NETTO
    netto = liste - nachlass - ABZUG_NETTO
    vr_n = sum(v[4] for v in VORRECHNUNGEN); vr_u = sum(v[5] for v in VORRECHNUNGEN)
    # USt der Gesamtleistung = USt der gestellten Rechnungen + USt aus der Bruttopauschale (Rest exakt 16.000,00 € brutto)
    ust = vr_u + REST_UST
    return dict(titel=titel, liste=liste, heizung_liste=heizung_liste, nachlass=nachlass, netto=netto, ust=ust,
                brutto=netto + ust, rest_netto=netto - vr_n, rest_ust=ust - vr_u, rest_brutto=netto + ust - vr_n - vr_u)

def tab(data, widths, style):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "L", 8), ("TEXTCOLOR", (0, 0), (-1, -1), GREY),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONT", (0, 0), (-1, 0), "LB", 8),
                           ("BACKGROUND", (0, 0), (-1, 0), HEAD),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6)] + style))
    return t

def build(path):
    w = werte(); g = gruppen()
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=90*mm, bottomMargin=34*mm,
                          title="Schlussrechnung 2026-44 – BV Liesborner Weg 19 (Villa)", author="LEANS Tech GmbH")
    later = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 54*mm, id="later")
    first = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 124*mm, id="first")
    doc.addPageTemplates([PageTemplate(id="p1", frames=[first], onPage=page, autoNextPageTemplate="pn"),
                          PageTemplate(id="pn", frames=[later], onPage=page)])
    E = [Paragraph("<font color='#4CAF50' size='14'><b>SCHLUSSRECHNUNG</b></font>",
                   ParagraphStyle("t", fontName="LB", fontSize=14, leading=18)),
         Spacer(1, 3*mm),
         Paragraph("BV: Liesborner Weg 19<br/>13507 Berlin (Villa)<br/>"
                   "Gewerke: Sanitär (Sanitärobjekte, Armaturenmontage) und Heizung (Fußbodenheizung, hydraulischer Abgleich)<br/>"
                   f"Leistungszeitraum: {LEISTUNGSZEITRAUM}", P),
         Spacer(1, 2*mm),
         Paragraph("Diese Schlussrechnung fasst alle Leistungen am BV zusammen, die bisher einzeln abgerechnet wurden. "
                   "Die bereits gestellten Rechnungen werden mit Netto- und Steuerbetrag abgezogen.", P),
         Spacer(1, 4*mm)]

    # A. Leistungsaufstellung
    E.append(Paragraph("<b>A. Leistungsaufstellung</b>", P)); E.append(Spacer(1, 1.5*mm))
    data = [["Pos.", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "Gesamt netto"]]
    st = [("ALIGN", (2, 0), (-1, -1), "RIGHT"), ("ALIGN", (3, 0), (3, -1), "CENTER")]
    for ti, (titel, herkunft, beleg, rows) in enumerate(g, 1):
        data.append([str(ti), Paragraph(f"<b>{titel}</b>", P), "", "", "", ""])
        st += [("BACKGROUND", (0, len(data)-1), (-1, len(data)-1), SHADE), ("SPAN", (1, len(data)-1), (-1, len(data)-1))]
        etage_alt, n = object(), 0
        for etage, op, txt, q, u, ep in rows:
            if etage and etage != etage_alt:
                data.append(["", Paragraph(f"<i>{etage}</i>", P), "", "", "", ""]); etage_alt = etage
            n += 1
            data.append([f"{ti}.{n}", Paragraph(txt, P),
                         num(q), u, eur(ep), eur(line_total(q, ep))])
        data.append(["", Paragraph(f"<b>Summe Titel {ti}</b>", P), "", "", "", eur(w["titel"][ti-1])])
        r = len(data) - 1
        st += [("LINEABOVE", (0, r), (-1, r), 0.5, GREY), ("FONT", (5, r), (5, r), "LB", 8), ("SPAN", (1, r), (4, r))]
    E.append(tab(data, [12*mm, 92*mm, 14*mm, 12*mm, 19*mm, 21*mm], st))

    # B. Zusammenstellung
    z = [["", "netto"]]
    for ti, (titel, herkunft, beleg, rows) in enumerate(g, 1):
        z.append([f"Titel {ti}: {titel}", eur(w["titel"][ti-1])])
    z += [["Summe zu Listenpreisen", eur(w["liste"])],
          [Paragraph(f"Nachlass Heizung (Titel 3 + 4: {eur(w['heizung_liste'])} netto, pauschaliert auf {eur(ZIEL_NETTO)} netto = {eur(ZIEL_BRUTTO)} brutto)", P), "-" + eur(w["nachlass"])],
          [Paragraph(f"{ABZUG_TEXT}: {eur(ABZUG_BRUTTO)} brutto", P), "-" + eur(ABZUG_NETTO)],
          ["Gesamtleistung netto", eur(w["netto"])]]
    k = len(z)
    secB = [Spacer(1, 5*mm), Paragraph("<b>B. Zusammenstellung</b>", P), Spacer(1, 1.5*mm),
            tab(z, [149*mm, 21*mm], [("ALIGN", (1, 0), (1, -1), "RIGHT"), ("LINEABOVE", (0, k-4), (-1, k-4), 0.5, GREY),
                                     ("LINEABOVE", (0, k-1), (-1, k-1), 0.8, GREY), ("FONT", (0, k-1), (-1, k-1), "LB", 8)])]
    E.append(KeepTogether(secB))

    # C. Abrechnung
    a = [["", "netto", "USt. 19 %", "brutto"],
         ["Gesamtleistung", eur(w["netto"]), eur(w["ust"]), eur(w["brutto"])]]
    for nr, dat, emp, gew, n, u, b in VORRECHNUNGEN:
        a.append([f"abzgl. RE {nr} vom {dat}", "-" + eur(n), "-" + eur(u), "-" + eur(b)])
    a.append(["Zahlbetrag dieser Schlussrechnung", eur(w["rest_netto"]), eur(w["rest_ust"]), eur(w["rest_brutto"])])
    k = len(a)
    secC = [Spacer(1, 5*mm), Paragraph("<b>C. Abrechnung</b>", P), Spacer(1, 1.5*mm),
            tab(a, [95*mm, 25*mm, 25*mm, 25*mm], [("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("FONT", (0, 1), (-1, 1), "LB", 8),
                                                   ("LINEABOVE", (0, k-1), (-1, k-1), 0.8, GREY), ("FONT", (0, k-1), (-1, k-1), "LB", 8.5)]),
            Spacer(1, 1.5*mm),
            Paragraph("Die Heizung ist als Bruttopauschale vereinbart; Netto und Umsatzsteuer sind daraus herausgerechnet. "
                      "Dadurch kann die Umsatzsteuer der Gesamtleistung um 0,01 € von 19 % abweichen.", PS),
            Spacer(1, 3*mm),
            # Kurzübersicht wie besprochen: offener Betrag, Abzug, Zahlbetrag (alles brutto)
            tab([["Kurz zusammengefasst", "brutto"],
                 ["Offener Betrag Villa (Heizung pauschal)", eur(ZIEL_BRUTTO)],
                 [ABZUG_TEXT, "-" + eur(ABZUG_BRUTTO)],
                 ["Zahlbetrag dieser Schlussrechnung", eur(REST_BRUTTO)]],
                [145*mm, 25*mm], [("ALIGN", (1, 0), (1, -1), "RIGHT"), ("LINEABOVE", (0, 3), (-1, 3), 0.8, GREY),
                                  ("FONT", (0, 3), (-1, 3), "LB", 8.5)])]
    assert ZIEL_BRUTTO - ABZUG_BRUTTO == REST_BRUTTO == w["rest_brutto"]
    E.append(KeepTogether(secC))

    # D. Zahlungsaufstellung: jede Villa-Rechnung, was bezahlt ist und was offen
    rot = lambda t: Paragraph(f"<font color='#B00000'>{t}</font>", PT)
    zr = [["Rechnung", "Datum", "Leistung", "brutto", "gezahlt", "Zahlungsdatum", "offen"]]
    for nr, dat, emp, gew, n, u, b in VORRECHNUNGEN:
        datum = ZAHLUNGSDATUM.get(nr) or (rot(ZAHLUNGSDATUM_OFFEN) if "_" in ZAHLUNGSDATUM_OFFEN else ZAHLUNGSDATUM_OFFEN)
        zr.append([f"RE {nr}", dat, Paragraph(gew, PT), eur(b), eur(b), datum, eur(0)])
    zr += [["2026-44", "19.10.2026", Paragraph("<b>Diese Schlussrechnung</b> – Heizung (Titel 3 + 4)", PT), eur(w["rest_brutto"]), eur(0), "–",
            eur(w["rest_brutto"])],
           [Paragraph("<b>Summe offen</b>", PT), "", "", "", "", "", eur(w["rest_brutto"])]]
    k = len(zr) - 1
    secD = [Spacer(1, 5*mm), Paragraph("<b>D. Zahlungsaufstellung</b>", P), Spacer(1, 1.5*mm),
            tab(zr, [24*mm, 18*mm, 50*mm, 20*mm, 19*mm, 20*mm, 19*mm],
                [("ALIGN", (3, 0), (4, -1), "RIGHT"), ("ALIGN", (6, 0), (6, -1), "RIGHT"), ("LINEABOVE", (0, k), (-1, k), 0.8, GREY),
                 ("FONT", (6, k), (6, k), "LB", 8.5)]),
            Spacer(1, 4*mm),
            Paragraph("Die Rechnungen 2024-47 und 2025-17 sind bezahlt und in dieser Schlussrechnung abgezogen.", P),
            Spacer(1, 2*mm),
            Paragraph(f"Bitte überweisen Sie den Betrag von <b>{eur(w['rest_brutto'])}</b> bis zum Fälligkeitsdatum ohne Abzug unter Angabe der "
                      "Rechnungsnummer auf das unten genannte Konto.", P)]
    E.append(KeepTogether(secD))
    doc.build(E)
    return w

if __name__ == "__main__":
    w = build(sys.argv[1])
    for k, v in w.items(): print(f"{k:13} {v}")
    assert w["titel"] == [D("12481.00"), D("4758.00"), D("270.00"), D("21525.30")], w["titel"]
    assert (w["rest_netto"], w["rest_ust"], w["rest_brutto"]) == (REST_NETTO, REST_UST, REST_BRUTTO), w
    for nr, dat, emp, gew, n, u, b in VORRECHNUNGEN:
        assert sum(line_total(q, ep) for *_, q, u2, ep in dict((x[2], x[3]) for x in gruppen())[f"RE {nr}"]) == n, nr
