# Prompt: Unberechnete Leistungen finden und Rechnungsentwuerfe erstellen

Wiederverwendbarer Ablauf fuer ChatGPT/Codex und Claude. Erstmals genutzt am 2026-09-28.

## Wann verwenden

Semir diktiert per Sprache eine Liste von Objekten oder Kunden, fuer die Rechnungen fehlen, offen sind oder Wartungen abzurechnen sind, und bittet um Entwuerfe zum Durchsehen.

## Ablauf

1. **Namen aus dem Diktat pruefen.** Die Spracherkennung verfaelscht Strassen- und Kundennamen. Nicht nur nach dem diktierten Wort suchen, sondern nach aehnlich klingenden Namen und nach der Schreibweise auf eigenen alten Rechnungen. Erfahrung aus dem ersten Einsatz: Ein diktierter Name entsprach einer Tippfehler-Schreibweise auf einer alten eigenen Rechnung, und eine diktierte Strasse war die Rechnungsanschrift des Kunden, nicht der Anlagenstandort.
2. **Quellen in dieser Reihenfolge durchsuchen:**
   - Google Drive: OP-Liste (offene Posten), Rechnungslisten je Jahr, Projektnummernliste (Kommissionsnummern), Projektordner, Hersteller-Serviceberichte und Wartungsvertraege, Grosshaendler-Rechnungen mit Kommissionsnummer.
   - Mail-Exporte in Drive: `.eml`-Dateien sind nur ueber den Titel suchbar, nicht im Volltext. Die `.txt`-Fassungen und Mail-Listen (`.md`/`.csv`) mit durchsuchen.
   - Gmail enthaelt nur neuere Post; die IONOS-Postfaecher sind nicht angebunden.
3. **Fuer jede Leistung klaeren:** Was wurde wann gemacht (Beleg), wer ist Rechnungsempfaenger, wurde schon berechnet, wurde bezahlt. Den Stand des Zahlungsabgleichs (letzter vorhandener Kontoauszug) immer mit angeben.
4. **Eingangsrechnungen gegen Ausgangsrechnungen pruefen:** Wurde eine Herstellerwartung oder ein Ersatzteil an den Kunden weiterberechnet, und deckt der berechnete Preis den Einkaufspreis?
5. **Entwurf schreiben:**
   - Layout und Formulierungen der letzten echten LEANS-Rechnung uebernehmen.
   - Rechnungsnummer, Datum und Bankverbindung als rote Platzhalter lassen; Nummern erst beim Versand vergeben, damit keine Nummer doppelt vergeben wird.
   - Preise aus frueheren Rechnungen an denselben Kunden oder aus der internen Preisregel ableiten und die Quelle nennen.
   - Am Ende jedes Entwurfs einen Abschnitt „Pruefhinweise (intern, vor Versand loeschen)“ mit Quellen-Links, Luecken und offenen Fragen.
6. **Ablage:** Einen Ordner „Rechnungsentwuerfe JJJJ-MM-TT“ im Google Drive anlegen, dazu ein Uebersichtsdokument mit Kurzfassung, Tabelle der Entwuerfe, Gesamtliste offener Rechnungen und Fragen an Semir. Nichts davon ins Repository (siehe [[../decisions/2026-09-28-keine-kundendaten-im-repo]]).
7. **Nichts versenden.** Entwuerfe bleiben Entwuerfe, bis Semir sie freigibt.

## Rechenregeln

- Umsatzsteuer je Position runden und die Positionsbetraege summieren, wie auf den bisherigen Rechnungen.
- Werkzeug und Energiezuschlaege aus Grosshaendler-Rechnungen nicht als Material weiterberechnen.
- Bei fehlenden Stunden keine Zahl erfinden: Platzhalter setzen und Summen fuer mehrere Stundenszenarien zeigen.
