#!/usr/bin/env python3
"""Legt E-Mail-Entwürfe mit Anhängen direkt im IONOS-Postfach info@leanstech-gmbh.de an.

Sendet NIE: Die Mails landen per IMAP im Ordner „Entwürfe“. Semir prüft und sendet selbst.

Zugangsdaten nur über Umgebungsvariablen, nie im Code oder im Chat:
  IONOS_INFO_PASSWORD   Passwort des Postfachs (Pflicht, außer bei --probe)
  IONOS_INFO_USER       Standard: info@leanstech-gmbh.de
  IONOS_IMAP_HOST       Standard: imap.ionos.de

Läuft auf dem PC direkt und in der Claude-Cloud über den Proxy aus HTTPS_PROXY
(dort muss imap.ionos.de unter „Allowed domains“ der Umgebung stehen).

Beispiele:
  python entwuerfe_anlegen.py rauch_we221.json --dateien ./pdf --probe     # nur Dateien prüfen, .eml schreiben
  python entwuerfe_anlegen.py rauch_we221.json --dateien ./pdf             # Entwürfe in info@ anlegen
"""

import argparse
import base64
import imaplib
import json
import mimetypes
import os
import socket
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from urllib.parse import urlparse

CA_BUNDLE = "/root/.ccr/ca-bundle.crt"


def ssl_kontext():
    ctx = ssl.create_default_context()
    if os.path.exists(CA_BUNDLE):
        ctx.load_verify_locations(CA_BUNDLE)
    return ctx


def proxy_tunnel(host, port, timeout=30):
    """Öffnet über HTTPS_PROXY einen CONNECT-Tunnel zu host:port; ohne Proxy direkt."""
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if not proxy:
        return socket.create_connection((host, port), timeout=timeout)
    p = urlparse(proxy)
    sock = socket.create_connection((p.hostname, p.port or 8080), timeout=timeout)
    sock.sendall(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n".encode())
    antwort = b""
    while b"\r\n\r\n" not in antwort:
        teil = sock.recv(4096)
        if not teil:
            break
        antwort += teil
    statuszeile = antwort.split(b"\r\n", 1)[0].decode(errors="replace")
    if " 200 " not in statuszeile + " ":
        sock.close()
        raise ConnectionError(f"Proxy lässt {host}:{port} nicht durch: {statuszeile}")
    return sock


class IMAP4_SSL_Proxy(imaplib.IMAP4_SSL):
    def _create_socket(self, timeout):
        roh = proxy_tunnel(self.host, self.port, timeout or 30)
        return self.ssl_context.wrap_socket(roh, server_hostname=self.host)


def imap_utf7_decode(name):
    """Dekodiert IMAP-Ordnernamen (modified UTF-7), z. B. Entw&APw-rfe -> Entwürfe."""
    out, i = [], 0
    while i < len(name):
        if name[i] == "&":
            j = name.index("-", i)
            if j == i + 1:
                out.append("&")
            else:
                b64 = name[i + 1:j].replace(",", "/")
                b64 += "=" * (-len(b64) % 4)
                out.append(base64.b64decode(b64).decode("utf-16-be"))
            i = j + 1
        else:
            out.append(name[i])
            i += 1
    return "".join(out)


def entwuerfe_ordner(imap):
    typ, zeilen = imap.list()
    if typ != "OK":
        raise RuntimeError("Ordnerliste nicht lesbar")
    kandidaten = []
    for z in zeilen:
        z = z.decode(errors="replace")
        flags = z[z.find("(") + 1:z.find(")")]
        roh = z.rsplit(" ", 1)[-1].strip('"')
        if "\\Drafts" in flags:
            return roh
        kandidaten.append(roh)
    for roh in kandidaten:
        if imap_utf7_decode(roh).lower() in ("entwürfe", "drafts", "entwurf"):
            return roh
    raise RuntimeError("Kein Entwürfe-Ordner gefunden: " + ", ".join(imap_utf7_decode(k) for k in kandidaten))


def lade(url, ziel):
    """Lädt ein Datenblatt aus dem Internet; nur echte PDFs werden behalten."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60, context=ssl_kontext()) as r:
            daten = r.read()
        if daten[:5] == b"%PDF-":
            ziel.parent.mkdir(parents=True, exist_ok=True)
            ziel.write_bytes(daten)
        else:
            print(f"    {url}: kein PDF erhalten")
    except Exception as e:  # Netzwerk gesperrt, 404 usw.
        print(f"    {url}: nicht ladbar ({e})")


def baue_mail(spec, mail, dateien_dir):
    msg = EmailMessage()
    msg["From"] = formataddr((spec.get("absender_name", ""), spec["absender"]))
    msg["To"] = ", ".join(mail["an"])
    msg["Subject"] = mail["betreff"]
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=spec["absender"].split("@")[1])
    msg.set_content(mail["text"])
    fehlend = []
    for a in mail["anhaenge"]:
        pfad = dateien_dir / a["datei"]
        if not pfad.is_file() and a.get("quelle", "").startswith("http"):
            lade(a["quelle"], pfad)
        if not pfad.is_file():
            fehlend.append(a["datei"])
            continue
        typ = mimetypes.guess_type(a["name"])[0] or "application/octet-stream"
        haupt, unter = typ.split("/", 1)
        msg.add_attachment(pfad.read_bytes(), maintype=haupt, subtype=unter, filename=a["name"])
    return msg, fehlend


def schon_da(imap, ordner, betreff):
    imap.select(ordner, readonly=True)
    # Betreff enthält Umlaute und Gedankenstriche: als UTF-8-Literal suchen
    imap.literal = betreff.encode("utf-8")
    typ, daten = imap.search("UTF-8", "SUBJECT")
    return typ == "OK" and bool(daten and daten[0].split())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="JSON mit Absender und Mails")
    ap.add_argument("--dateien", required=True, help="Ordner mit den Anhängen")
    ap.add_argument("--probe", action="store_true", help="nur prüfen und .eml-Dateien schreiben, nichts hochladen")
    ap.add_argument("--nur", nargs="*", help="nur diese Mail-Kennungen (z. B. klima sanitaer)")
    ap.add_argument("--ohne-fehlende", action="store_true", help="Mail trotzdem anlegen, wenn ein Anhang fehlt")
    ap.add_argument("--doppelt-erlaubt", action="store_true", help="auch anlegen, wenn ein Entwurf mit gleichem Betreff schon da ist")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    dateien_dir = Path(args.dateien)
    mails = [m for m in spec["mails"] if not args.nur or m["kennung"] in args.nur]

    gebaut = []
    for m in mails:
        msg, fehlend = baue_mail(spec, m, dateien_dir)
        anz = sum(1 for _ in msg.iter_attachments())
        groesse = len(msg.as_bytes())
        print(f"[{m['kennung']}] {m['betreff']}\n    Anhänge: {anz}/{len(m['anhaenge'])}, Größe {groesse / 1e6:.1f} MB")
        if fehlend:
            print("    FEHLT: " + ", ".join(fehlend))
            if not args.ohne_fehlende:
                print("    -> übersprungen (mit --ohne-fehlende trotzdem anlegen)")
                continue
        gebaut.append((m, msg))

    if args.probe:
        aus = Path("probe-eml")
        aus.mkdir(exist_ok=True)
        for m, msg in gebaut:
            (aus / f"{m['kennung']}.eml").write_bytes(msg.as_bytes())
        print(f"Probe: {len(gebaut)} Mails als .eml in {aus}/ geschrieben, nichts hochgeladen.")
        return 0

    passwort = os.environ.get("IONOS_INFO_PASSWORD")
    if not passwort:
        print("IONOS_INFO_PASSWORD fehlt (Umgebungsvariable).", file=sys.stderr)
        return 2
    user = os.environ.get("IONOS_INFO_USER", spec["absender"])
    host = os.environ.get("IONOS_IMAP_HOST", "imap.ionos.de")

    imap = IMAP4_SSL_Proxy(host, 993, ssl_context=ssl_kontext())
    imap.login(user, passwort)
    ordner = entwuerfe_ordner(imap)
    print(f"Angemeldet als {user}, Entwürfe-Ordner: {imap_utf7_decode(ordner)}")
    for m, msg in gebaut:
        if not args.doppelt_erlaubt and schon_da(imap, ordner, m["betreff"]):
            print(f"[{m['kennung']}] liegt schon in den Entwürfen, nicht doppelt angelegt.")
            continue
        typ, daten = imap.append(ordner, "(\\Draft \\Seen)", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        print(f"[{m['kennung']}] Entwurf angelegt: {typ} {daten}")
    imap.logout()
    print("Fertig. Nichts gesendet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
