"""Endgültige Schlussrechnungen (freigegeben von Semir am 19.10.2026): Villa Nr. 2026-44 und
Neubau 19 a + b Nr. 2026-45, Rechnungsdatum 19.10.2026, 10 Tage, fällig 29.10.2026, Berliner Volksbank, ohne Wasserzeichen."""
import sys, os
import make_invoice_leans as inv

FINAL = dict(datum="19.10.2026", ziel="10 Tage", faellig="29.10.2026")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VILLA = os.path.join(ROOT, "Villa_0200/2_Schlussrechnung/Schlussrechnung_2026-44_Villa_17.000_brutto.pdf")
NEUBAU = os.path.join(ROOT, "Neubau_19ab_1150/5_Schlussrechnung/Schlussrechnung_2026-45_Neubau_19ab_43.745,31.pdf")

def build():
    inv.WATERMARK = False
    import make_invoice_leans_kumuliert as kum, make_invoice_neubau as nb
    # 2024-47 laut Semir bezahlt („20.000 brutto sind noch übrig, das war's“); Datum mangels Kontoauszug 04–07/2024 nicht belegt
    kum.ZAHLUNGSDATUM_OFFEN = "bezahlt"
    inv.META.update(nr="2026-44", **FINAL); w1 = kum.build(VILLA)
    inv.META.update(nr="2026-45", **FINAL); w2 = nb.build(NEUBAU)
    return w1, w2

if __name__ == "__main__":
    w1, w2 = build()
    print("Villa 2026-44:", w1["rest_netto"], w1["rest_ust"], w1["rest_brutto"])
    print("Neubau 2026-45: Rest", w2["rest"]["brutto"], "| Zahlbetrag", w2["gesamt_offen"])
