"""Unternehmererklärung nach § 96 GEG und Fachbauleitererklärung TGA für Villa und Neubau 19 a + b,
im Layout der Fachunternehmererklärungen (Kopf, Unterschrift, Fußzeile aus make_fue.py).
Aufgeführt ist nur, was laut Rechnungen/Angeboten zum Leistungsumfang gehört (Positionen im Kommentar); Punkte ohne Beleg
im Leistungsumfang stehen nicht drin. Semir prüft, setzt das Datum und unterschreibt (Wunsch 19.10.2026: „nur noch Datum“)."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import ParagraphStyle
import make_fue as fue

pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
W, H = A4
BODY = ParagraphStyle("eb", parent=fue.BODY, fontSize=9.5, leading=12.5, spaceAfter=4)
ITEM = ParagraphStyle("ei", parent=BODY, alignment=0, leftIndent=6*mm, firstLineIndent=-6*mm, spaceAfter=2)
JA, NEIN = '<font name="DV">☒</font>', '<font name="DV">☐</font>'

BAUHERR = "Bauherr: CREST Living GmbH & Co. KG"
VILLA = fue.VILLA + [BAUHERR]
NEUBAU = fue.NEUBAU + [BAUHERR]
FBL = "Fachbauleiter: Semir Redzic, Geschäftsführer LEANS Tech GmbH"

GEG_INTRO = ("Als ausführendes Unternehmen bestätigen wir dem Eigentümer gemäß § 96 des Gebäudeenergiegesetzes (GEG), "
             "dass die nachstehend angekreuzten, von uns geschäftsmäßig ausgeführten Arbeiten den Anforderungen des GEG entsprechen.")
GEG_SCHLUSS = "Diese Erklärung ist vom Eigentümer aufzubewahren und der zuständigen Behörde auf Verlangen vorzulegen."
FBL_TEXT = ["Ich war für die oben genannten Gewerke als Fachbauleiter tätig und habe die Ausführung dieser Arbeiten überwacht.",
            "Ich erkläre, dass die Arbeiten nach den Ausführungsunterlagen des Auftraggebers, den öffentlich-rechtlichen Vorschriften, "
            "insbesondere der Bauordnung für Berlin, nach den allgemein anerkannten Regeln der Technik und nach den Herstellerangaben "
            "ausgeführt wurden.",
            "Folgende Prüfungen und Arbeiten wurden durchgeführt:"]
FBL_SCHLUSS = "Die zugehörigen Protokolle liegen dem Bauherrn vor oder werden nachgereicht."

DOKUMENTE = [
    # Zielordner, Datei, Titel, Kopfzeilen, Einleitung, [(angekreuzt, Punkt)], Schluss
    ("Villa_0200/4_Fachunternehmererklaerungen", "Unternehmererklaerung_GEG_Villa.pdf", "UNTERNEHMERERKLÄRUNG | § 96 GEG",
     VILLA + ["Leistungszeitraum: 11.2023 – 03.12.2024"], [GEG_INTRO],
     [(True, "Einbau der Fußbodenheizung (Wärmeverteilung) in KG, EG und OG, Systeme Bekotec EN FTS und Tackerplatte mit Unterdämmung"),
      (True, "Hydraulischer Abgleich der Heizungsanlage (durchgeführt am 03.12.2024)")],
     GEG_SCHLUSS),
    ("Villa_0200/4_Fachunternehmererklaerungen", "Fachbauleitererklaerung_Villa.pdf", "FACHBAULEITERERKLÄRUNG | TGA",
     VILLA + ["Gewerke: Heizung (Fußbodenheizung, hydraulischer Abgleich), Sanitär", FBL], FBL_TEXT,
     [(True, "Druckprüfung der Fußbodenheizung (DIN EN 1264-4)"),
      (True, "Befüllung mit aufbereitetem Heizungswasser, Entlüftung, Einregulierung und Aufheizen"),
      (True, "Hydraulischer Abgleich der Heizungsanlage (03.12.2024)"),
      (True, "Funktionsprüfung der montierten Sanitärobjekte und Armaturen")],
     FBL_SCHLUSS + " Gasanschluss und Inbetriebnahme der Trinkwasseranlage gehörten nicht zu unserem Leistungsumfang."),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "Unternehmererklaerung_GEG_Neubau_19ab.pdf", "UNTERNEHMERERKLÄRUNG | § 96 GEG",
     NEUBAU + ["Leistungszeitraum: 05.2025 – 12.2025"], [GEG_INTRO],
     [(True, "Einbau der Heizungsanlage je Haus: elektrisch angetriebene Luft/Wasser-Wärmepumpe Samsung EHS Mono HT R290 "
             "(Außeneinheit AE160CXYDGK, 16 kW) mit Pufferspeicher"),
      (True, "Wärmeverteilung über Fußbodenheizung (REHAU PE-Xa 16 × 1,5) mit Heizkreisverteilern"),
      (True, "Trinkwassererwärmung über Trinkwarmwasserstation (Danfoss)"),
      (True, "Wärmedämmung von Wärmeverteilungs- und Warmwasserleitungen sowie Armaturen (§ 69 GEG)"),
      (True, "Klimaanlage je Haus: Mitsubishi Heavy Industries, Außengerät mit Kanalgerät; Dämmung der Kälteleitungen (§ 70 GEG)"),
      (True, "Wohnungslüftung: Ventilatoren Helios ELS EC und Außenwand-Luftdurchlässe LUNOS ALD-R 160"),
      (True, "Einregulierung der Heizungsanlage (hydraulischer Abgleich)")],
     GEG_SCHLUSS),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "Fachbauleitererklaerung_Neubau_19ab.pdf", "FACHBAULEITERERKLÄRUNG | TGA",
     NEUBAU + ["Gewerke: Heizung inkl. Wärmepumpe und FBH, Sanitär, Lüftung, Klima", FBL], FBL_TEXT,
     [(True, "Dichtheitsprüfung und Spülung der Trinkwasserinstallation (DIN EN 806-4)"),
      (True, "Druckprüfung der Heizungsanlage und der Fußbodenheizung (DIN EN 1264-4)"),
      (True, "Befüllung mit aufbereitetem Heizungswasser, Entlüftung, Einregulierung und Aufheizen"),
      (True, "Dichtheitsprüfung der Kältemittelleitungen und Inbetriebnahme der Klimaanlagen"),
      (True, "Inbetriebnahme der Wärmepumpen"),
      (True, "Funktionsprüfung der Lüftung; Brandschutz-Deckenschott nach Zulassung eingebaut"),
      (True, "Inbetriebnahme und Einweisung des Betreibers")],
     FBL_SCHLUSS),
]

def dokument(path, titel, kopfzeilen, einleitung, punkte, schluss):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(f"{titel.split(' | ')[0].title()} – {kopfzeilen[0][13:]}"); c.setAuthor("LEANS Tech GmbH")
    y = fue.kopf(c, titel, kopfzeilen, kopf_x=23*mm)
    inhalt = [Paragraph(t, BODY) for t in einleitung] + [Spacer(1, 1*mm)]
    inhalt += [Paragraph(f"{JA if ja else NEIN}&nbsp;&nbsp;{p}", ITEM) for ja, p in punkte]
    inhalt += [Spacer(1, 3*mm), Paragraph(schluss, BODY)]
    unten = 68*mm
    f = Frame(20*mm, unten, W - 40*mm, y - 3*mm - unten, showBoundary=0, leftPadding=0, rightPadding=0)
    f.addFromList(inhalt, c)
    assert not inhalt, f"Text passt nicht auf die Seite: {path}"
    fue.unterschrift(c, zusatz="Fachbauleiter" if titel.startswith("FACHBAU") else None); fue.fuss(c)
    c.showPage(); c.save()

def build(root):
    out = []
    for ordner, datei, *rest in DOKUMENTE:
        os.makedirs(os.path.join(root, ordner), exist_ok=True)
        p = os.path.join(root, ordner, datei); dokument(p, *rest); out.append(p)
    return out

if __name__ == "__main__":
    for p in build(sys.argv[1] if len(sys.argv) > 1 else ".."): print(p)
