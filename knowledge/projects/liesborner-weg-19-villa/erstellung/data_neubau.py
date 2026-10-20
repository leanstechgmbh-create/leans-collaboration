"""Neubau Butterfly Houses Liesborner Weg 19 a + b (Projekt 1150): Auftrag, Nachträge, Abschlagsrechnungen
und Zahlungen. Werte aus den Original-PDFs (Neubau_19ab_1150/) und den Kontoauszügen (Berliner Volksbank).
Die Abzüge je Zahlung folgen der Rechenweise im CREST-Rechnungsprüfblatt vom 15.10.2025:
netto − Bauumlage 0,25 % → × 1,19 → − Sicherheitseinbehalt 10 % → − Skonto → − Bauabzug 15 %."""
from decimal import Decimal as D
from data import r2, VAT

BU_SATZ, SE_SATZ, BAUABZUG_SATZ = D("0.0025"), D("0.10"), D("0.15")

# Bauvertrag HLS, Anlage 1 vom 15.05.2025: Pauschalpreis 300.000,00 € brutto (Auftrag Nr. 20250418_#)
PAUSCHALE_BRUTTO = D("300000.00")
NACHTRAEGE = [
    # nr, angebot, datum, text, netto
    ("NA 1", "216", "12.06.2025", "Verstärkungen für Versorgungsleitungen, UP-Körper und Waschbeckenaufhängung, Betonwandöffnung UG, "
     "GESSI 316 UP-Körper und Fertigmontagesets, abzgl. Instandsetzung Dämmung Eingangsbereich "
     "(freigegeben lt. CREST-Rechnungsprüfblatt vom 15.10.2025)", D("5200.00")),
    ("NA 2", "282", "12.10.2025", "Erdleitungen Schmutzwasser (KG DN 100/125) und Trinkwasser (PE 32/25)", D("6822.60")),
]

# Abzug laut Semir (19.10.2026): CREST darf die Inbetriebnahme der Hebeanlage in Haus B und die kleine Reparatur der
# Platine der Klimaanlage gegenrechnen, pauschal brutto (Korrektur 20.10.2026: 4.000 €, vorher 2.000 €; wie der
# Villa-Abzug). Netto/USt aus dem Bruttobetrag.
ABZUG_BRUTTO = D("4000.00")
ABZUG_NETTO = r2(ABZUG_BRUTTO / (1 + VAT))
ABZUG_UST = ABZUG_BRUTTO - ABZUG_NETTO
ABZUG_TEXT = "abzgl. Inbetriebnahme der Hebeanlage Haus B und Reparatur der Platine der Klimaanlage (pauschal)"

# nr, datum, rate, netto, ust, brutto, skonto_satz, bauabzug, zahlungen [(datum, betrag)]
AR = [
    ("2025-28", "20.05.2025", "1. AR – Rohinstallation 1. Rate", D("37815.13"), D("7184.87"), D("45000.00"), D("0.03"), True,
     [("26.05.2025", D("33308.77"))]),
    ("2025-35", "11.06.2025", "2. AR – Rohinstallation 2. Rate", D("50420.17"), D("9579.83"), D("60000.00"), D("0.03"), True,
     [("18.06.2025", D("44411.69"))]),
    ("2025-37", "01.07.2025", "3. AR – Fußbodenheizung", D("37815.13"), D("7184.87"), D("45000.00"), D("0.03"), True,
     [("14.07.2025", D("33308.77"))]),
    # Bauabzug zunächst einbehalten, am 04.09.2025 erstattet (Freistellungsbescheinigung ab 03.07.2025)
    ("2025-43", "24.07.2025", "4. AR – Heizungsraum/Klima/Wärmepumpe 1. Rate", D("50420.17"), D("9579.83"), D("60000.00"), D("0.03"), False,
     [("04.08.2025", D("44411.69")), ("04.09.2025", D("7837.36"))]),
    ("2025-69", "12.10.2025", "5. AR – Heizungsraum/Klima/Wärmepumpe 2. Rate", D("37815.13"), D("7184.87"), D("45000.00"), D("0.03"), False,
     [("16.10.2025", D("39186.79"))]),
    ("2025-70", "12.10.2025", "6. AR – Nachträge 1 und 2", D("11192.34"), D("2126.55"), D("13318.89"), D("0"), False,
     [("29.10.2025", D("11957.03"))]),
    ("2025-79", "21.10.2025", "7. AR – Komplettierung Armaturen", D("25210.08"), D("4789.92"), D("30000.00"), D("0.03"), False,
     [("29.10.2025", D("26124.52"))]),
    ("2025-98", "16.12.2025", "8. AR – Inbetriebnahme und Abnahme (Teil)", D("9243.70"), D("1756.30"), D("11000.00"), D("0"), False, []),
]

def abzuege(netto, brutto, skonto_satz, bauabzug, bezahlt):
    """Abzüge einer bezahlten AR nach CREST-Rechenweise (alle Beträge brutto)."""
    if not bezahlt:
        return dict(bu=D(0), se=D(0), skonto=D(0), bauabzug=D(0), soll=D(0))
    bu_netto = r2(netto * BU_SATZ)
    nach_bu = r2((netto - bu_netto) * (1 + VAT))
    se = r2(nach_bu * SE_SATZ)
    skonto = r2((nach_bu - se) * skonto_satz)
    ba = r2((nach_bu - se - skonto) * BAUABZUG_SATZ) if bauabzug else D(0)
    return dict(bu=brutto - nach_bu, se=se, skonto=skonto, bauabzug=ba, soll=nach_bu - se - skonto - ba)

def werte():
    p_netto = r2(PAUSCHALE_BRUTTO / (1 + VAT)); p_ust = PAUSCHALE_BRUTTO - p_netto
    na = [(n, a, d, t, net, r2(net * VAT)) for n, a, d, t, net in NACHTRAEGE]
    leist_netto = p_netto + sum(x[4] for x in na); leist_ust = r2(leist_netto * VAT)
    # Abzug vom Bruttobetrag: USt = USt der Leistung − USt-Anteil des Abzugs (Gesamtleistung genau um den Abzug brutto weniger)
    ges_netto = leist_netto - ABZUG_NETTO
    ges_ust = leist_ust - ABZUG_UST
    ar_netto = sum(a[3] for a in AR); ar_ust = sum(a[4] for a in AR); ar_brutto = sum(a[5] for a in AR)
    zeilen, s = [], dict(bu=D(0), se=D(0), skonto=D(0), bauabzug=D(0), gezahlt=D(0))
    for nr, dat, rate, n, u, b, sk, ba, zahl in AR:
        x = abzuege(n, b, sk, ba, bool(zahl))
        gezahlt = sum(z[1] for z in zahl)
        zeilen.append(dict(nr=nr, datum=dat, rate=rate, brutto=b, gezahlt=gezahlt, zahlungen=zahl,
                           offen=b - gezahlt - x["bu"] - x["se"] - x["skonto"] - x["bauabzug"], **x))
        for k in ("bu", "se", "skonto", "bauabzug", "gezahlt"): s[k] += zeilen[-1][k]
    rest = dict(netto=ges_netto - ar_netto, ust=ges_ust - ar_ust, brutto=ges_netto + ges_ust - ar_brutto)
    offen_ar = sum(z["offen"] for z in zeilen)
    return dict(p_netto=p_netto, p_ust=p_ust, na=na, leist_netto=leist_netto, leist_ust=leist_ust, leist_brutto=leist_netto + leist_ust,
                abzug=dict(netto=ABZUG_NETTO, ust=ABZUG_UST, brutto=ABZUG_BRUTTO, text=ABZUG_TEXT), ges_netto=ges_netto, ges_ust=ges_ust, ges_brutto=ges_netto + ges_ust,
                ar_netto=ar_netto, ar_ust=ar_ust, ar_brutto=ar_brutto, rest=rest, zeilen=zeilen, summen=s,
                offen_ar=offen_ar, sofort=rest["brutto"] + offen_ar, gesamt_offen=rest["brutto"] + offen_ar + s["se"])

if __name__ == "__main__":
    w = werte()
    for a, z in zip(AR, w["zeilen"]):
        # Jede rekonstruierte Zahlung muss auf den Cent dem Kontoauszug entsprechen
        if a[8]:
            bank = sum(x[1] for x in a[8])
            assert z["soll"] == bank, (a[0], z["soll"], bank)
            assert z["offen"] == 0, (a[0], z["offen"])
        print(f"{z['nr']}  brutto {z['brutto']:>10}  BU {z['bu']:>7}  SE {z['se']:>9}  Skonto {z['skonto']:>8}  "
              f"Bauabzug {z['bauabzug']:>8}  gezahlt {z['gezahlt']:>10}  offen {z['offen']:>9}")
    assert w["ar_brutto"] == D("309318.89") and w["summen"]["gezahlt"] == D("240546.62")
    assert w["leist_brutto"] - w["ges_brutto"] == ABZUG_BRUTTO and w["rest"]["brutto"] == D("988.00")
    assert w["gesamt_offen"] == D("41745.31"), w["gesamt_offen"]
    assert w["summen"]["bauabzug"] == D("19593.40")
    assert w["leist_brutto"] == D("314306.89") and w["ges_brutto"] == D("310306.89")
    for k in ("p_netto", "ges_netto", "ges_ust", "ges_brutto", "ar_netto", "ar_ust", "ar_brutto"): print(f"{k:11} {w[k]}")
    print("rest", w["rest"]); print("summen", w["summen"])
    print("offen 8. AR", w["offen_ar"], "| sofort fällig", w["sofort"], "| inkl. SE", w["gesamt_offen"])
