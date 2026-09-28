# Zweite, unabhängige Prüfung: Zeilen aus den Original-PDFs (Wortpositionen) rekonstruieren und nachrechnen
import re, pymupdf as f
from decimal import Decimal as D
from data import SANITAER, HEIZUNG, r2
def de(s): return D(s.replace(".", "").replace(",", "."))
def rows_of(path):
    out = []
    for p in f.open(path):
        ws = sorted(p.get_text("words"), key=lambda w: (round(w[1] / 3), w[0]))
        line, y = [], None
        for w in ws:
            if y is None or abs(w[1] - y) <= 3: line.append(w)
            else: out.append(" ".join(x[4] for x in sorted(line, key=lambda x: x[0]))); line = [w]
            y = w[1]
        if line: out.append(" ".join(x[4] for x in sorted(line, key=lambda x: x[0])))
    return out
def main():
    files = {"RE 2024-47": "RECHNUNG 2024-47 - LEANS Tech GmbH - 14852.39 EUR.pdf",
             "RE 2025-17": "RECHNUNG 2025-17 - LEANS Tech GmbH - 5662.02 EUR (1).pdf",
             "Dok. 159": "RECHNUNG 159 - LEANS Tech GmbH - 321.3 EUR.pdf",
             "Dok. 176": "044_—_SCHLUSSRECHNUNG 176 - LEANS Tech GmbH - 22541.3 EUR (2).pdf"}
    pat = re.compile(r"(\d+,\d{2}) (?:Stk\.|set|Set|m²|pschl\.) ([\d.]+,\d{2}) € 19,00 % (?:([\d.]+,\d{2}) € )?([\d.]+,\d{2}) €")
    allok = True
    for key, fn in files.items():
        lines = rows_of("orig/" + fn)
        pos = [m.groups() for l in lines for m in [pat.search(l)] if m]
        net = sum(r2(de(q) * de(ep)) for q, ep, _, _ in pos)
        brutto_zeilen = sum(de(b) for *_, b in pos)
        # jede Zeile: Brutto = Netto × 1,19 (gerundet)?
        zeilen_ok = all(r2(r2(de(q) * de(ep)) * D("1.19")) == de(b) for q, ep, _, b in pos)
        src = [x for x in SANITAER + HEIZUNG if x[5] == key or (key == "Dok. 159" and x[5] == "Dok. 159")]
        exp = sum(r2(D(q) * D(ep)) for p, t, q, u, ep, b in src if q)
        n_exp = len([x for x in src if x[2]])
        ok = (exp == net) and (n_exp == len(pos)) and zeilen_ok
        allok &= ok
        print(f"{key:10} PDF: {len(pos):2} Pos., Σnetto {net:>9}, Σbrutto-Zeilen {brutto_zeilen:>9} | data.py: {n_exp:2} Pos., Σnetto {exp:>9} | Zeilen brutto=netto×1,19: {zeilen_ok} -> {'OK' if ok else 'ABWEICHUNG'}")
        for l in lines:
            if re.search(r"(Nettobetrag|Gesamtsumme|Gesamt|Rabatt|Zwischensumme)", l): print("           ", l)
    print("ERGEBNIS:", "alle Positionen und Summen stimmen mit den Originalen überein" if allok else "ABWEICHUNG – prüfen")

if __name__ == "__main__":
    main()
