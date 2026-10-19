"""Zwei getrennte Mappen (Villa 0200 und Neubau 19 a + b / 1150), je ein PDF mit Deckblatt, anklickbarem
Inhaltsverzeichnis und Lesezeichen: Abrechnung nach Gewerken, Schlussrechnung, Original-Belege,
Freistellungsbescheinigung § 48b, Fachunternehmererklärungen, Unternehmererklärung § 96 GEG,
Fachbauleitererklärung und Datenblätter (mit Übersicht, was vorliegt und was fehlt)."""
import os, sys, glob, re, tempfile
from decimal import Decimal as D
import pymupdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
import make_invoice_leans as inv
import make_invoice_leans_kumuliert as kum
import data, data_neubau
from data import r2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
V, N = "Villa_0200", "Neubau_19ab_1150"
FREISTELLUNG = "00_Freistellungsbescheinigung_48b_gueltig_2025-07-03_bis_2026-07-02.pdf"
STAND = "19.10.2026"
eur, num = inv.eur, inv.num

H1 = ParagraphStyle("h1", fontName="LB", fontSize=16, leading=20, textColor=inv.GREEN)
H2 = ParagraphStyle("h2", fontName="LB", fontSize=10.5, leading=13, spaceBefore=7, spaceAfter=3, textColor=inv.GREEN)
P = ParagraphStyle("p", fontName="L", fontSize=8.5, leading=11, textColor=inv.GREY)
PB = ParagraphStyle("pb", parent=P, fontName="LB")
PS = ParagraphStyle("ps", parent=P, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#666666"))
TP = ParagraphStyle("tp", parent=P, fontSize=8, leading=10)
TPB = ParagraphStyle("tpb", parent=TP, fontName="LB")
TPR, TPBR = ParagraphStyle("tpr", parent=TP, alignment=2), ParagraphStyle("tpbr", parent=TPB, alignment=2)
T1 = ParagraphStyle("t1", fontName="LB", fontSize=8.5, leading=11, textColor=inv.GREY)
T2 = ParagraphStyle("t2", fontName="L", fontSize=8, leading=10.2, textColor=inv.GREY)
OK, FEHLT = colors.HexColor("#E3F4E4"), colors.HexColor("#FFF4CE")

# ---------------------------------------------------------------- Tabellen-Helfer

def tabelle(rows, widths, rechts=(), fett=(), farben=None):
    """rows: Liste von Zeilen (erste = Kopf); rechts: Spalten rechtsbündig; fett: Zeilenindizes fett."""
    def zelle(i, j, v):
        b = i == 0 or i in fett
        return v if not isinstance(v, str) else Paragraph(v, (TPBR if b else TPR) if j in rechts else (TPB if b else TP))
    t = Table([[zelle(i, j, v) for j, v in enumerate(r)] for i, r in enumerate(rows)], colWidths=[w*mm for w in widths], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), inv.HEAD), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#BBBBBB")),
          ("TOPPADDING", (0, 0), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8)]
    for i in fett: st.append(("LINEABOVE", (0, i), (-1, i), 0.6, inv.GREY))
    for i, c in (farben or {}).items(): st.append(("BACKGROUND", (0, i), (-1, i), c))
    t.setStyle(TableStyle(st)); return t

def seite(c, doc):
    W, H = A4
    c.drawImage(os.path.join(os.path.dirname(__file__), inv.LOGO), W - 52*mm, H - 26*mm, width=34*mm, height=18*mm,
                mask="auto", preserveAspectRatio=True)
    c.setStrokeColor(inv.GREEN); c.setLineWidth(0.8); c.line(18*mm, 14*mm, W - 18*mm, 14*mm)
    c.setFont("L", 7); c.setFillColor(inv.GREY)
    c.drawString(18*mm, 10*mm, f"LEANS Tech GmbH · Berlepschstr. 165 · 14165 Berlin · Stand {STAND}")
    c.drawRightString(W - 18*mm, 10*mm, f"Seite {doc.page}")

def dokument(path, titel, flow):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=30*mm, bottomMargin=20*mm,
                            title=titel, author="LEANS Tech GmbH")
    doc.build(flow, onFirstPage=seite, onLaterPages=seite)

# ---------------------------------------------------------------- Abrechnung Villa

def abrechnung_villa(path):
    w = kum.werte(); g = kum.gruppen()
    anzahl = [len(rows) for *_, rows in g]
    vr = {v[0]: v for v in data.VORRECHNUNGEN}
    san = w["titel"][0] + w["titel"][1]; hz = w["titel"][2] + w["titel"][3]
    hz_netto = hz - w["nachlass"] - inv.ABZUG_NETTO
    assert san + hz_netto == w["netto"]
    gezahlt = vr["2024-47"][6] + vr["2025-17"][6]
    assert gezahlt + inv.REST_BRUTTO == w["brutto"]
    leistung = [
        ["Gewerk", "Leistung", "Beleg", "Pos.", "netto"],
        ["Sanitär", "Sanitärobjekte liefern und montieren, Armaturen montieren (DG, OG, EG, KG)", "RE 2024-47", str(anzahl[0]), eur(w["titel"][0])],
        ["Sanitär", "Sanitär-Nachtrag: Urinale, Badewanne, Küchenarmaturen, Waschbecken", "RE 2025-17", str(anzahl[1]), eur(w["titel"][1])],
        ["", "<b>Summe Sanitär</b>", "", "", f"<b>{eur(san)}</b>"],
        ["Heizung", "Hydraulischer Abgleich", "Dok. 159 → 2026-44", str(anzahl[2]), eur(w["titel"][2])],
        ["Heizung", "Fußbodenheizung KG, EG, OG (Bekotec EN FTS, Tackerplatte), Befüllung, Einregulierung, Aufheizen",
         "Dok. 176 → 2026-44", str(anzahl[3]), eur(w["titel"][3])],
        ["Heizung", "Nachlass: Heizung pauschal 20.000,00 € brutto (= 16.806,72 € netto)", "2026-44", "", eur(-w["nachlass"])],
        ["Heizung", "abzgl. Gasanschluss und Inbetriebnahme Trinkwasser (3.000,00 € brutto)", "2026-44", "", eur(-inv.ABZUG_NETTO)],
        ["", "<b>Summe Heizung</b>", "", "", f"<b>{eur(hz_netto)}</b>"],
        ["", "<b>Gesamtleistung Villa</b>", "", str(sum(anzahl)), f"<b>{eur(w['netto'])}</b>"],
        ["", "zzgl. Umsatzsteuer", "", "", eur(w["ust"])],
        ["", "<b>Gesamtleistung brutto</b>", "", "", f"<b>{eur(w['brutto'])}</b>"],
    ]
    rechnungen = [
        ["Rechnung", "Datum", "Gewerk", "netto", "brutto", "bezahlt", "offen"],
        ["RE 2024-47", vr["2024-47"][1], "Sanitär", eur(vr["2024-47"][4]), eur(vr["2024-47"][6]), "bezahlt (lt. Semir)", eur(0)],
        ["RE 2025-17", vr["2025-17"][1], "Sanitär-Nachtrag", eur(vr["2025-17"][4]), eur(vr["2025-17"][6]), "19.09.2025", eur(0)],
        ["SR 2026-44", STAND, "Heizung, kumuliert", eur(inv.REST_NETTO), eur(inv.REST_BRUTTO), "fällig 29.10.2026", eur(inv.REST_BRUTTO)],
        ["Summe", "", "", eur(w["netto"]), eur(w["brutto"]), eur(gezahlt), eur(inv.REST_BRUTTO)],
    ]
    ersetzt = [
        ["Beleg", "Datum", "Inhalt", "brutto", "Status"],
        ["Dok. 159", "03.12.2024", "Hydraulischer Abgleich (nur Angebotsnummer)", "321,30 €", "ersetzt durch SR 2026-44"],
        ["Dok. 176", "05.01.2025", "„Schlussrechnung“ Fußbodenheizung (nur Angebotsnummer)", "22.541,30 €", "ersetzt durch SR 2026-44"],
        ["NA 175 / Dok. 175", "05.01.2025", "Nachtragsangebot Sanitärobjekte", "6.669,95 €", "Angebot / Vorversion"],
        ["RE 2025-8", "28.03.2025", "Sanitär-Nachtrag (erste Fassung)", "6.669,95 €", "durch RE 2025-17 ersetzt – Storno ausstellen"],
    ]
    flow = [Paragraph("Abrechnung Villa – Liesborner Weg 19 (Projekt 0200)", H1), Spacer(1, 1*mm),
            Paragraph(f"Auftraggeber CREST Living GmbH &amp; Co. KG · Leistungszeitraum {inv.LEISTUNGSZEITRAUM} · "
                      f"Gewerke Sanitär und Heizung · Stand {STAND}", P),
            Paragraph("1. Was abgerechnet wurde – nach Gewerken", H2),
            tabelle(leistung, [17, 90, 31, 12, 24], rechts=(3, 4), fett=(3, 8, 9, 11)),
            Paragraph("2. Rechnungen und Zahlungen", H2),
            tabelle(rechnungen, [22, 21, 28, 23, 24, 32, 24], rechts=(3, 4, 6), fett=(4,), farben={3: FEHLT}),
            Spacer(1, 1.5*mm),
            Paragraph("Netto und Umsatzsteuer der Schlussrechnung sind aus der Bruttopauschale herausgerechnet; die Umsatzsteuer "
                      "der Gesamtleistung weicht deshalb um 0,01 € von 19 % ab. RE 2024-47: Zahlung laut Semir erfolgt, Datum mangels "
                      "Kontoauszug 04–07/2024 nicht belegt.", PS),
            Paragraph("3. Ersetzte und zu stornierende Belege", H2),
            tabelle(ersetzt, [28, 21, 60, 22, 43], rechts=(3,))]
    dokument(path, "Abrechnung Villa Liesborner Weg 19", flow)

# ---------------------------------------------------------------- Abrechnung Neubau

GEWERKE = ["Klima", "Lüftung", "Heizung inkl. Wärmepumpe und FBH", "Sanitär", "Diverses"]

def angebot_gewerke(pfad):
    """Brutto je Gewerk aus den Zwischensummen des Angebots-PDFs (Reihenfolge wie GEWERKE) und Gesamtbetrag."""
    t = "\n".join(p.get_text() for p in pymupdf.open(pfad)).replace("\xa0", " ")
    betrag = lambda s: D(s.replace(".", "").replace(",", ".").replace(" €", "").strip())
    zs = [betrag(m.group(2)) for m in re.finditer(r"Zwischensumme\n([\d.,]+ €)\n([\d.,]+ €)", t)]
    gesamt = betrag(re.search(r"([\d.,]+ €)\nNettobetrag", t).group(1))
    assert len(zs) == len(GEWERKE) and sum(zs) == gesamt, (pfad, zs, gesamt)
    return zs, gesamt

def anteilig(betraege, ziel):
    """Ziel rechnerisch im Verhältnis der Beträge aufteilen; Rundungsrest auf den größten Posten."""
    s = sum(betraege); a = [r2(b * ziel / s) for b in betraege]
    a[a.index(max(a))] += ziel - sum(a); return a

def abrechnung_neubau(path):
    a_hz, a_sum = angebot_gewerke(glob.glob(os.path.join(ROOT, N, "2_Angebote_Endstand", "*ANGEBOT-233*.pdf"))[0])
    b_hz, b_sum = angebot_gewerke(glob.glob(os.path.join(ROOT, N, "2_Angebote_Endstand", "*ANGEBOT-234*.pdf"))[0])
    zus = [x + y for x, y in zip(a_hz, b_hz)]
    pa = anteilig(zus, data_neubau.PAUSCHALE_BRUTTO)
    haus = anteilig([a_sum, b_sum], data_neubau.PAUSCHALE_BRUTTO)
    w = data_neubau.werte(); s = w["summen"]
    gewerk = [["Gewerk", "Haus A (19 a)<br/>Angebot 233", "Haus B (19 b)<br/>Angebot 234", "zusammen", "Pauschale<br/>anteilig"]]
    gewerk += [[g, eur(x), eur(y), eur(z), eur(p)] for g, x, y, z, p in zip(GEWERKE, a_hz, b_hz, zus, pa)]
    gewerk += [["<b>Summe</b>", f"<b>{eur(a_sum)}</b>", f"<b>{eur(b_sum)}</b>", f"<b>{eur(a_sum + b_sum)}</b>",
                f"<b>{eur(data_neubau.PAUSCHALE_BRUTTO)}</b>"],
               ["Pauschale anteilig je Haus", eur(haus[0]), eur(haus[1]), "", eur(sum(haus))]]
    na = [["Nachtrag", "Angebot", "Inhalt", "netto", "USt", "brutto"]]
    na += [[n, a, t.split(" (freigegeben")[0], eur(net), eur(u), eur(net + u)] for n, a, d, t, net, u in w["na"]]
    gl = [["Gesamtleistung beide Häuser", "netto", "USt", "brutto"],
          ["Pauschale laut Bauvertrag HLS (Anlage 1 vom 15.05.2025)", eur(w["p_netto"]), eur(w["p_ust"]), eur(data_neubau.PAUSCHALE_BRUTTO)],
          ["Nachträge 1 und 2", eur(sum(x[4] for x in w["na"])), eur(sum(x[5] for x in w["na"])), eur(sum(x[4] + x[5] for x in w["na"]))],
          ["<b>Gesamtleistung</b>", f"<b>{eur(w['ges_netto'])}</b>", f"<b>{eur(w['ges_ust'])}</b>", f"<b>{eur(w['ges_brutto'])}</b>"]]
    ar = [["Rechnung", "Datum", "Rate", "brutto", "Einbehalte¹", "gezahlt", "offen"]]
    for z in w["zeilen"]:
        einb = z["bu"] + z["se"] + z["skonto"] + z["bauabzug"]
        ar.append([z["nr"], z["datum"], z["rate"].split(" – ")[1], eur(z["brutto"]), eur(einb), eur(z["gezahlt"]), eur(z["offen"])])
    einb_sum = s["bu"] + s["se"] + s["skonto"] + s["bauabzug"]
    ar.append(["Summe", "", "", eur(w["ar_brutto"]), eur(einb_sum), eur(s["gezahlt"]), eur(w["offen_ar"])])
    sr = [["Schlussrechnung Nr. 2026-45 vom " + STAND, "brutto"],
          ["Gesamtleistung", eur(w["ges_brutto"])], ["abzgl. 8 Abschlagsrechnungen", eur(-w["ar_brutto"])],
          ["Restbetrag Schlussrechnung", eur(w["rest"]["brutto"])], ["8. AR 2025-98 (nicht bezahlt)", eur(w["offen_ar"])],
          ["Sicherheitseinbehalt 10 % (1. bis 7. AR)", eur(s["se"])], ["<b>Zahlbetrag, fällig 29.10.2026</b>", f"<b>{eur(w['gesamt_offen'])}</b>"]]
    bilanz = [["Wohin die Gesamtleistung von " + eur(w["ges_brutto"]) + " gegangen ist", "brutto"],
              ["an LEANS gezahlt", eur(s["gezahlt"])], ["Bauabzugsteuer 15 % – von CREST ans Finanzamt abgeführt (gilt als gezahlt)", eur(s["bauabzug"])],
              ["Skonto – akzeptiert, wird nicht zurückgefordert", eur(s["skonto"])], ["Bauumlage 0,25 % – akzeptiert", eur(s["bu"])],
              ["<b>offen laut Schlussrechnung 2026-45</b>", f"<b>{eur(w['gesamt_offen'])}</b>"]]
    assert s["gezahlt"] + s["bauabzug"] + s["skonto"] + s["bu"] + w["gesamt_offen"] == w["ges_brutto"]
    flow = [Paragraph("Abrechnung Neubau 19 a + b – Butterfly Houses (Projekt 1150)", H1), Spacer(1, 1*mm),
            Paragraph(f"Auftraggeber CREST Living GmbH &amp; Co. KG · Auftrag 20250418_# · Pauschalvertrag für beide Häuser · "
                      f"Gewerke Klima, Lüftung, Heizung inkl. Wärmepumpe und FBH, Sanitär · Stand {STAND}", P),
            Paragraph("1. Leistung je Haus und Gewerk (brutto)", H2),
            tabelle(gewerk, [52, 30, 30, 30, 32], rechts=(1, 2, 3, 4), fett=(6,)),
            Spacer(1, 1.5*mm),
            Paragraph("Beauftragt wurde eine gemeinsame Pauschale von 300.000,00 € brutto für beide Häuser. Die Spalte „Pauschale anteilig“ "
                      "und die Aufteilung je Haus sind rechnerisch im Verhältnis der Angebote ermittelt; abgerechnet wurde nach Bauphasen "
                      "(Abschlagsrechnungen unten), nicht nach Haus oder Gewerk.", PS),
            Paragraph("2. Nachträge und Gesamtleistung", H2),
            tabelle(na, [19, 17, 77, 21, 19, 21], rechts=(3, 4, 5)), Spacer(1, 2*mm),
            tabelle(gl, [97, 24, 24, 29], rechts=(1, 2, 3), fett=(3,)),
            Paragraph("3. Abschlagsrechnungen und Zahlungen", H2),
            tabelle(ar, [19, 20, 50, 22, 21, 22, 20], rechts=(3, 4, 5, 6), fett=(9,), farben={8: FEHLT}),
            Spacer(1, 1.5*mm),
            Paragraph(f"¹ Einbehalte wie von CREST vorgenommen: Bauumlage {eur(s['bu'])}, Sicherheitseinbehalt {eur(s['se'])}, "
                      f"Skonto {eur(s['skonto'])}, Bauabzugsteuer {eur(s['bauabzug'])} (1.–3. AR; bei der 4. AR einbehalten und am "
                      "04.09.2025 erstattet). Alle Zahlungen stimmen auf den Cent mit dem Kontoauszug überein.", PS),
            KeepTogether([Paragraph("4. Schlussrechnung und Stand", H2),
                          Table([[tabelle(sr, [60, 24], rechts=(1,), fett=(6,), farben={6: FEHLT}),
                                  tabelle(bilanz, [62, 24], rechts=(1,), fett=(5,))]],
                                colWidths=[88*mm, 86*mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0)])])]
    dokument(path, "Abrechnung Neubau Liesborner Weg 19 a + b", flow)

# ---------------------------------------------------------------- Datenblatt-Übersicht

DB_VILLA = [
    ("Sanitär", "Duravit ME by Starck Urinal (OG, EG, KG)", f"{V}/5_Datenblaetter/1_Sanitaer/Duravit_ME_by_Starck_Urinal_2809302000.pdf",
     "Produktseite Duravit 2809302000 (weiß Hochglanz); Ausführung weiß matt im OG abgleichen"),
    ("Sanitär", "Geberit iCon Wand-Tiefspül-WC mit WC-Sitz (8 Stück)", None, ""),
    ("Sanitär", "Villeroy & Boch Subway 3.0 Badewanne", None, ""),
    ("Sanitär", "Wandwaschbecken TWG71 und PB2035, Mineralguss weiß matt", None, ""),
    ("Sanitär", "Laufen Handwaschbecken ohne Hahnloch", None, ""),
    ("Sanitär", "Geberit Duschrinne (OG)", None, ""),
    ("Heizung", "Schlüter Bekotec EN FTS (EG, OG)", None, ""),
    ("Heizung", "Tackerplatte mit Unterdämmung „Ratiodämm“ (KG)", None, ""),
]
DB_NEUBAU = [
    ("Klima", "Mitsubishi Heavy Außengerät SRC60ZSX-W3", f"{N}/7_Datenblaetter/1_Klima/MHI_Aussengeraet_SRC60ZSX-W3.pdf",
     "laut S-Klima-Angebot 200118621 vom 21.05.2025 (Angebot 233/234 nannte SCM 60 ZS-W) – Typenschild abgleichen"),
    ("Klima", "Mitsubishi Heavy Kanalgerät FDUM60VH", f"{N}/7_Datenblaetter/1_Klima/MHI_Kanalgeraet_FDUM60VH.pdf",
     "laut S-Klima-Angebot 200118621 (Bestellmail nennt FDUT56KXE6F-E) – Typenschild abgleichen"),
    ("Klima", "Kabelfernbedienung RC-EX3A / RC-ES1", None, ""),
    ("Lüftung", "Helios ELS EC 60/45/25 F mit Unterputzgehäuse", None, ""),
    ("Lüftung", "LUNOS Außenwand-Luftdurchlass ALD-R 160", None, ""),
    ("Lüftung", "Brandschutz-Deckenschott DN 160 (mit Zulassung)", None, ""),
    ("Heizung", "Samsung EHS Mono HT R290, Außeneinheit AE160CXYDGK (16 kW)",
     f"{N}/7_Datenblaetter/3_Heizung/Samsung_Waermepumpe_AE160CXYDGK_Mono-HT_R290_Technische_Info.pdf", "Technische Info"),
    ("Heizung", "Samsung Anlagenkonfiguration Haus A (19 a)", f"{N}/7_Datenblaetter/3_Heizung/Samsung_Anlagenkonfiguration_Haus_A_19a.pdf",
     "Hydraulikschema vom 20.05.2025"),
    ("Heizung", "Samsung Anlagenkonfiguration Haus B (19 b)", f"{N}/7_Datenblaetter/3_Heizung/Samsung_Anlagenkonfiguration_Haus_B_19b.pdf",
     "Hydraulikschema vom 20.05.2025"),
    ("Heizung", "Danfoss Unterputzkasten EvoFlat 145H4908 / 145H4909",
     f"{N}/7_Datenblaetter/3_Heizung/Danfoss_EvoFlat_Unterputzkasten_145H4908_145H4909.pdf", "Katalogseite"),
    ("Heizung", "Danfoss Trinkwarmwasserstation (Wohnungsstation)", None, ""),
    ("Heizung", "Pufferspeicher 800 l, REHAU PE-Xa 16 × 1,5, Edelstahlrohr Temponox", None, ""),
    ("Sanitär", "Dallmer Duschrinne CeraLine Plan W 900, DN 50",
     f"{N}/7_Datenblaetter/4_Sanitaer/Dallmer_Duschrinne_CeraLine_Plan_W_900_DN50.pdf", "Angebot 233/234 nannte CeraLine Nano W 1000"),
    ("Sanitär", "Dallmer Duschrinne CeraLine Plan W 1200, DN 50",
     f"{N}/7_Datenblaetter/4_Sanitaer/Dallmer_Duschrinne_CeraLine_Plan_W_1200_DN50.pdf", ""),
    ("Sanitär", "Dallmer Abdeckung CeraLine Individual 900", f"{N}/7_Datenblaetter/4_Sanitaer/Dallmer_Abdeckung_CeraLine_Individual_900.pdf", ""),
    ("Sanitär", "Dallmer Abdeckung CeraLine Individual 1200", f"{N}/7_Datenblaetter/4_Sanitaer/Dallmer_Abdeckung_CeraLine_Individual_1200.pdf", ""),
    ("Sanitär", "Geberit Silent-PP Abwasserrohr", f"{N}/7_Datenblaetter/4_Sanitaer/Geberit_Silent-PP_Produktdatenblatt.pdf",
     "allgemeines Produktdatenblatt"),
    ("Sanitär", "Geberit iCon WC, Sigma-Montageelemente, Betätigungsplatte Sigma01", None, ""),
    ("Sanitär", "hansgrohe Vernis Shape, ShowerSelect S, iBox, Croma Select S", None, ""),
    ("Sanitär", "BWT Enthärter Rondomat Duo, Kemper Außenarmatur, Rückspülfilter", None, ""),
    ("Sanitär", "Freistehende Badewannen LISBON (Welt der Bäder, 4 Stück)", None, ""),
]

def datenblatt_uebersicht(path, titel, liste):
    rows = [["Gewerk", "Produkt laut Rechnung / Angebot", "Datenblatt", "Hinweis"]]
    farben = {}
    for i, (g, prod, pfad, hinweis) in enumerate(liste, 1):
        rows.append([g, prod, "liegt bei" if pfad else "fehlt", hinweis or ("" if pfad else "beim Hersteller herunterladen")])
        farben[i] = OK if pfad else FEHLT
    vorhanden = sum(1 for x in liste if x[2])
    flow = [Paragraph(titel, H1), Spacer(1, 1*mm),
            Paragraph(f"{vorhanden} von {len(liste)} Produkten haben ein Datenblatt in Drive; sie liegen in dieser Mappe direkt dahinter. "
                      "Die gelb markierten fehlen in Drive und müssen beim Hersteller heruntergeladen werden (Internetzugriff war "
                      "hier gesperrt).", P), Spacer(1, 3*mm),
            tabelle(rows, [18, 72, 20, 64], farben=farben)]
    dokument(path, titel, flow)
    return [(g, prod, pfad) for g, prod, pfad, _ in liste if pfad]

# ---------------------------------------------------------------- Mappe zusammenbauen

def trennblatt(path, titel, unter):
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=105*mm)
    doc.build([Paragraph(titel, ParagraphStyle("x", parent=H1, fontSize=22, leading=28, alignment=1)), Spacer(1, 6*mm),
               Paragraph(unter, ParagraphStyle("y", parent=P, fontSize=10.5, leading=15, alignment=1))])

def deckblatt(path, titel, unter, hinweis, e, seiten):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=14*mm)
    rows = [[Paragraph(x[1], T1 if x[0] == 1 else T2), Paragraph(x[2], T1 if x[0] == 1 else T2), Paragraph(str(seiten.get(i, "")), T2)]
            for i, x in enumerate(e)]
    t = Table(rows, colWidths=[12*mm, 148*mm, 14*mm])
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (2, 0), (2, -1), "RIGHT"),
          ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
          ("LINEBELOW", (0, 0), (-1, -1), 0.2, colors.HexColor("#DDDDDD"))]
    st += [("BACKGROUND", (0, i), (-1, i), inv.HEAD) for i, x in enumerate(e) if x[0] == 1]
    t.setStyle(TableStyle(st))
    doc.build([Paragraph(titel, ParagraphStyle("d", parent=H1, fontSize=18, leading=23)), Spacer(1, 2*mm), Paragraph(unter, P),
               Spacer(1, 2*mm), Paragraph(hinweis, P), Spacer(1, 4*mm), t])

def mappe(out, titel, unter, hinweis, e):
    """e: [(Ebene, Kürzel, Titel, Quelle)], Quelle = Pfad relativ zu ROOT, ('#trenn', Untertitel) oder ('#pdf', Pfad, Erzeuger)."""
    tmp = tempfile.mkdtemp(); docs = []
    for i, (lvl, kz, tit, src) in enumerate(e):
        if isinstance(src, tuple) and src[0] == "#trenn":
            p = os.path.join(tmp, f"t{i}.pdf"); trennblatt(p, f"{kz} · {tit}", src[1])
        elif isinstance(src, tuple):
            p = os.path.join(tmp, f"g{i}.pdf"); src[1](p)
        else:
            p = os.path.join(ROOT, src); assert os.path.exists(p), p
        docs.append(pymupdf.open(p))
    cover = os.path.join(tmp, "cover.pdf"); deckblatt(cover, titel, unter, hinweis, e, {}); n_cover = pymupdf.open(cover).page_count
    seiten, s = {}, n_cover + 1
    for i, d in enumerate(docs): seiten[i] = s; s += d.page_count
    deckblatt(cover, titel, unter, hinweis, e, seiten); assert pymupdf.open(cover).page_count == n_cover
    m = pymupdf.open(cover)
    for d in docs: m.insert_pdf(d)
    # Inhaltsverzeichnis anklickbar: Einträge der Reihe nach suchen (gleiche Titel können mehrfach vorkommen)
    pos = (0, -1.0)
    for i, (lvl, kz, tit, src) in enumerate(e):
        treffer = sorted(((pno, h) for pno in range(n_cover) for h in m[pno].search_for(tit[:60])), key=lambda x: (x[0], x[1].y0))
        treffer = [(pno, h) for pno, h in treffer if (pno, h.y0) > pos]
        if not treffer: raise AssertionError(f"TOC-Eintrag nicht gefunden: {tit[:60]}")
        pno, r = treffer[0]; pos = (pno, r.y0)
        r = pymupdf.Rect(15*mm*72/25.4, r.y0 - 1, m[pno].rect.width - 15*mm*72/25.4, r.y1 + 1)
        m[pno].insert_link({"kind": pymupdf.LINK_GOTO, "from": r, "page": seiten[i] - 1})
    m.set_toc([[1, "Deckblatt und Inhaltsverzeichnis", 1]] + [[lvl, (kz + " · " if kz else "") + tit, seiten[i]] for i, (lvl, kz, tit, _) in enumerate(e)])
    m.set_metadata({"title": titel, "author": "LEANS Tech GmbH"})
    m.save(out, garbage=3, deflate=True)
    return m.page_count, len(e)

FREI_TEXT = ("Gültig vom 03.07.2025 bis 02.07.2026 – <b>abgelaufen</b>. Eine neue Bescheinigung beim FA für Körperschaften III "
             "beantragen und nachreichen. Ohne gültige Bescheinigung behält CREST 15 % Bauabzugsteuer ein und führt sie ans Finanzamt ab")

def eintraege_villa():
    o = lambda f: os.path.join(V, "1_Belege_Original", f)
    e = [(1, "1", "Abrechnung nach Gewerken", ("#trenn", "Was bei der Villa abgerechnet wurde: Sanitär und Heizung, Rechnungen, Zahlungen, ersetzte Belege")),
         (2, "1.1", "Abrechnung Villa – Gewerke, Rechnungen und Zahlungen", ("#pdf", abrechnung_villa)),
         (1, "2", "Schlussrechnung", ("#trenn", "Kumulierte Schlussrechnung über alle Villa-Leistungen")),
         (2, "2.1", "Schlussrechnung Nr. 2026-44 vom 19.10.2026 – Zahlbetrag 17.000,00 € brutto",
          f"{V}/2_Schlussrechnung/Schlussrechnung_2026-44_Villa_kumuliert_17.000_brutto.pdf"),
         (1, "3", "Rechnungen und Belege (Originale)", ("#trenn", "Alle bisherigen Villa-Belege, einheitlich benannt mit Status"))]
    for i, f in enumerate(sorted(os.listdir(os.path.join(ROOT, V, "1_Belege_Original"))), 1):
        e.append((2, f"3.{i}", os.path.splitext(f)[0][3:].replace("_", " "), o(f)))
    e += [(1, "4", "Freistellungsbescheinigung § 48b EStG", ("#trenn", FREI_TEXT + " (bei 2026-44: 2.550,00 €).")),
          (2, "4.1", "Freistellungsbescheinigung Finanzamt für Körperschaften III vom 03.07.2025", FREISTELLUNG),
          (1, "5", "Fachunternehmererklärungen", ("#trenn", "Je Gewerk – Datum, Unterschrift und Stempel setzt Semir Redzic")),
          (2, "5.1", "Fachunternehmererklärung Heizung (Fußbodenheizung, hydraulischer Abgleich)",
           f"{V}/4_Fachunternehmererklaerungen/FUE_Villa_Heizung_Fussbodenheizung.pdf"),
          (2, "5.2", "Fachunternehmererklärung Sanitär", f"{V}/4_Fachunternehmererklaerungen/FUE_Villa_Sanitaer.pdf"),
          (1, "6", "Unternehmererklärung § 96 GEG", ("#trenn", "Bestätigung an den Eigentümer, dass die Heizungsarbeiten dem Gebäudeenergiegesetz entsprechen")),
          (2, "6.1", "Unternehmererklärung nach § 96 GEG – Heizung Villa", f"{V}/4_Fachunternehmererklaerungen/Unternehmererklaerung_GEG_Villa.pdf"),
          (1, "7", "Fachbauleitererklärung", ("#trenn", "Fachbauleitung TGA – ausgeführte Prüfungen und Arbeiten")),
          (2, "7.1", "Fachbauleitererklärung TGA – Heizung und Sanitär Villa", f"{V}/4_Fachunternehmererklaerungen/Fachbauleitererklaerung_Villa.pdf"),
          (1, "8", "Datenblätter", ("#trenn", "Übersicht der verbauten Produkte und vorhandene Datenblätter")),
          (2, "8.1", "Datenblatt-Übersicht Villa – vorhanden und fehlend", ("#pdf", lambda p: datenblatt_uebersicht(p, "Datenblätter Villa – Liesborner Weg 19", DB_VILLA)))]
    for i, (g, prod, pfad) in enumerate([x[:3] for x in DB_VILLA if x[2]], 2):
        e.append((2, f"8.{i}", f"Datenblatt {g}: {prod}", pfad))
    return e

def eintraege_neubau():
    e = [(1, "1", "Abrechnung nach Gewerken – Haus A und Haus B", ("#trenn", "Was beim Neubau abgerechnet wurde: Gewerke je Haus, Nachträge, Abschlagsrechnungen, Zahlungen, Schlussrechnung")),
         (2, "1.1", "Abrechnung Neubau 19 a + b – Häuser, Gewerke, Rechnungen und Zahlungen", ("#pdf", abrechnung_neubau)),
         (1, "2", "Schlussrechnung", ("#trenn", "Kumulierte Schlussrechnung für beide Häuser mit Zahlungsaufstellung und Sicherheitseinbehalt")),
         (2, "2.1", "Schlussrechnung Nr. 2026-45 vom 19.10.2026 – Zahlbetrag 45.745,31 €",
          f"{N}/5_Schlussrechnung/Schlussrechnung_2026-45_Neubau_19ab_45.745,31.pdf"),
         (1, "3", "Auftrag, Angebote, Nachträge und Abschlagsrechnungen", ("#trenn", "Originale: Zahlungsplan, Angebote 233 (Haus A) und 234 (Haus B), Nachträge, 8 Abschlagsrechnungen mit CREST-Prüfblatt"))]
    k = 1
    for ordner, praefix in (("1_Auftrag", "Auftrag: "), ("2_Angebote_Endstand", "Angebot: "), ("3_Nachtraege", "Nachtrag: "), ("4_Rechnungen", "Rechnung: ")):
        for f in sorted(glob.glob(os.path.join(ROOT, N, ordner, "*.pdf"))):
            e.append((2, f"3.{k}", praefix + os.path.basename(f)[:-4].replace("_", " "), os.path.relpath(f, ROOT))); k += 1
    e += [(1, "4", "Freistellungsbescheinigung § 48b EStG", ("#trenn", FREI_TEXT + " (bei 2026-45: 6.861,80 €).")),
          (2, "4.1", "Freistellungsbescheinigung Finanzamt für Körperschaften III vom 03.07.2025", FREISTELLUNG),
          (1, "5", "Fachunternehmererklärungen", ("#trenn", "Je Gewerk – Datum, Unterschrift und Stempel setzt Semir Redzic"))]
    for i, (t, d) in enumerate([("Klima", "Klima"), ("Lüftung", "Lueftung"), ("Heizung inkl. Wärmepumpe und Fußbodenheizung", "Heizung"), ("Sanitär", "Sanitaer")], 1):
        e.append((2, f"5.{i}", f"Fachunternehmererklärung {t}", f"{N}/6_Fachunternehmererklaerungen/FUE_Neubau_19ab_{d}.pdf"))
    e += [(1, "6", "Unternehmererklärung § 96 GEG", ("#trenn", "Bestätigung an den Eigentümer, dass Heizung, Lüftung und Klima dem Gebäudeenergiegesetz entsprechen")),
          (2, "6.1", "Unternehmererklärung nach § 96 GEG – Neubau 19 a + b", f"{N}/6_Fachunternehmererklaerungen/Unternehmererklaerung_GEG_Neubau_19ab.pdf"),
          (1, "7", "Fachbauleitererklärung", ("#trenn", "Fachbauleitung TGA – ausgeführte Prüfungen und Arbeiten")),
          (2, "7.1", "Fachbauleitererklärung TGA – Klima, Lüftung, Heizung, Sanitär", f"{N}/6_Fachunternehmererklaerungen/Fachbauleitererklaerung_Neubau_19ab.pdf"),
          (1, "8", "Datenblätter", ("#trenn", "Übersicht der verbauten Produkte je Gewerk und vorhandene Datenblätter")),
          (2, "8.1", "Datenblatt-Übersicht Neubau – vorhanden und fehlend",
           ("#pdf", lambda p: datenblatt_uebersicht(p, "Datenblätter Neubau – Liesborner Weg 19 a + b", DB_NEUBAU)))]
    for i, (g, prod, pfad) in enumerate([x[:3] for x in DB_NEUBAU if x[2]], 2):
        e.append((2, f"8.{i}", f"Datenblatt {g}: {prod}", pfad))
    return e

HINWEIS = ("<b>Inhalt:</b> Abrechnung, Schlussrechnung, Belege, Freistellungsbescheinigung, Erklärungen und Datenblätter. "
           "Die Erklärungen sind fertig vorbereitet; es fehlen nur Datum, Unterschrift und Stempel von Semir Redzic. "
           "Einträge im Inhaltsverzeichnis sind anklickbar; die Lesezeichen im PDF-Viewer führen ebenfalls zu jedem Dokument.")
MAPPEN = [
    (f"{V}/00_Mappe_Villa_0200_Abrechnung_und_Dokumentation.pdf", "Mappe Villa – BV Liesborner Weg 19, 13507 Berlin",
     f"Projekt 0200 · Auftraggeber CREST Living GmbH &amp; Co. KG · Gewerke Sanitär und Heizung · LEANS Tech GmbH · Stand {STAND}",
     eintraege_villa),
    (f"{N}/00_Mappe_Neubau_19ab_1150_Abrechnung_und_Dokumentation.pdf", "Mappe Neubau – Butterfly Houses, Liesborner Weg 19 a + b",
     f"Projekt 1150 · Auftrag 20250418_# · Auftraggeber CREST Living GmbH &amp; Co. KG · Haus A (19 a) und Haus B (19 b) · "
     f"Gewerke Klima, Lüftung, Heizung, Sanitär · LEANS Tech GmbH · Stand {STAND}", eintraege_neubau),
]

def dateiname(kz, titel):
    t = re.sub(r"\s+", " ", titel.replace(":", " –").replace("/", "-").replace("→", "-").replace("€", "EUR")).strip()
    if "." in kz: kz = "{}.{:02d}".format(*map(int, kz.split(".")))   # 3.02 vor 3.10 sortieren
    return f"{kz} {t}"[:110].rstrip(" .–-")

def ordner(ziel, gesamt, e, name_gesamt):
    """Dieselben Inhalte als normale Ordner: je Abschnitt ein Unterordner, je Dokument eine nummerierte PDF-Datei."""
    import shutil
    if os.path.exists(ziel): shutil.rmtree(ziel)
    os.makedirs(ziel); shutil.copy(gesamt, os.path.join(ziel, name_gesamt)); sub = ziel; n = 1
    for lvl, kz, tit, src in e:
        if lvl == 1:
            sub = os.path.join(ziel, dateiname(kz, tit)); os.makedirs(sub); continue
        p = os.path.join(sub, dateiname(kz, tit) + ".pdf")
        src[1](p) if isinstance(src, tuple) else shutil.copy(os.path.join(ROOT, src), p); n += 1
    return n

ORDNERNAME = {V: "Villa Liesborner Weg 19 (0200)", N: "Neubau Liesborner Weg 19 a+b (1150)"}

def build(ordner_ziel=None):
    res = []
    for out, titel, unter, f in MAPPEN:
        e = f(); res.append((out, mappe(os.path.join(ROOT, out), titel, unter, HINWEIS, e)))
        if ordner_ziel:
            name = ORDNERNAME[out.split("/")[0]]
            ordner(os.path.join(ordner_ziel, name), os.path.join(ROOT, out), e, f"00 Gesamtmappe {name} – alles in einer Datei.pdf")
    return res

if __name__ == "__main__":
    # optional: Zielordner für die Einzel-PDFs (normale Ordnerstruktur zum Durchsehen)
    for out, (seiten, eintraege) in build(sys.argv[1] if len(sys.argv) > 1 else None):
        print(f"{out}: {seiten} Seiten, {eintraege} Einträge")
