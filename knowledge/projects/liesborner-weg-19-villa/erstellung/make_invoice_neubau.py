"""Kumulierte Schlussrechnung Neubau Butterfly Houses Liesborner Weg 19 a + b (beide Häuser zusammen) im
LEANS-Rechnungslayout: Gesamtleistung (Pauschale + Nachträge), Abzug aller Abschlagsrechnungen mit Netto und USt
(§ 14 Abs. 5 UStG), Zahlungsaufstellung mit den CREST-Abzügen und den noch offenen Beträgen."""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from data_neubau import werte, NACHTRAEGE
from make_invoice_leans import page, P, eur, GREY, HEAD

LEISTUNGSZEITRAUM = "05.2025 – 16.12.2025"   # Bauablaufplan ab KW 20/2025, letzte AR bis 16.12.2025
PS = ParagraphStyle("ps", parent=P, fontSize=7.5, leading=9.5)
H = lambda t: Paragraph(f"<b>{t}</b>", P)

def tab(data, widths, style, font=8):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "L", font), ("TEXTCOLOR", (0, 0), (-1, -1), GREY),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONT", (0, 0), (-1, 0), "LB", font),
                           ("BACKGROUND", (0, 0), (-1, 0), HEAD),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6)] + style))
    return t

def build(path):
    w = werte()
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=90*mm, bottomMargin=34*mm,
                          title="Schlussrechnung 2026-45 – BV Liesborner Weg 19 a und b (Neubau)", author="LEANS Tech GmbH")
    later = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 54*mm, id="later")
    first = Frame(20*mm, 34*mm, A4[0] - 40*mm, A4[1] - 124*mm, id="first")
    doc.addPageTemplates([PageTemplate(id="p1", frames=[first], onPage=page, autoNextPageTemplate="pn"),
                          PageTemplate(id="pn", frames=[later], onPage=page)])
    E = [Paragraph("<font color='#4CAF50' size='14'><b>SCHLUSSRECHNUNG</b></font>",
                   ParagraphStyle("t", fontName="LB", fontSize=14, leading=18)),
         Spacer(1, 3*mm),
         Paragraph("Liesborner Weg 19 a und b (Neubau Butterfly Houses, Haus 1 und Haus 2)<br/>13507 Berlin<br/>"
                   "Auftrag Nr: 20250418_# · Bauvertrag HLS mit Anlage 1 (Zahlungsplan) vom 15.05.2025<br/>"
                   f"Gewerk: Heizung, Klima, Lüftung und Sanitär<br/>Leistungszeitraum: {LEISTUNGSZEITRAUM}", P),
         Spacer(1, 2*mm),
         Paragraph("Mit dieser Schlussrechnung rechnen wir die Gesamtleistung für beide Häuser ab. Alle Abschlagsrechnungen werden "
                   "mit Netto- und Steuerbetrag abgezogen. Die Zahlungsaufstellung zeigt jede Zahlung mit Ihren Abzügen und die noch offenen Beträge.", P),
         Spacer(1, 4*mm)]

    # A. Gesamtleistung
    a = [["Pos.", "Leistung", "netto", "USt. 19 %", "brutto"],
         ["1", Paragraph("Pauschalpreis HLS lt. Bauvertrag und Zahlungsplan vom 15.05.2025: Rohinstallation, Fußbodenheizung, "
                         "Heizungsraum/Klima/Wärmepumpe, Komplettierung Armaturen (GESSI 316, Edelstahl), Inbetriebnahme und Abnahme", P),
          eur(w["p_netto"]), eur(w["p_ust"]), eur(w["p_netto"] + w["p_ust"])]]
    for i, (n, ang, dat, txt, net, ust) in enumerate(w["na"], 2):
        a.append([str(i), Paragraph(f"{'Nachtrag ' + n[3:]} (Angebot {ang} vom {dat}): {txt}", P), eur(net), eur(ust), eur(net + ust)])
    ab = w["abzug"]
    a.append(["", Paragraph("Summe Leistungen", P), eur(w["leist_netto"]), eur(w["leist_ust"]), eur(w["leist_brutto"])])
    a.append(["", Paragraph(ab["text"][0].upper() + ab["text"][1:], P), "-" + eur(ab["netto"]), "-" + eur(ab["ust"]), "-" + eur(ab["brutto"])])
    a.append(["", H("Gesamtleistung"), eur(w["ges_netto"]), eur(w["ges_ust"]), eur(w["ges_brutto"])])
    k = len(a) - 1
    E += [H("A. Gesamtleistung"), Spacer(1, 1.5*mm),
          tab(a, [10*mm, 100*mm, 21*mm, 18*mm, 21*mm], [("ALIGN", (2, 0), (-1, -1), "RIGHT"), ("LINEABOVE", (0, k - 2), (-1, k - 2), 0.5, GREY),
                                                        ("LINEABOVE", (0, k), (-1, k), 0.8, GREY), ("FONT", (2, k), (-1, k), "LB", 8)]),
          Spacer(1, 1.5*mm),
          Paragraph(f"Der Abzug ist pauschal mit {eur(ab['brutto'])} brutto vereinbart; Netto und Umsatzsteuer sind daraus herausgerechnet. "
                    "Dadurch kann die Umsatzsteuer der Gesamtleistung um 0,01 € von 19 % abweichen.", PS)]

    # B. Abzug der Abschlagsrechnungen
    from data_neubau import AR
    b = [["Rechnung", "Datum", "Rate", "netto", "USt. 19 %", "brutto"]]
    for nr, dat, rate, n, u, br, *_ in AR:
        b.append([nr, dat, Paragraph(rate, P), "-" + eur(n), "-" + eur(u), "-" + eur(br)])
    b.append(["", "", H("Summe Abschlagsrechnungen"), "-" + eur(w["ar_netto"]), "-" + eur(w["ar_ust"]), "-" + eur(w["ar_brutto"])])
    b.append(["", "", H("Restbetrag dieser Schlussrechnung"), eur(w["rest"]["netto"]), eur(w["rest"]["ust"]), eur(w["rest"]["brutto"])])
    k = len(b)
    E += [Spacer(1, 5*mm), H("B. Abzüglich Abschlagsrechnungen"), Spacer(1, 1.5*mm),
          tab(b, [17*mm, 19*mm, 71*mm, 22*mm, 19*mm, 22*mm],
              [("ALIGN", (3, 0), (-1, -1), "RIGHT"), ("LINEABOVE", (0, k-2), (-1, k-2), 0.5, GREY),
               ("LINEABOVE", (0, k-1), (-1, k-1), 0.8, GREY), ("FONT", (3, k-2), (-1, k-1), "LB", 8)]),
          Spacer(1, 1.5*mm),
          Paragraph("Der Restbetrag besteht aus der Schlussrate „Inbetriebnahme und Abnahme“ (15.000,00 € abzgl. 8. AR 11.000,00 € = 4.000,00 €) "
                    "und der Differenz zu Nachtrag 1 (freigegeben 6.188,00 €, mit der 6. AR abgerechnet 5.200,00 € = 988,00 €), "
                    f"abzüglich des pauschalen Abzugs von {eur(w['abzug']['brutto'])} (Teil A).", PS)]

    # C. Zahlungsaufstellung
    z = [["Rechnung", "brutto", "Bau-\numlage", "Sicherh.-\neinbehalt", "Skonto", "Bauabzug\n(Finanzamt)", "Zahlung", "Zahlungs-\ndatum", "offen"]]
    for r in w["zeilen"]:
        z.append([r["nr"], eur(r["brutto"]), eur(r["bu"]), eur(r["se"]), eur(r["skonto"]), eur(r["bauabzug"]),
                  eur(r["gezahlt"]), Paragraph(" + ".join(d for d, _ in r["zahlungen"]) or "–", PS), eur(r["offen"])])
    s = w["summen"]
    z.append([H("Summe"), eur(w["ar_brutto"]), eur(s["bu"]), eur(s["se"]), eur(s["skonto"]), eur(s["bauabzug"]),
              eur(s["gezahlt"]), "", eur(w["offen_ar"])])
    k = len(z) - 1
    secC = [Spacer(1, 5*mm), H("C. Zahlungsaufstellung"), Spacer(1, 1.5*mm),
            tab(z, [15*mm, 19*mm, 15*mm, 18*mm, 16*mm, 18*mm, 20*mm, 31*mm, 18*mm],
                [("ALIGN", (1, 0), (6, -1), "RIGHT"), ("ALIGN", (8, 0), (8, -1), "RIGHT"), ("LINEABOVE", (0, k), (-1, k), 0.8, GREY),
                 ("FONT", (1, k), (-1, k), "LB", 7.5)], font=7.5),
            Spacer(1, 1.5*mm),
            Paragraph("Abzüge wie von Ihnen vorgenommen: Bauumlage 0,25 % netto, Sicherheitseinbehalt 10 %, Skonto, Bauabzugsteuer 15 % "
                      "(nur 1.–3. AR; bei der 4. AR einbehalten und am 04.09.2025 erstattet). Die an das Finanzamt abgeführte Bauabzugsteuer "
                      "wird als Zahlung angerechnet.", PS)]
    E.append(KeepTogether(secC))

    # D. Offene Beträge: Restbetrag + offene 8. AR, Sicherheitseinbehalt separat obendrauf, dann alles zusammen
    se_liste = ", ".join(f"{r['nr']}: {eur(r['se'])}" for r in w["zeilen"] if r["se"])
    # Übersicht wie besprochen: erst alles Offene, dann der Pauschalabzug, dann der Zahlbetrag
    ab = w["abzug"]; vor = w["rest"]["brutto"] + ab["brutto"]
    o = [["", "brutto"],
         ["Restbetrag Schlussrate und Nachtrag 1 (Teil B vor Abzug)", eur(vor)],
         ["8. Abschlagsrechnung Nr. 2025-98 vom 16.12.2025 (nicht bezahlt)", eur(w["offen_ar"])],
         ["Zwischensumme offen", eur(vor + w["offen_ar"])],
         ["zzgl. Sicherheitseinbehalt 10 % aus der 1. bis 7. AR (siehe Anmerkung)", eur(s["se"])],
         ["Offen vor Abzug", eur(vor + w["offen_ar"] + s["se"])],
         [ab["text"][0].upper() + ab["text"][1:], "-" + eur(ab["brutto"])],
         ["Zahlbetrag gesamt", eur(w["gesamt_offen"])]]
    assert vor + w["offen_ar"] + s["se"] - ab["brutto"] == w["gesamt_offen"]
    secD = [Spacer(1, 5*mm), H("D. Offene Beträge"), Spacer(1, 1.5*mm),
            tab(o, [145*mm, 25*mm], [("ALIGN", (1, 0), (1, -1), "RIGHT"), ("LINEABOVE", (0, 3), (-1, 3), 0.5, GREY),
                                     ("FONT", (0, 3), (-1, 3), "LB", 8), ("LINEABOVE", (0, 5), (-1, 5), 0.5, GREY),
                                     ("FONT", (0, 5), (-1, 5), "LB", 8), ("LINEABOVE", (0, 7), (-1, 7), 0.8, GREY),
                                     ("FONT", (0, 7), (-1, 7), "LB", 8.5)]),
            Spacer(1, 1.5*mm),
            Paragraph(f"Der Abzug von {eur(ab['brutto'])} ist in Teil A von der Gesamtleistung abgezogen; der Restbetrag in Teil B "
                      f"({eur(w['rest']['brutto'])}) enthält ihn bereits.", PS),
            Spacer(1, 1.5*mm),
            Paragraph(f"Anmerkung zum Sicherheitseinbehalt: Von Ihren Zahlungen auf die 1. bis 7. Abschlagsrechnung haben Sie jeweils 10 % "
                      f"als Sicherheit einbehalten ({se_liste}), zusammen <b>{eur(s['se'])}</b>. Mit dieser Schlussrechnung bitten wir um "
                      "Auszahlung des Einbehalts.", PS),
            Spacer(1, 4*mm),
            Paragraph(f"Bitte überweisen Sie den Zahlbetrag von <b>{eur(w['gesamt_offen'])}</b> bis zum Fälligkeitsdatum unter Angabe der "
                      "Rechnungsnummer auf das unten genannte Konto.", P)]
    E.append(KeepTogether(secD))
    doc.build(E)
    return w

if __name__ == "__main__":
    w = build(sys.argv[1])
    print("Gesamtleistung", w["ges_brutto"], "| Rest SR", w["rest"]["brutto"], "| + 8. AR =", w["sofort"],
          "| + SE = Zahlbetrag gesamt", w["gesamt_offen"])
