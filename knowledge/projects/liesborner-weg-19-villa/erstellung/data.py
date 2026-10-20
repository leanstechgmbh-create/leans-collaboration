"""Single source of truth for the Villa Liesborner Weg 19 cumulative final invoice.
All values transcribed from the original LEANS invoices in Google Drive."""
from decimal import Decimal as D, ROUND_HALF_UP

def r2(x): return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

VAT = D("0.19")

# (pos, beschreibung, menge, einheit, ep_netto, beleg)
SANITAER = [
  ("1.1", "Dachgeschoss (DG)", None, None, None, None),
  ("1.1.1", "Geberit iCon Wand-Tiefspül-WC mit WC-Sitz, kurz, weiß matt – liefern und montieren", "1", "Stk.", "789.00", "RE 2024-47"),
  ("1.1.2", "WC-Drückerplatte montieren", "1", "Stk.", "65.00", "RE 2024-47"),
  ("1.1.4", "Unterputz-Waschtischarmatur montieren", "1", "Stk.", "109.00", "RE 2024-47"),
  ("1.1.5", "Unterputz-Duscharmatur Gessi montieren", "1", "Stk.", "229.00", "RE 2024-47"),
  ("1.1.6", "Siphon schwarz matt liefern und montieren", "1", "Stk.", "89.00", "RE 2024-47"),
  ("1.1.1*", "Küchenarmatur (bauseits) montieren, 2 Eckventile + Ablaufgarnitur liefern und montieren", "1", "Stk.", "229.00", "RE 2025-17"),
  ("1.2", "Obergeschoss (OG)", None, None, None, None),
  ("1.2.1", "Geberit iCon Wand-Tiefspül-WC mit WC-Sitz, kurz, weiß matt – liefern und montieren", "3", "Stk.", "789.00", "RE 2024-47"),
  ("1.2.2", "WC-Drückerplatte montieren", "3", "Stk.", "65.00", "RE 2024-47"),
  ("1.2.3.1", "Wandwaschbecken TWG71 Mineralguss weiß matt mit Siphon", "2", "Stk.", "589.00", "RE 2024-47"),
  ("1.2.3.2", "Wandwaschbecken PB2035 Mineralguss weiß matt mit Siphon", "1", "Stk.", "579.00", "RE 2024-47"),
  ("1.2.4", "Unterputz-Waschtischarmatur montieren", "3", "Stk.", "109.00", "RE 2024-47"),
  ("1.2.5", "Unterputz-Duscharmatur Gessi montieren", "2", "Stk.", "229.00", "RE 2024-47"),
  ("1.2.7", "Duschrinne Geberit liefern und montieren", "1", "Stk.", "467.00", "RE 2024-47"),
  ("1.2.8", "Siphon schwarz matt liefern und montieren", "3", "Stk.", "89.00", "RE 2024-47"),
  ("1.2.9", "Urinal-Drückerplatte montieren", "1", "Stk.", "100.00", "RE 2025-17"),
  ("1.2.10", "Duravit ME by Starck Urinal Rimless weiß matt 0,5 l mit Deckel, Absaugsiphon und Zulaufgarnitur", "1", "Stk.", "830.00", "RE 2025-17"),
  ("1.3", "Erdgeschoss (EG)", None, None, None, None),
  ("1.3.1", "Geberit iCon Wand-Tiefspül-WC mit WC-Sitz, kurz, weiß matt – liefern und montieren", "2", "Stk.", "789.00", "RE 2024-47"),
  ("1.3.2.1", "WC-Drückerplatte montieren", "2", "Stk.", "65.00", "RE 2024-47"),
  ("1.3.3", "Duravit ME by Starck Urinal Rimless weiß 0,5 l mit Deckel, Absaugsiphon und Zulaufgarnitur", "1", "Stk.", "750.00", "RE 2025-17"),
  ("1.3.5", "Waschbecken und Armatur (bauseits) montieren inkl. Eckventile, Schläuche und Ablaufgarnitur", "1", "Stk.", "320.00", "RE 2025-17"),
  ("1.4", "Kellergeschoss (KG)", None, None, None, None),
  ("1.4.1", "Geberit iCon Wand-Tiefspül-WC mit WC-Sitz, kurz, weiß matt – liefern und montieren", "1", "Stk.", "789.00", "RE 2024-47"),
  ("1.4.2", "WC-Drückerplatte montieren", "2", "Stk.", "65.00", "RE 2024-47"),
  ("1.4.3", "Wandwaschbecken TWG71 Mineralguss weiß matt mit Siphon", "1", "Stk.", "589.00", "RE 2024-47"),
  ("1.4.4", "Unterputz-Waschtischarmatur montieren", "2", "Stk.", "109.00", "RE 2024-47"),
  ("1.4.5", "Unterputz-Duscharmatur Gessi montieren", "2", "Stk.", "229.00", "RE 2024-47"),
  ("1.4.6", "Küchenarmatur (schwenkbar) liefern und montieren, 2 Eckventile + Ablaufgarnitur", "1", "Stk.", "429.00", "RE 2025-17"),
  ("1.4.7", "Duravit ME by Starck Urinal Rimless weiß 0,5 l mit Deckel, Absaugsiphon und Zulaufgarnitur", "1", "Stk.", "750.00", "RE 2025-17"),
  ("1.4.8", "Urinal-Drückerplatte montieren", "1", "Stk.", "100.00", "RE 2025-17"),
  ("1.4.9", "Villeroy & Boch Subway 3.0 Rechteck-Badewanne Stone White mit Überlauf", "1", "Stk.", "1250.00", "RE 2025-17"),
  ("1.4.10", "Badewannen-Armatur montieren", "1", "Stk.", "109.00", "RE 2024-47"),
  ("1.4.11", "Waschmaschine und Trockner montieren mit Schallschutzmatte", "2", "Set", "119.00", "RE 2024-47"),
  ("1.4.12", "Siphon schwarz matt liefern und montieren", "1", "Stk.", "89.00", "RE 2024-47"),
  ("1.4.13", "Siphon chrom liefern und montieren", "1", "Stk.", "79.00", "RE 2024-47"),
  ("1.4.14", "Handbrausen-Halterung montieren", "1", "Stk.", "65.00", "RE 2024-47"),
  ("1.4.15", "Handwaschbecken Laufen ohne Hahnloch", "1", "Stk.", "465.00", "RE 2024-47"),
  ("1.4.16", "Geberit iCon weiß Wand-Tiefspül-WC mit WC-Sitz", "1", "Stk.", "425.00", "RE 2024-47"),
]

HEIZUNG = [
  ("2.1", "Durchführung des hydraulischen Abgleichs (Lieferdatum 03.12.2024)", "1", "pschl.", "270.00", "Dok. 159"),
  ("2.7.0", "KG: Ratiodämm Tackerplatte 2 cm mit Unterdämmung 3 cm", "78.50", "m²", "42.50", "Dok. 176"),
  ("2.7.1", "KG: Ratiodämm Tackerplatte 3 cm mit Unterdämmung 6 cm", "40.50", "m²", "45.70", "Dok. 176"),
  ("2.8.1", "EG: Bekotec EN FTS", "125.50", "m²", "47.80", "Dok. 176"),
  ("2.9", "OG: Bekotec EN FTS", "67.50", "m²", "47.80", "Dok. 176"),
  ("2.10", "KG: Ratiodämm Tackerplatte 2 cm mit Unterdämmung 2 cm", "58.00", "m²", "41.60", "Dok. 176"),
  ("2.11", "Befüllung des gesamten Heizsystems mit aufbereitetem Heizungswasser, Entlüftung, Einregulierung und Aufheizen", "1", "pschl.", "4700.00", "Dok. 176"),
]
FBH_RABATT = D("0.12")   # wie im Dokument 176 gewährt – nur auf die FBH-Positionen 2.7.0–2.11

# Bereits gestellte, gültige Rechnungen (werden in der Schlussrechnung abgezogen)
VORRECHNUNGEN = [
  # nr, datum, empfaenger, gewerk, netto, ust, brutto
  ("2024-47", "16.04.2024", "CREST Living GmbH & Co. KG", "Sanitärobjekte / Montage Armaturen", D("12481.00"), D("2371.39"), D("14852.39")),
  ("2025-17", "14.04.2025", "CREST Living GmbH & Co. KG", "Sanitärobjekte / Montage (Nachtrag)",D("4758.00"),  D("904.02"),  D("5662.02")),
]

def line_total(q, ep): return r2(D(q) * D(ep))

def totals():
    san = sum(line_total(q, ep) for p, t, q, u, ep, b in SANITAER if q)
    hz_abgleich = sum(line_total(q, ep) for p, t, q, u, ep, b in HEIZUNG if b == "Dok. 159")
    fbh = sum(line_total(q, ep) for p, t, q, u, ep, b in HEIZUNG if b == "Dok. 176")
    rabatt = r2(fbh * FBH_RABATT)
    gesamt_netto = san + hz_abgleich + fbh - rabatt
    ust = r2(gesamt_netto * VAT)
    vr_netto = sum(v[4] for v in VORRECHNUNGEN)
    vr_ust = sum(v[5] for v in VORRECHNUNGEN)
    rest_netto = gesamt_netto - vr_netto
    rest_ust = ust - vr_ust
    return dict(san=san, hz_abgleich=hz_abgleich, fbh=fbh, rabatt=rabatt, fbh_netto=fbh - rabatt,
                gesamt_netto=gesamt_netto, ust=ust, gesamt_brutto=gesamt_netto + ust,
                vr_netto=vr_netto, vr_ust=vr_ust, vr_brutto=vr_netto + vr_ust,
                rest_netto=rest_netto, rest_ust=rest_ust, rest_brutto=rest_netto + rest_ust)

if __name__ == "__main__":
    t = totals()
    for k, v in t.items(): print(f"{k:14} {v:>12}")
    assert t["san"] == D("17239.00"), t["san"]
    assert t["fbh"] == D("21525.30"), t["fbh"]
    assert t["fbh_netto"] == D("18942.26"), t["fbh_netto"]
    # each prior invoice's own VAT must equal 19 % of its net
    for v in VORRECHNUNGEN: assert r2(v[4] * VAT) == v[5] and v[4] + v[5] == v[6], v
