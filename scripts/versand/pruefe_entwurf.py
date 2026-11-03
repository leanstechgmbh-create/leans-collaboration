#!/usr/bin/env python3
"""Prüft die Anhänge eines Gmail-Entwurfs bitgenau gegen die Originaldateien.

Eingabe: die gespeicherte Ausgabe von `mcp Gmail get_draft messageFormat=RAW` (JSON mit Feld `raw`)
und ein Ordner mit den Original-PDFs. Auch Dateien in ZIP-Anhängen werden geprüft.

  python3 -I pruefe_entwurf.py <get_draft-ausgabe.txt> <ordner-mit-originalen>

Rückgabe 0, wenn jeder Anhang (und jede Datei in jeder ZIP) einem Original entspricht.
"""

import base64
import email
import hashlib
import io
import json
import sys
import zipfile
from email import policy
from pathlib import Path


def sha(daten):
    return hashlib.sha256(daten).hexdigest()


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    roh = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["raw"]
    roh += "=" * (-len(roh) % 4)
    mail = email.message_from_bytes(base64.urlsafe_b64decode(roh), policy=policy.default)
    originale = {sha(p.read_bytes()): p.name for p in Path(sys.argv[2]).iterdir() if p.is_file()}

    print(f"Betreff: {mail['Subject']}\nAn: {mail['To']}\nVon: {mail['From']}")
    fehler = 0
    anzahl = 0
    for anhang in mail.iter_attachments():
        anzahl += 1
        daten = anhang.get_content()
        name = anhang.get_filename()
        if name.lower().endswith(".zip"):
            z = zipfile.ZipFile(io.BytesIO(daten))
            kaputt = z.testzip()
            print(f"  ZIP {name}: {'OK' if kaputt is None else 'DEFEKT bei ' + kaputt}")
            fehler += kaputt is not None
            for eintrag in z.infolist():
                treffer = originale.get(sha(z.read(eintrag)))
                print(f"    {'OK ' if treffer else 'FEHLT'} {eintrag.filename} ({eintrag.file_size} B){' = ' + treffer if treffer else ''}")
                fehler += not treffer
        else:
            treffer = originale.get(sha(daten))
            print(f"  {'OK ' if treffer else 'FEHLT'} {name} ({len(daten)} B){' = ' + treffer if treffer else ''}")
            fehler += not treffer
    if anzahl == 0:
        print("  Keine Anhänge im Entwurf.")
        return 1
    print("Ergebnis:", "alles bitgenau" if fehler == 0 else f"{fehler} Abweichung(en)")
    return 0 if fehler == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
