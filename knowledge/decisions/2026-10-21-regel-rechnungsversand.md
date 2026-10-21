# REGEL – Rechnungsversand (für alle Chats und Assistenten)

Stand: 21.10.2026 · Festgelegt von Semir Redzic, LEANS Tech GmbH

## Jede Rechnung = eine eigene E-Mail

1. **Eine Mail pro Rechnung bzw. Schlussrechnung.** Keine Sammelmails über mehrere
   Bauvorhaben.
2. **Empfänger:** der jeweils Zuständige beim Kunden (Ansprechpartner aus Auftrag bzw.
   bisherigem Schriftverkehr), dazu die Firmen-Sammeladresse, falls bisher üblich.
3. **Die Mail ist kurz, höflich und vollständig:** Anrede mit Namen, Bauvorhaben,
   Rechnungsnummer, Betrag, Fälligkeit, Bankverbindung, Liste der Anlagen, Signatur.

## Anhänge: genau zwei

| Anhang | Inhalt | Format |
|---|---|---|
| 1 | Rechnung bzw. Schlussrechnung (ggf. mit Aufstellung als zweite PDF) | **PDF, einzeln** |
| 2 | Alles andere | **eine ZIP je Bauvorhaben** |

Die ZIP ist sortiert:

- `01 Erklaerungen/`: Fachunternehmererklärungen, Fachbauleitererklärung,
  GEG-/Unternehmererklärung, Sachkundebescheinigung
- `02 Datenblaetter/`: alle Datenblätter der verbauten Geräte und Materialien
- `03 Nachweise/`: Prüf- und Inbetriebnahmeprotokolle, Firmennachweise (falls vorhanden)

Dateinamen sind sprechend, z. B. `Fachunternehmererklaerung Sanitaer Villa.pdf`.
ZIP-Name: `Anlagen <Bauvorhaben> - <Rechnung Nr>.zip`.

## Ablage und Versand

- **Insolvenzordner** (Google Drive, ID `1TTiMBN6SS71T_VGdjYIBWq74JXOwxosm`): **nur die
  Rechnungs-PDF** als Kopie in den Ordner der Firma, die auf der Rechnung steht. Keine
  Erklärungen, Datenblätter oder ZIPs.
- **Nur Entwürfe anlegen. Gesendet wird erst nach Semirs ausdrücklichem „ja, senden“**
  für genau diese Mail.
- Große Anhänge kommen über die Seite „LEANS Versand“
  (https://claude.ai/artifact/PeMuDe75EtBaQGwne3NBSU) in den Gmail-Entwurf: Auftrag in
  der Datenbank `auftraege` eintragen, Semir drückt „Offene Aufträge ausführen“.
- Nach dem Versand den Status in der „00 Übersicht – <Firma>“ auf „versendet am …“
  setzen.
