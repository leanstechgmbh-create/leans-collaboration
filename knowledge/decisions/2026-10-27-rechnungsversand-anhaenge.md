# Entscheidung: Anhänge beim Rechnungsversand

- Datum: 2026-10-27
- Von: Semir Redzic
- Gilt für: jeden Chat und jeden Assistenten, jeden Versandweg (IONOS info@/sr@, Gmail)

## Regel

1. Die Rechnung wird immer als eigene, normale PDF angehängt. Nie in eine ZIP.
2. Alle zusätzlichen Dateien zur Rechnung (Aufmaß, Stundenzettel, Fotos, Lieferscheine, Nachweise,
   Abnahmeprotokolle) werden zusammen in genau eine ZIP gepackt, damit die Mail klein bleibt.
3. ZIP-Name: „Anlagen <Betreff>.zip“, z. B. „Anlagen Rechnung 2026-60 BV Teststr. 1.zip“.
4. Zusammen max. 25 MB. Darüber: ZIP in Drive ablegen und den Link in den Mailtext setzen.

## Umsetzung

- `scripts/leans-mail.py`: Rechnung mit `--anhang rechnung.pdf`, Zusatzdateien mit `--zusatz datei` (mehrfach),
  das Skript baut die ZIP selbst. Optional `--zip-name`.
- Gmail-Weg: ZIP vorher mit `zip -j "Anlagen <Betreff>.zip" datei1 datei2` bauen und beide als `attachments` mitgeben.
- Skills `/senden` und `/mail-entwurf` verweisen auf diese Regel.
