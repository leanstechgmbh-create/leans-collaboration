#!/usr/bin/env python3
"""LEANS Mailversand als info@ oder sr@leanstech-gmbh.de ueber den IONOS-Mailserver.

Funktioniert in jedem Chat, sobald in der Cloud-Umgebung zwei Dinge gesetzt sind:
  1. Netzwerk: smtp.ionos.de unter "Allowed domains" (Umgebung bearbeiten > Network access).
  2. Secrets:  IONOS_INFO_PASSWORD und/oder IONOS_SR_PASSWORD (Umgebung bearbeiten > Environment variables).

Aufruf:
  python3 scripts/leans-mail.py --von info --an kunde@example.de \
      --betreff "Angebot 412" --text-datei mail.txt --anhang angebot.pdf --anhang fotos.zip
  python3 scripts/leans-mail.py --von sr --an a@b.de --betreff "..." --text "Kurzer Text" --dry-run

Optionen:
  --von info|sr            Absenderadresse (info@ oder sr@leanstech-gmbh.de)
  --an ADRESSE             Empfaenger, mehrfach moeglich
  --cc ADRESSE             Kopie, mehrfach moeglich
  --betreff TEXT           Betreff
  --text TEXT              Mailtext (Klartext) ODER --text-datei DATEI
  --anhang DATEI           Anhang, mehrfach moeglich (zusammen max. 25 MB)
  --antwort-auf MSGID      Message-ID der Kundenmail fuer die Thread-Zuordnung (optional)
  --dry-run                Nur anzeigen, nichts senden

Exit-Codes: 0 gesendet, 2 Konfiguration fehlt, 3 Netz/Server nicht erreichbar, 4 Anmeldung abgelehnt.
"""
import argparse
import mimetypes
import os
import smtplib
import socket
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

SMTP_HOST = "smtp.ionos.de"
SMTP_PORT = 587
ABSENDER = {
    "info": ("info@leanstech-gmbh.de", "IONOS_INFO_PASSWORD"),
    "sr": ("sr@leanstech-gmbh.de", "IONOS_SR_PASSWORD"),
}
ANZEIGENAME = "LEANS Tech GmbH"
SIGNATUR = (
    "\n\nFreundliche Grüße\nSemir Redzic\nLEANS Tech GmbH\n"
    "Klima ▪ Lüftung ▪ Sanitär ▪ Heizung\nTel: +49 152 16607036\n"
    "info@leanstech-gmbh.de\nwww.leanstechgmbh-hkls.de\n"
)
MAX_BYTES = 25 * 1024 * 1024


def fehler(code: int, text: str) -> None:
    print(f"FEHLER: {text}", file=sys.stderr)
    sys.exit(code)


def baue_nachricht(args: argparse.Namespace, absender: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((ANZEIGENAME, absender))
    msg["To"] = ", ".join(args.an)
    if args.cc:
        msg["Cc"] = ", ".join(args.cc)
    msg["Subject"] = args.betreff
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="leanstech-gmbh.de")
    if args.antwort_auf:
        msg["In-Reply-To"] = args.antwort_auf
        msg["References"] = args.antwort_auf
    text = args.text if args.text is not None else Path(args.text_datei).read_text(encoding="utf-8")
    if "Freundliche Grüße" not in text:
        text = text.rstrip() + SIGNATUR
    msg.set_content(text)

    gesamt = 0
    for pfad in args.anhang or []:
        p = Path(pfad)
        if not p.is_file():
            fehler(2, f"Anhang nicht gefunden: {p}")
        daten = p.read_bytes()
        gesamt += len(daten)
        if gesamt > MAX_BYTES:
            fehler(2, "Anhaenge zusammen groesser als 25 MB. Datei in Drive ablegen und Link in den Text setzen.")
        typ, _ = mimetypes.guess_type(p.name)
        haupt, unter = (typ or "application/octet-stream").split("/", 1)
        msg.add_attachment(daten, maintype=haupt, subtype=unter, filename=p.name)
    return msg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--von", choices=ABSENDER.keys(), required=True)
    ap.add_argument("--an", action="append", required=True)
    ap.add_argument("--cc", action="append")
    ap.add_argument("--betreff", required=True)
    gruppe = ap.add_mutually_exclusive_group(required=True)
    gruppe.add_argument("--text")
    gruppe.add_argument("--text-datei")
    ap.add_argument("--anhang", action="append")
    ap.add_argument("--antwort-auf")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    absender, secret_name = ABSENDER[args.von]
    passwort = os.environ.get(secret_name, "")
    if not passwort and not args.dry_run:
        fehler(2, f"Secret {secret_name} fehlt. In der Cloud-Umgebung unter Environment variables setzen.")

    msg = baue_nachricht(args, absender)
    print(f"Von: {absender}\nAn: {msg['To']}\nCc: {msg.get('Cc', '')}\nBetreff: {msg['Subject']}")
    print("Anhaenge:", ", ".join(Path(a).name for a in (args.anhang or [])) or "keine")
    if args.dry_run:
        print("--- dry-run, nichts gesendet ---")
        return

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            try:
                smtp.login(absender, passwort)
            except smtplib.SMTPAuthenticationError as e:
                fehler(4, f"IONOS lehnt die Anmeldung fuer {absender} ab ({e.smtp_code}). Passwort im Secret {secret_name} pruefen.")
            smtp.send_message(msg)
    except (socket.gaierror, OSError, smtplib.SMTPConnectError) as e:
        fehler(3, f"{SMTP_HOST}:{SMTP_PORT} nicht erreichbar ({e}). In der Cloud-Umgebung smtp.ionos.de unter Allowed domains eintragen.")
    print(f"GESENDET als {absender}, Message-ID {msg['Message-ID']}")


if __name__ == "__main__":
    main()
