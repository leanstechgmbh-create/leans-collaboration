#!/usr/bin/env python3
"""LEANS Mailversand als info@ oder sr@leanstech-gmbh.de ueber den IONOS-Mailserver.

Funktioniert in jedem Chat, sobald in der Cloud-Umgebung zwei Dinge gesetzt sind:
  1. Netzwerk: smtp.ionos.de unter "Allowed domains" (Umgebung bearbeiten > Network access).
  2. Secrets:  IONOS_INFO_PASSWORD und/oder IONOS_SR_PASSWORD (Umgebung bearbeiten > Environment variables).

Aufruf (senden):
  python3 scripts/leans-mail.py --von info --an kunde@example.de \
      --betreff "Angebot 412" --text-datei mail.txt --anhang angebot.pdf --anhang fotos.zip
  python3 scripts/leans-mail.py --von sr --an a@b.de --betreff "..." --text "Kurzer Text" --dry-run

Aufruf (lesen, Postfach info@ oder sr@ direkt bei IONOS, auch Gesendet):
  python3 scripts/leans-mail.py lesen --konto info --ordner INBOX --tage 7
  python3 scripts/leans-mail.py lesen --konto sr --ordner Sent --tage 30 --suche "Angebot 412"
  python3 scripts/leans-mail.py lesen --konto info --ordner INBOX --uid 1234 --volltext
  python3 scripts/leans-mail.py lesen --konto info --ordner-liste

Aufruf (Test aller drei Konten: IMAP-Anmeldung, Posteingang, Gesendet, SMTP-Anmeldung; sendet NICHTS):
  python3 scripts/leans-mail.py test
  python3 scripts/leans-mail.py test --konto sr

Unter Windows "python" statt "python3". Einrichtung am PC: scripts/mail-einrichten.ps1.

Optionen:
  --von info|sr            Absenderadresse (info@ oder sr@leanstech-gmbh.de)
  --an ADRESSE             Empfaenger, mehrfach moeglich
  --cc ADRESSE             Kopie, mehrfach moeglich
  --betreff TEXT           Betreff
  --text TEXT              Mailtext (Klartext) ODER --text-datei DATEI
  --anhang DATEI           Anhang einzeln (z. B. die Rechnung als PDF), mehrfach moeglich
  --zusatz DATEI           Zusatzdatei (Aufmass, Fotos, Nachweise), mehrfach; alle werden in EINE ZIP gepackt
  --zip-name NAME          Name der ZIP (Standard: "Anlagen <Betreff>.zip")

REGEL RECHNUNGSVERSAND (Semir, 27.10.2026): Rechnung immer als eigene PDF per --anhang,
alle weiteren Dateien per --zusatz, die landen zusammen in einer ZIP. Zusammen max. 25 MB.
  --antwort-auf MSGID      Message-ID der Kundenmail fuer die Thread-Zuordnung (optional)
  --dry-run                Nur anzeigen, nichts senden

Exit-Codes: 0 gesendet, 2 Konfiguration fehlt, 3 Netz/Server nicht erreichbar, 4 Anmeldung abgelehnt.
"""
import argparse
import email
import email.header
import imaplib
import mimetypes
import os
import re
import smtplib
import socket
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

SMTP_PORT = 587
IMAP_PORT = 993
# Konto -> (Adresse, Secret, SMTP-Host, IMAP-Host). Gmail braucht ein App-Passwort
# (Google-Konto -> Sicherheit -> Bestaetigung in zwei Schritten -> App-Passwoerter).
ABSENDER = {
    "info": ("info@leanstech-gmbh.de", "IONOS_INFO_PASSWORD", "smtp.ionos.de", "imap.ionos.de"),
    "sr": ("sr@leanstech-gmbh.de", "IONOS_SR_PASSWORD", "smtp.ionos.de", "imap.ionos.de"),
    "gmail": ("leanstechgmbh@gmail.com", "GMAIL_APP_PASSWORD", "smtp.gmail.com", "imap.gmail.com"),
}
ANZEIGENAME = "LEANS Tech GmbH"
SIGNATUR = (
    "\n\nFreundliche Grüße\nSemir Redzic\nLEANS Tech GmbH\n"
    "Klima ▪ Lüftung ▪ Sanitär ▪ Heizung\nTel: +49 152 16607036\n"
    "info@leanstech-gmbh.de\nwww.leanstechgmbh-hkls.de\n"
)
MAX_BYTES = 25 * 1024 * 1024
# Namen des Gesendet-Ordners, falls der Server ihn nicht per SPECIAL-USE (\\Sent) kennzeichnet.
GESENDET_KANDIDATEN = ("Gesendete Objekte", "Sent", "Sent Items", "Gesendet", "INBOX.Sent",
                       "[Gmail]/Gesendet", "[Gmail]/Sent Mail")


class KontoFehler(Exception):
    def __init__(self, code: int, text: str):
        super().__init__(text)
        self.code = code


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
    anhaenge = list(args.anhang or [])
    if args.zusatz:
        import tempfile
        import zipfile
        zip_name = args.zip_name or ("Anlagen " + re.sub(r'[\\/:*?"<>|]+', "-", args.betreff).strip() + ".zip")
        if not zip_name.lower().endswith(".zip"):
            zip_name += ".zip"
        zip_pfad = Path(tempfile.mkdtemp()) / zip_name
        with zipfile.ZipFile(zip_pfad, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for pfad in args.zusatz:
                p = Path(pfad)
                if not p.is_file():
                    fehler(2, f"Zusatzdatei nicht gefunden: {p}")
                z.write(p, arcname=p.name)
        anhaenge.append(str(zip_pfad))
        print(f"ZIP gebaut: {zip_name} ({zip_pfad.stat().st_size // 1024} KB, {len(args.zusatz)} Dateien)")
    for pfad in anhaenge:
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


def _dekodiere(wert) -> str:
    if wert is None:
        return ""
    teile = email.header.decode_header(str(wert))
    out = []
    for text, zeichensatz in teile:
        if isinstance(text, bytes):
            out.append(text.decode(zeichensatz or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def _textkoerper(nachricht) -> str:
    if nachricht.is_multipart():
        for teil in nachricht.walk():
            if teil.get_content_type() == "text/plain" and not teil.get_filename():
                return teil.get_payload(decode=True).decode(teil.get_content_charset() or "utf-8", errors="replace")
        for teil in nachricht.walk():
            if teil.get_content_type() == "text/html" and not teil.get_filename():
                html = teil.get_payload(decode=True).decode(teil.get_content_charset() or "utf-8", errors="replace")
                return re.sub(r"<[^>]+>", " ", html)
        return ""
    return nachricht.get_payload(decode=True).decode(nachricht.get_content_charset() or "utf-8", errors="replace")


def _passwort(schluessel: str) -> str:
    _, secret_name, _, _ = ABSENDER[schluessel]
    passwort = os.environ.get(secret_name, "")
    if schluessel == "gmail":
        passwort = passwort.replace(" ", "")  # Google zeigt App-Passwoerter in Vierergruppen an
    return passwort


def _imap_verbinden(schluessel: str) -> imaplib.IMAP4_SSL:
    konto, secret_name, _, imap_host = ABSENDER[schluessel]
    passwort = _passwort(schluessel)
    if not passwort:
        raise KontoFehler(2, f"Secret {secret_name} fehlt. Am PC: scripts/mail-einrichten.ps1, in der Cloud: Environment variables.")
    try:
        imap = imaplib.IMAP4_SSL(imap_host, IMAP_PORT, ssl_context=ssl.create_default_context(), timeout=30)
    except (socket.gaierror, OSError) as e:
        raise KontoFehler(3, f"{imap_host}:{IMAP_PORT} nicht erreichbar ({e}). In der Cloud-Umgebung {imap_host} unter Allowed domains eintragen.")
    try:
        imap.login(konto, passwort)
    except imaplib.IMAP4.error as e:
        raise KontoFehler(4, f"{imap_host} lehnt die Anmeldung fuer {konto} ab ({e}). Passwort im Secret {secret_name} pruefen.")
    return imap


def _finde_gesendet(imap: imaplib.IMAP4_SSL):
    """Gesendet-Ordner ermitteln: zuerst per SPECIAL-USE-Kennzeichen \\Sent, dann ueber bekannte Namen."""
    status, zeilen = imap.list()
    namen = []
    for zeile in zeilen or []:
        if not isinstance(zeile, bytes):
            continue
        m = re.match(r'\((?P<flags>[^)]*)\) (?:"[^"]*"|NIL) (?P<name>.+)$', zeile.decode(errors="replace"))
        if not m:
            continue
        name = m.group("name").strip()
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        if "\\sent" in m.group("flags").lower():
            return name
        namen.append(name)
    for kandidat in GESENDET_KANDIDATEN:
        if kandidat in namen:
            return kandidat
    return None


def _waehle_ordner(imap: imaplib.IMAP4_SSL, wunsch: str):
    if wunsch.lower() in ("sent", "gesendet"):
        gesendet = _finde_gesendet(imap)
        if gesendet and imap.select(f'"{gesendet}"', readonly=True)[0] == "OK":
            return gesendet
    if imap.select(f'"{wunsch}"', readonly=True)[0] == "OK":
        return wunsch
    return None


def lesen(args: argparse.Namespace) -> None:
    konto = ABSENDER[args.konto][0]
    try:
        imap = _imap_verbinden(args.konto)
    except KontoFehler as e:
        fehler(e.code, str(e))

    if args.ordner_liste:
        status, ordner = imap.list()
        for zeile in ordner or []:
            print(zeile.decode(errors="replace"))
        imap.logout()
        return

    ordner = _waehle_ordner(imap, args.ordner)
    if ordner is None:
        fehler(2, f"Ordner {args.ordner} nicht gefunden. Mit --ordner-liste nachsehen.")

    if args.uid:
        status, daten = imap.uid("fetch", args.uid, "(RFC822)")
        if status != "OK" or not daten or daten[0] is None:
            fehler(2, f"UID {args.uid} in {ordner} nicht gefunden.")
        nachricht = email.message_from_bytes(daten[0][1])
        print(f"Von: {_dekodiere(nachricht['From'])}\nAn: {_dekodiere(nachricht['To'])}\nCc: {_dekodiere(nachricht.get('Cc'))}")
        print(f"Datum: {nachricht['Date']}\nBetreff: {_dekodiere(nachricht['Subject'])}\nMessage-ID: {nachricht['Message-ID']}")
        anhaenge = [teil.get_filename() for teil in nachricht.walk() if teil.get_filename()]
        print("Anhaenge:", ", ".join(_dekodiere(a) for a in anhaenge) or "keine")
        if args.volltext:
            print("---")
            print(_textkoerper(nachricht))
        if args.anhang_speichern:
            ziel = Path(args.anhang_speichern)
            ziel.mkdir(parents=True, exist_ok=True)
            for teil in nachricht.walk():
                name = teil.get_filename()
                if name:
                    (ziel / _dekodiere(name)).write_bytes(teil.get_payload(decode=True))
                    print("gespeichert:", ziel / _dekodiere(name))
        imap.logout()
        return

    import datetime
    seit = (datetime.date.today() - datetime.timedelta(days=args.tage)).strftime("%d-%b-%Y")
    kriterien = ["SINCE", seit]
    if args.suche:
        kriterien += ["TEXT", f'"{args.suche}"']
    status, treffer = imap.uid("search", None, *kriterien)
    uids = (treffer[0] or b"").split()
    print(f"{konto} / {ordner}: {len(uids)} Nachrichten seit {seit}" + (f' mit "{args.suche}"' if args.suche else ""))
    for uid in uids[-args.max:]:
        status, daten = imap.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM TO DATE SUBJECT)])")
        kopf = email.message_from_bytes(daten[0][1])
        print(f"UID {uid.decode()} | {kopf['Date']} | von {_dekodiere(kopf['From'])} | an {_dekodiere(kopf['To'])} | {_dekodiere(kopf['Subject'])}")
    imap.logout()


def _smtp_anmelden(schluessel: str) -> None:
    absender, secret_name, smtp_host, _ = ABSENDER[schluessel]
    try:
        with smtplib.SMTP(smtp_host, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            try:
                smtp.login(absender, _passwort(schluessel))
            except smtplib.SMTPAuthenticationError as e:
                raise KontoFehler(4, f"{smtp_host} lehnt die Anmeldung fuer {absender} ab ({e.smtp_code}). Passwort im Secret {secret_name} pruefen.")
    except (socket.gaierror, OSError, smtplib.SMTPConnectError) as e:
        raise KontoFehler(3, f"{smtp_host}:{SMTP_PORT} nicht erreichbar ({e}). In der Cloud-Umgebung {smtp_host} unter Allowed domains eintragen.")


def test(args: argparse.Namespace) -> None:
    """Prueft je Konto Lesen (IMAP: Posteingang und Gesendet) und Senden (SMTP-Anmeldung). Sendet keine Mail."""
    import datetime
    seit = (datetime.date.today() - datetime.timedelta(days=args.tage)).strftime("%d-%b-%Y")
    alle_ok = True
    for schluessel in args.konto or list(ABSENDER):
        adresse = ABSENDER[schluessel][0]
        print(f"\n== {adresse} ==")
        try:
            imap = _imap_verbinden(schluessel)
        except KontoFehler as e:
            print(f"  Lesen:  FEHLER  {e}")
            alle_ok = False
        else:
            for wunsch in ("INBOX", "Sent"):
                ordner = _waehle_ordner(imap, wunsch)
                if ordner is None:
                    print(f"  Lesen:  FEHLER  Ordner {wunsch} nicht gefunden")
                    alle_ok = False
                    continue
                status, treffer = imap.uid("search", None, "SINCE", seit)
                anzahl = len((treffer[0] or b"").split()) if status == "OK" else "?"
                print(f"  Lesen:  OK      {ordner}: {anzahl} Mails in den letzten {args.tage} Tagen")
            imap.logout()
        if not _passwort(schluessel):
            print("  Senden: FEHLER  kein Passwort gesetzt")
            alle_ok = False
            continue
        try:
            _smtp_anmelden(schluessel)
        except KontoFehler as e:
            print(f"  Senden: FEHLER  {e}")
            alle_ok = False
        else:
            print(f"  Senden: OK      Anmeldung bei {ABSENDER[schluessel][2]} angenommen (keine Mail gesendet)")
    print("\nERGEBNIS: alles bereit" if alle_ok else "\nERGEBNIS: nicht alles bereit, siehe FEHLER oben")
    sys.exit(0 if alle_ok else 1)


def _kopie_in_gesendet(schluessel: str, msg: EmailMessage) -> None:
    """IONOS legt per SMTP gesendete Mails nicht selbst in Gesendet ab; Gmail schon. Best effort."""
    if schluessel == "gmail":
        return
    try:
        imap = _imap_verbinden(schluessel)
        gesendet = _finde_gesendet(imap)
        if not gesendet:
            raise KontoFehler(2, "Gesendet-Ordner nicht gefunden")
        imap.append(f'"{gesendet}"', "\\Seen", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        print(f"Kopie in {gesendet} abgelegt")
    except (KontoFehler, imaplib.IMAP4.error, OSError) as e:
        print(f"HINWEIS: Mail ist gesendet, aber keine Kopie in Gesendet abgelegt ({e})", file=sys.stderr)


def main() -> None:
    # Windows-Konsole: Umlaute und Signatur-Zeichen nicht mit UnicodeEncodeError abbrechen lassen
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        tp = argparse.ArgumentParser(prog="leans-mail.py test")
        tp.add_argument("--konto", choices=ABSENDER.keys(), action="append")
        tp.add_argument("--tage", type=int, default=3)
        test(tp.parse_args(sys.argv[2:]))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "lesen":
        lp = argparse.ArgumentParser(prog="leans-mail.py lesen")
        lp.add_argument("--konto", choices=ABSENDER.keys(), required=True)
        lp.add_argument("--ordner", default="INBOX", help="INBOX oder Sent (Gesendet)")
        lp.add_argument("--tage", type=int, default=14)
        lp.add_argument("--suche")
        lp.add_argument("--max", type=int, default=50)
        lp.add_argument("--uid", help="eine Nachricht komplett anzeigen")
        lp.add_argument("--volltext", action="store_true")
        lp.add_argument("--anhang-speichern", help="Zielordner fuer Anhaenge der Nachricht (--uid)")
        lp.add_argument("--ordner-liste", action="store_true")
        lesen(lp.parse_args(sys.argv[2:]))
        return

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--von", choices=ABSENDER.keys(), required=True)
    ap.add_argument("--an", action="append", required=True)
    ap.add_argument("--cc", action="append")
    ap.add_argument("--betreff", required=True)
    gruppe = ap.add_mutually_exclusive_group(required=True)
    gruppe.add_argument("--text")
    gruppe.add_argument("--text-datei")
    ap.add_argument("--anhang", action="append")
    ap.add_argument("--zusatz", action="append")
    ap.add_argument("--zip-name")
    ap.add_argument("--antwort-auf")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    absender, secret_name, smtp_host, _ = ABSENDER[args.von]
    passwort = _passwort(args.von)
    if not passwort and not args.dry_run:
        fehler(2, f"Secret {secret_name} fehlt. Am PC: scripts/mail-einrichten.ps1, in der Cloud: Environment variables.")

    msg = baue_nachricht(args, absender)
    print(f"Von: {absender}\nAn: {msg['To']}\nCc: {msg.get('Cc', '')}\nBetreff: {msg['Subject']}")
    print("Anhaenge:", ", ".join(Path(a).name for a in (args.anhang or [])) or "keine",
          "| Zusatz in ZIP:", ", ".join(Path(a).name for a in (args.zusatz or [])) or "keine")
    if args.dry_run:
        print("--- dry-run, nichts gesendet ---")
        return

    try:
        with smtplib.SMTP(smtp_host, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            try:
                smtp.login(absender, passwort)
            except smtplib.SMTPAuthenticationError as e:
                fehler(4, f"{smtp_host} lehnt die Anmeldung fuer {absender} ab ({e.smtp_code}). Passwort im Secret {secret_name} pruefen.")
            smtp.send_message(msg)
    except (socket.gaierror, OSError, smtplib.SMTPConnectError) as e:
        fehler(3, f"{smtp_host}:{SMTP_PORT} nicht erreichbar ({e}). In der Cloud-Umgebung {smtp_host} unter Allowed domains eintragen.")
    print(f"GESENDET als {absender}, Message-ID {msg['Message-ID']}")
    _kopie_in_gesendet(args.von, msg)


if __name__ == "__main__":
    main()
