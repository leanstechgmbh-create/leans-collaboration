"""Übersicht Liesborner Weg 19: Villa (0200) und Neubau 19 a+b (1150) – Stand 29.09.2026."""
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
import make_invoice_leans as inv   # Fonts L / LB, Farben

P  = ParagraphStyle("p", fontName="L", fontSize=8, leading=10)
PB = ParagraphStyle("pb", parent=P, fontName="LB")
H1 = ParagraphStyle("h1", fontName="LB", fontSize=15, leading=19, textColor=inv.GREEN)
H2 = ParagraphStyle("h2", fontName="LB", fontSize=11, leading=14, spaceBefore=6, spaceAfter=3, textColor=inv.GREEN)
H3 = ParagraphStyle("h3", fontName="LB", fontSize=9, leading=12, spaceBefore=4, spaceAfter=2)
RED, AMB, GRN = colors.HexColor("#FDE2E1"), colors.HexColor("#FFF4CE"), colors.HexColor("#E3F4E4")

def tab(rows, widths, colour=None, right=()):
    PR = ParagraphStyle("pr", parent=P, alignment=2); PBR = ParagraphStyle("pbr", parent=PB, alignment=2)
    data = [[Paragraph(str(c), (PBR if j in right else PB) if i == 0 else (PR if j in right else P)) for j, c in enumerate(r)] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w*mm for w in widths], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), inv.HEAD), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#BBBBBB")),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    for c in right: st.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    for i, col in (colour or {}).items(): st.append(("BACKGROUND", (0, i), (-1, i), col))
    t.setStyle(TableStyle(st)); return t

def build(out):
    doc = SimpleDocTemplate(out, pagesize=landscape(A4), leftMargin=12*mm, rightMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm,
                            title="Übersicht Liesborner Weg 19 – Villa und Neubau 19 a+b", author="LEANS Tech GmbH")
    E = [Paragraph("Übersicht Liesborner Weg 19, 13507 Berlin – Stand 29.09.2026", H1),
         Paragraph("Zwei getrennte Bauvorhaben, beide für <b>CREST Living GmbH &amp; Co. KG</b>. Achtung: Alle CREST-Firmen haben ihren Sitz am Liesborner Weg 19 – "
                   "die Adresse allein sagt nichts über die Baustelle. Maßgeblich ist die Zeile „BV:“ auf dem Beleg. "
                   "Zahlungen laut Kontoauszügen 02/2024, 08–09/2024 und 01/2025–04/2026 (übrige Monate fehlen in Drive).", P),
         Spacer(1, 3*mm),
         tab([["", "Villa (Bestand) – Projekt 0200 „ALT“", "Neubau Butterfly Houses 19 a + b – Projekt 1150 „NEU“"],
              ["Zeitraum", "Nov. 2023 – Dez. 2024 (Rechnungen bis Apr. 2025)", "Mai 2025 – Dez. 2025 (laufend)"],
              ["Auftrag", "kein schriftlicher Auftrag in Drive; Beauftragung über CREST-Baustellenprotokolle + Nachtragsangebot 175",
               "Bauvertrag HLS, Anlage 1 Zahlungsplan vom 15.05.2025: Pauschal 300.000,00 € brutto (unterschriebener Vertrag nicht in Drive)"],
              ["Gewerke", "Sanitärobjekte/Armaturen, Heizung (Fußbodenheizung, hydraulischer Abgleich)", "Klima, Lüftung, Heizung inkl. Wärmepumpe + FBH, Sanitär – je Haus"],
              ["Abgerechnet (brutto)", "gültig: 20.514,41 € (RE 2024-47, 2025-17); ungültig/ohne Nr.: 22.862,60 € (Dok. 159, 176)", "309.318,89 € (8 Rechnungen inkl. Nachtrag)"],
              ["Offen", "Dok. 159 + 176 = 22.862,60 € → neue Schlussrechnung 20.000 € netto / 23.800 € brutto", "8. AR 11.000 €, Restrate 4.000 €, Sicherheitseinbehalte, Schlussrechnung"]],
             [30, 118, 125]),
         Paragraph("1. Villa – Liesborner Weg 19 (Projekt 0200)", H2),
         tab([["Beleg", "Datum", "Adressiert an", "Gewerk", "Netto", "Brutto", "Zahlung", "Status / To-do"],
              ["RE 2024-47", "16.04.2024", "CREST Living", "Sanitärobjekte, Montage Armaturen", "12.481,00", "14.852,39", "nicht belegbar", "Kontoauszüge Apr.–Jul. 2024 besorgen"],
              ["Dok. 159", "03.12.2024", "CREST Investment", "Heizung – hydraulischer Abgleich", "270,00", "321,30", "keine", "OFFEN – nur Angebotsnr.; in neue SR übernommen"],
              ["Dok. 176 (SR)", "05.01.2025", "CREST Investment", "Fußbodenheizung (12 % Rabatt)", "18.942,26", "22.541,30", "keine", "OFFEN – nur Angebotsnr.; in neue SR übernommen"],
              ["NA 175", "05.01.2025", "CREST Living", "Nachtragsangebot Sanitärobjekte", "5.605,00", "6.669,95", "–", "Angebot"],
              ["Dok. 175", "05.01.2025", "CREST Investment", "Sanitär-Nachtrag", "5.605,00", "6.669,95", "–", "Vorversion von RE 2025-8"],
              ["RE 2025-8", "28.03.2025", "CREST Investment", "Sanitär-Nachtrag", "5.605,00", "6.669,95", "keine", "durch 2025-17 ersetzt → Stornorechnung schreiben"],
              ["RE 2025-17", "14.04.2025", "CREST Living", "Sanitär-Nachtrag (korrigiert)", "4.758,00", "5.662,02", "19.09.2025: 5.662,02", "bezahlt"],
              ["NEU: SR FBH", "(Entwurf)", "CREST Living", "Fußbodenheizung + hydr. Abgleich", "20.000,00", "23.800,00", "–", "ersetzt Dok. 159 + 176; Nr./Datum vergeben"]],
             [22, 21, 26, 53, 19, 19, 30, 83], colour={2: RED, 3: RED, 6: AMB, 7: GRN, 8: AMB}, right=(4, 5)),
         Spacer(1, 2*mm),
         Paragraph("<b>Neue Schlussrechnung Fußbodenheizung:</b> Positionen zu Listenpreisen 21.795,30 € netto (FBH 21.525,30 + hydr. Abgleich 270,00), "
                   "Nachlass 1.795,30 € → <b>20.000,00 € netto + 3.800,00 € USt = 23.800,00 € brutto</b>. Hinweis: Dok. 176 hatte 12 % Rabatt "
                   "(= 19.212,26 € netto); die 20.000 € liegen 787,74 € netto darüber. "
                   "<b>Gleichwertig als kumulierte Schlussrechnung</b> über alle Villa-Leistungen: Gesamtleistung 37.239,00 € netto / 44.314,41 € brutto, "
                   "abzgl. RE 2024-47 und RE 2025-17 → gleicher Zahlbetrag 23.800,00 €. Nur eine der beiden Fassungen versenden. "
                   "Leistungszeitraum laut CREST-Protokollen 11.2023 – 03.12.2024.", P),
         PageBreak(),
         Paragraph("2. Neubau Butterfly Houses – Liesborner Weg 19 a + b (Projekt 1150)", H2),
         Paragraph("<b>Getrennt wurde nach Haus, nicht nach Gewerk:</b> je Haus ein Komplettangebot; Klima, Lüftung, Heizung inkl. Wärmepumpe/FBH und Sanitär sind Titel "
                   "innerhalb der Angebote. Beauftragt wurde dann eine gemeinsame Pauschale für beide Häuser (Raten nach Bauphasen). "
                   "(Eine Trennung nach Gewerk <u>und</u> Haus gab es bei Scharfenberger Str. 26 – Angebote 102–105 und 43–45 –, nicht hier.)", P),
         Paragraph("Angebote – Endstände (Vorversionen: 202, 203, 213, 233 v1/v2, 234 v1/v2)", H3),
         tab([["Angebot", "Datum", "Haus", "Klima", "Lüftung", "Heizung inkl. WP + FBH", "Sanitär", "Diverses", "Summe brutto"],
              ["233 (v3)", "14.04.2025", "19 a – Haus 1", "13.897,41", "12.376,60", "68.383,51", "61.495,43", "1.319,71", "157.472,66"],
              ["234 (v3)", "14.04.2025", "19 b – Haus 2", "13.897,41", "11.620,95", "68.383,51", "59.976,99", "1.319,71", "155.198,57"],
              ["", "", "zusammen", "27.794,82", "23.997,55", "136.767,02", "121.472,42", "2.639,42", "312.671,23"]],
             [22, 20, 26, 24, 24, 38, 24, 22, 28], right=(3, 4, 5, 6, 7, 8)),
         Paragraph("Auftrag: Pauschale 300.000 € brutto (≈ 4 % unter den Angeboten) · Zahlungsplan-Raten: Rohinstallation 45.000 / 60.000 · FBH 45.000 · "
                   "Heizraum/Klima/WP 60.000 / 45.000 · Armaturen 30.000 · Inbetriebnahme + Abnahme 15.000.", P),
         Paragraph("Nachträge", H3),
         tab([["Nachtrag", "Datum", "Inhalt", "Brutto", "Status"],
              ["NA 1 – 216", "12.06. / 21.10.2025", "Verstärkungen, Wandöffnung UG (COSMO gestrichen)", "5.200,00", "CREST hat 5.200 € NETTO freigegeben; abgerechnet als 5.200 € BRUTTO → 830,25 € netto zu wenig"],
              ["NA 2 – 282 (= 283)", "12.10.2025", "Erdleitungen Schmutz- und Trinkwasser", "8.118,89", "abgerechnet in 2025-70; Nr. 282/283 doppelt"],
              ["NA 2 – 217", "12.06. / 22.07.2025", "Umsetzen UP-Körper (6–8 Std.)", "653,55 – 808,25", "nicht abgerechnet – beauftragt?"],
              ["Angebot 230", "15.11.2025", "Wasserzählerschacht (optional)", "1.231,32", "nicht abgerechnet – beauftragt?"]],
             [28, 30, 70, 26, 119], right=(3,)),
         Paragraph("Rechnungen und Zahlungen", H3),
         tab([["Rechnung", "Datum", "Rate / Inhalt", "Brutto", "Gezahlt", "Datum Zahlung", "Bemerkung (Verwendungszweck CREST)"],
              ["1. AR 2025-28", "20.05.2025", "Rohinstallation 1", "45.000,00", "33.308,77", "26.05.2025", "abzgl. BU, SE 10 %, Bauabzug 15 % (5.878,02)"],
              ["2. AR 2025-35", "11.06.2025", "Rohinstallation 2", "60.000,00", "44.411,69", "18.06.2025", "abzgl. BU, SE 10 %, Skonto, Bauabzug (7.837,36)"],
              ["3. AR 2025-37", "01.07.2025", "Fußbodenheizung", "45.000,00", "33.308,77", "14.07.2025", "abzgl. BU, Skonto, Bauabzug (5.878,02)"],
              ["4. AR 2025-43", "24.07.2025", "Heizraum/Klima/WP 1", "60.000,00", "52.249,05", "04.08. + 04.09.2025", "Bauabzug 7.837,36 am 04.09. nachgezahlt"],
              ["5. AR 2025-69", "12.10.2025", "Heizraum/Klima/WP 2", "45.000,00", "39.186,79", "16.10.2025", "abzgl. BU, SE 10 %, Skonto"],
              ["6. AR 2025-70", "12.10.2025", "Nachträge 1 + 2", "13.318,89", "11.957,03", "29.10.2025", "CREST-Prüfblatt: 12.844,01 freigegeben"],
              ["7. AR 2025-79", "21.10.2025", "Armaturen", "30.000,00", "26.124,52", "29.10.2025", ""],
              ["8. AR 2025-98", "16.12.2025", "Teil Inbetriebnahme/Abnahme", "11.000,00", "0,00", "–", "OFFEN – keine Zahlung bis Apr. 2026"],
              ["Summe", "", "", "309.318,89", "240.546,62", "", "Differenz 68.772,27 (Einbehalte, Bauabzug, Skonto, BU, 8. AR)"]],
             [26, 20, 42, 24, 24, 32, 105], colour={8: RED, 9: inv.HEAD}, right=(3, 4)),
         Spacer(1, 2*mm),
         KeepTogether([Paragraph("Offene Punkte Neubau", H3),
         Paragraph("• 8. AR 2025-98 über 11.000 € unbezahlt → erinnern. • Restrate 4.000 € der Pauschale (15.000 − 11.000) noch nicht abgerechnet → mit Schlussrechnung. "
                   "• Sicherheitseinbehalt 10 %: rechnerisch 28.500 € auf die Raten + 1.427,11 € auf den Nachtrag → nach Abnahme/Bürgschaft zurückfordern. "
                   "• Bauabzugsteuer 19.593,40 € (1.–3. AR) hat CREST ans Finanzamt abgeführt → beim Finanzamt anrechnen lassen, keine Forderung an CREST. "
                   "• Nachtrag 1: 830,25 € netto zu wenig abgerechnet (siehe oben). • Unterschriebenen Bauvertrag HLS suchen.", P)]),
         Spacer(1, 3*mm),
         Paragraph("<b>Wichtig für beide Projekte:</b> Laut CREST-Prüfblatt war die Freistellungsbescheinigung (§ 48b EStG) nur bis <b>02.07.2026</b> gültig. "
                   "Eine neuere Bescheinigung liegt nicht in Drive (geprüft 29.09.2026). "
                   "Ohne neue Bescheinigung darf CREST von jeder Zahlung 15 % Bauabzugsteuer einbehalten – bei der neuen Schlussrechnung wären das 3.570,00 €. "
                   "<b>Bankverbindung vor dem Versand festlegen:</b> Der Entwurf nennt die Berliner Volksbank, die letzte Rechnung 2026-43 dagegen N26 (Kontoinhaber Semir Redzic privat).", P)]
    doc.build(E)

if __name__ == "__main__":
    build(sys.argv[1]); print("ok")
