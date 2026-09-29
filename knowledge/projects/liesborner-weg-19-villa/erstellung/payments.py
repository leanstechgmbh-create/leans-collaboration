from decimal import Decimal as D
# nr -> (gezahlt brutto oder None = nicht verifizierbar, Quelle)
ZAHLUNGEN = {
    "2024-47": (None, "nicht verifizierbar – Kontoauszüge Apr.–Jul. 2024 fehlen in Drive; nicht in OP-Liste 15.07.2026"),
    "2025-17": (D("5662.02"), "bezahlt 19.09.2025 durch CREST Living (Vwz. „R. 2025-17 v. 14.04.25, BV. Liesborner Weg 19“)"),
}

# Alle gefundenen Belege zum BV (für die Excel-Übersicht). gezahlt None = nicht verifizierbar.
BELEGE = [
    dict(nr="RE 2024-47", datum="16.04.2024", an="CREST Living GmbH & Co. KG", gewerk="Sanitärobjekte / Montage Armaturen",
         netto=12481.00, ust=2371.39, brutto=14852.39, gezahlt=None, zaehlt=True,
         status="Gültige Rechnung. Zahlung nicht verifizierbar (Kontoauszüge Apr.–Jul. 2024 fehlen); nicht in OP-Liste 15.07.2026.",
         id="1g6nY1jQ-8vG3aS5XhX6H6acuorJHnNb1"),
    dict(nr="Dok. 159", datum="03.12.2024", an="CREST Investment GmbH", gewerk="Heizung – hydraulischer Abgleich",
         netto=270.00, ust=51.30, brutto=321.30, gezahlt=0, zaehlt=True,
         status="Nur „Angebotsnummer 159“, keine Rechnungsnummer. Keine Zahlung Jan. 2025–Apr. 2026. Wird durch neue Schlussrechnung ersetzt.",
         id="1uzr4oftGcv9a1kAyKVSrmYjRWDeN_Eq5"),
    dict(nr="Dok. 176 (SR)", datum="05.01.2025", an="CREST Investment GmbH", gewerk="Fußbodenheizung (Schlussrechnung)",
         netto=18942.26, ust=3599.03, brutto=22541.30, gezahlt=0, zaehlt=True,
         status="OFFEN. Nur „Angebotsnummer 176“, keine Rechnungsnummer, falscher Empfänger. Keine Zahlung bis Apr. 2026; in OP-Liste 15.07.2026. Wird durch neue Schlussrechnung ersetzt.",
         id="1foZqeVpqvHKekiLv0qZJMnfcPezxwBKZ"),
    dict(nr="NA 175", datum="05.01.2025", an="CREST Living GmbH & Co. KG", gewerk="Nachtragsangebot Sanitärobjekte",
         netto=5605.00, ust=1064.95, brutto=6669.95, gezahlt=0, zaehlt=False,
         status="Angebot (keine Forderung).", id="1JRWNYV_kejBgctS9o1diSfqkidg0sI0D"),
    dict(nr="Dok. 175", datum="05.01.2025", an="CREST Investment", gewerk="Sanitärobjekte Nachtrag",
         netto=5605.00, ust=1064.95, brutto=6669.95, gezahlt=0, zaehlt=False,
         status="Vorversion ohne Rechnungsnummer, am 28.03.2025 als RE 2025-8 neu gestellt.", id="1rTdochXOIHlzC_eGiEUnTnm8p6fh4EVM"),
    dict(nr="RE 2025-8", datum="28.03.2025", an="CREST Investment", gewerk="Sanitärobjekte Nachtrag",
         netto=5605.00, ust=1064.95, brutto=6669.95, gezahlt=0, zaehlt=False,
         status="Inhaltlich durch RE 2025-17 (an CREST Living) ersetzt, nicht bezahlt → Stornorechnung zu 2025-8 ausstellen (USt-Ausweis!). 847,00 € netto Differenz zu 2025-17 klären.",
         id="1Wp1fnJ1YDxFhOI_ShhnBsH4_b5bpgIS-"),
    dict(nr="RE 2025-17", datum="14.04.2025", an="CREST Living GmbH & Co. KG", gewerk="Sanitärobjekte Nachtrag (korrigiert)",
         netto=4758.00, ust=904.02, brutto=5662.02, gezahlt=5662.02, zaehlt=True,
         status="Bezahlt 19.09.2025 durch CREST Living.", id="1Qbcqk--Kr-13q1xiiQopgAto4NLtN_Rj"),
]
