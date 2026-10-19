"""Fachunternehmererklärungen Villa und Neubau 19 a + b im LEANS-Layout der bisherigen Erklärungen
(Vorlage: „FACHUNTERNEHMERERKLÄRUNG - Heizung.pdf“ für CREST Wohnen am Tegeler See vom 22.11.2025).
Datum und Unterschrift bleiben frei – Semir unterschreibt selbst.
Kopf, Unterschriftsbereich und Fußzeile werden auch von make_erklaerungen.py genutzt."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
import make_invoice_leans as inv   # registriert Fonts L/LB, Logo

GREEN = colors.HexColor("#8DC63F"); TGREEN = colors.HexColor("#6BAA2C"); GREY = colors.HexColor("#222222")
EMPF = ["CREST Living GmbH & Co. KG", "Liesborner Weg 19", "13507 Berlin"]
TEXT = ["Als Fachunternehmer erklären wir, dass die im oben genannten Auftrag enthaltenen Leistungen nach den anerkannten "
        "Regeln der Technik ausgeführt wurden.",
        "Der Auftrag wurde nach geltenden Vorschriften, Normen und Verordnungen durchgeführt.",
        "Die verarbeiteten Materialien, Baustoffe und Produkte sind von einer Materialprüfanstalt, einem Überwachungsinstitut, "
        "dem TÜV oder ähnlichem zugelassen.",
        "Die Herstellerangaben wurden bei der Verarbeitung eingehalten."]
VILLA = ["Bauvorhaben: Liesborner Weg 19, 13507 Berlin (Villa)"]
NEUBAU = ["Bauvorhaben: Liesborner Weg 19 a und b, 13507 Berlin (Neubau Butterfly Houses)", "Auftragsnummer: 20250418_#"]
ERKLAERUNGEN = [
    # Zielordner, Dateiname, Titel-Gewerk, Kopfzeilen
    ("Villa_0200/4_Fachunternehmererklaerungen", "FUE_Villa_Heizung_Fussbodenheizung.pdf", "HEIZUNG",
     VILLA + ["Gewerk: Heizung – Fußbodenheizung und hydraulischer Abgleich"]),
    ("Villa_0200/4_Fachunternehmererklaerungen", "FUE_Villa_Sanitaer.pdf", "SANITÄR",
     VILLA + ["Gewerk: Sanitär – Sanitärobjekte und Montage von Armaturen"]),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "FUE_Neubau_19ab_Heizung.pdf", "HEIZUNG",
     NEUBAU + ["Gewerk: Heizung inkl. Wärmepumpe und Fußbodenheizung"]),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "FUE_Neubau_19ab_Sanitaer.pdf", "SANITÄR", NEUBAU + ["Gewerk: Sanitär"]),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "FUE_Neubau_19ab_Lueftung.pdf", "LÜFTUNG", NEUBAU + ["Gewerk: Lüftung"]),
    ("Neubau_19ab_1150/6_Fachunternehmererklaerungen", "FUE_Neubau_19ab_Klima.pdf", "KLIMA", NEUBAU + ["Gewerk: Klima"]),
]
FOOT = [("LEANS Tech GmbH", "Berlepschstr. 165", "14165 Berlin"),
        ("+49 170 8280836", "www.leanstech-gmbh.de", "info@leanstech-gmbh.de"),
        ("Berliner Volksbank", "DE21 1009 0000 2911 7280 04", "BIC: BEVODEBB"),
        ("USt. ID: DE357948720", "Geschäftsführer:", "Semir Redzic")]
BODY = ParagraphStyle("b", fontName="L", fontSize=10.5, leading=15, textColor=GREY, alignment=4, spaceAfter=7)
W, H = A4

def kopf(c, titel, kopfzeilen, kopf_x=48*mm):
    """Logo, Absenderzeile, Empfänger, grüner Titel und fette Kopfzeilen (Bauvorhaben, Gewerk …)."""
    c.drawImage(os.path.join(os.path.dirname(__file__), inv.LOGO), W - 70*mm, H - 40*mm, width=48*mm, height=30*mm,
                mask="auto", preserveAspectRatio=True)
    c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.line(20*mm, H - 42*mm, W - 20*mm, H - 42*mm)
    c.setFillColor(TGREEN); c.setFont("LB", 7.5); c.drawString(20*mm, H - 48*mm, "LEANS Tech GmbH – Berlepschstr. 165 – 14165 Berlin")
    c.setFillColor(GREY); c.setFont("L", 10)
    y = H - 56*mm
    for line in EMPF: c.drawString(20*mm, y, line); y -= 9*mm
    c.setFillColor(TGREEN); c.setFont("LB", 12); c.drawString(23*mm, H - 96*mm, titel)
    c.setFillColor(GREY); c.setFont("LB", 10.5); y = H - 115*mm
    for line in kopfzeilen: c.drawString(kopf_x, y, line); y -= 5.5*mm
    return y

def unterschrift(c, name="Semir Redzic", zusatz=None):
    """Ort/Datum (Datum rot als Platzhalter) und leere Unterschriftslinie – bewusst ohne Unterschrift/Stempel."""
    c.setFillColor(GREY); c.setFont("L", 10.5); c.drawString(20*mm, 60*mm, "Berlin, ")
    c.setFillColor(colors.HexColor("#B00000")); c.drawString(20*mm + c.stringWidth("Berlin, ", "L", 10.5), 60*mm, "__.__.2026")
    c.setFillColor(GREY); c.setStrokeColor(GREY); c.setLineWidth(0.5); c.line(W - 85*mm, 64*mm, W - 20*mm, 64*mm)
    c.setFont("L", 8.5); c.drawCentredString(W - 52.5*mm, 59.5*mm, "Unterschrift / Firmenstempel")
    c.setFont("L", 10.5); c.drawRightString(W - 20*mm, 52*mm, name)
    if zusatz: c.setFont("L", 8.5); c.drawRightString(W - 20*mm, 47.5*mm, zusatz)

def fuss(c):
    c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.line(20*mm, 34*mm, W - 20*mm, 34*mm)
    c.setFillColor(GREY); c.setFont("L", 7.5); x0, colw = 20*mm, (W - 40*mm) / 4
    for i, col in enumerate(FOOT):
        for j, t in enumerate(col): c.drawCentredString(x0 + colw*(i + 0.5), 27*mm - j*3.6*mm, t)

def erklaerung(path, gewerk, kopfzeilen):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(f"Fachunternehmererklärung {gewerk.title()} – {kopfzeilen[0][13:]}"); c.setAuthor("LEANS Tech GmbH")
    kopf(c, f"FACHUNTERNEHMERERKLÄRUNG | {gewerk}", kopfzeilen)
    Frame(20*mm, H - 205*mm, W - 40*mm, 62*mm, showBoundary=0, leftPadding=0, rightPadding=0).addFromList(
        [Paragraph(t, BODY) for t in TEXT], c)
    unterschrift(c); fuss(c)
    c.showPage(); c.save()

def build(root):
    out = []
    for ordner, datei, gewerk, kopfzeilen in ERKLAERUNGEN:
        os.makedirs(os.path.join(root, ordner), exist_ok=True)
        p = os.path.join(root, ordner, datei); erklaerung(p, gewerk, kopfzeilen); out.append(p)
    return out

if __name__ == "__main__":
    for p in build(sys.argv[1] if len(sys.argv) > 1 else ".."): print(p)
