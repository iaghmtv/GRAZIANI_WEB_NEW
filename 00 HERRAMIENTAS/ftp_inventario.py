"""Inventario recursivo de /public_html del hosting Graziani por FTP-TLS.
Lee las credenciales del .ENV, lista todo y guarda inventario.json junto a este script.
Uso:  python ftp_inventario.py
"""
import re, json, ftplib, os

ENV = r"E:\GRACIANI\WEB GRAZIANI\GRAZIANI WEB DATA.ENV"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventario.json")
ROOT = "/public_html"

txt = open(ENV, encoding="utf-8", errors="replace").read()
blk = txt[txt.find("FTP"):]
host = re.search(r"host:\s*(\S+)", blk).group(1)
user = re.search(r"usr:\s*(\S+)", blk).group(1)
pw   = re.search(r"psw:\s*(\S+)", blk).group(1)

ftp = ftplib.FTP_TLS(timeout=60)
ftp.connect(host, 21)
ftp.auth()
ftp.login(user, pw)
ftp.prot_p()
ftp.set_pasv(True)
print("Conectado:", ftp.getwelcome().splitlines()[0])

entries = []  # [ruta, tipo, tamaño, modificado]
def walk(path):
    for name, facts in ftp.mlsd(path, facts=["type", "size", "modify"]):
        if name in (".", ".."):
            continue
        full = path.rstrip("/") + "/" + name
        t = facts.get("type", "?")
        entries.append([full, t, int(facts.get("size", 0) or 0), facts.get("modify", "")])
        if t == "dir":
            walk(full)

walk(ROOT)
ftp.quit()

json.dump(entries, open(OUT, "w", encoding="utf-8"), indent=0)
files = [e for e in entries if e[1] == "file"]
dirs  = [e for e in entries if e[1] == "dir"]
print(f"{len(files)} archivos, {len(dirs)} carpetas, {sum(e[2] for e in files)/1e6:.1f} MB")
print("Inventario guardado en:", OUT)
