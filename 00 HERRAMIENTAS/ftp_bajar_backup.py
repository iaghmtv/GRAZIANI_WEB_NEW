"""Baja una copia exacta de /public_html del hosting Graziani por FTP-TLS.
Usa inventario.json (correr antes ftp_inventario.py). Verifica tamaños y conserva fechas del servidor.
Uso:  python ftp_bajar_backup.py [carpeta_destino]
      (sin argumento, crea "01 SITIO ORIGINAL (backup FTP AAAA-MM-DD)" con la fecha de hoy)
"""
import re, json, ftplib, os, sys, time
from datetime import date

ENV = r"E:\GRACIANI\WEB GRAZIANI\GRAZIANI WEB DATA.ENV"
INV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventario.json")
DEST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    r"E:\GRACIANI\WEB GRAZIANI", f"01 SITIO ORIGINAL (backup FTP {date.today().isoformat()})")

txt = open(ENV, encoding="utf-8", errors="replace").read()
blk = txt[txt.find("FTP"):]
host = re.search(r"host:\s*(\S+)", blk).group(1)
user = re.search(r"usr:\s*(\S+)", blk).group(1)
pw   = re.search(r"psw:\s*(\S+)", blk).group(1)

entries = json.load(open(INV, encoding="utf-8"))
ftp = ftplib.FTP_TLS(timeout=120)
ftp.connect(host, 21)
ftp.auth()
ftp.login(user, pw)
ftp.prot_p()
ftp.set_pasv(True)
print("Destino:", DEST)

for path, t, size, mod in entries:
    if t == "dir":
        os.makedirs(os.path.join(DEST, path.lstrip("/")), exist_ok=True)

ok, bad, total = 0, [], 0
t0 = time.time()
for path, t, size, mod in entries:
    if t != "file":
        continue
    local = os.path.join(DEST, path.lstrip("/"))
    os.makedirs(os.path.dirname(local), exist_ok=True)
    try:
        with open(local, "wb") as f:
            ftp.retrbinary("RETR " + path, f.write, blocksize=65536)
        got = os.path.getsize(local)
        if got != size:
            bad.append((path, size, got))
        else:
            ok += 1
            total += got
        if mod:
            ts = time.mktime(time.strptime(mod[:14], "%Y%m%d%H%M%S"))
            os.utime(local, (ts, ts))
    except Exception as e:
        bad.append((path, size, str(e)))
ftp.quit()
print(f"OK {ok} archivos, {total/1e6:.1f} MB en {time.time()-t0:.0f}s")
print("Con problemas:", bad if bad else "ninguno")
