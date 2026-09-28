r"""Verifica por HTTPS que el sitio oficial sirve lo que publicó ftp_publicar.py.

  python verificar_publicacion.py

Para cada archivo que ftp_publicar.py sube (mismas exclusiones), pide https://hidraembotelladora.com/<ruta> y
compara el tamaño (Content-Length) con el local; informa también el Content-Type de las imágenes WebP.
"""
import os, re, sys, filecmp, urllib.request, concurrent.futures

BASE_URL = "https://hidraembotelladora.com/"
LOCAL = r"E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO"
SERVIDOR_BACKUP = r"E:\GRACIANI\WEB GRAZIANI\01 SITIO ORIGINAL (backup FTP 2026-09-23)\public_html"
EXCLUIR_ARCHIVOS = {"_captura_movil.html", "_captura_productos.html", "hero.html", "pagina-anterior.html",
                    ".htaccess", ".DS_Store", "Thumbs.db", "desktop.ini"}
EXCLUIR_CARPETAS = {"cgi-bin", ".well-known", ".git"}
EXCLUIR_PATRON = re.compile(r"^(hero_.*|pagina_completa_.*)\.jpg$")

rutas = []
for d, carpetas, archivos in os.walk(LOCAL):
    rel_d = os.path.relpath(d, LOCAL)
    carpetas[:] = [c for c in carpetas if c not in EXCLUIR_CARPETAS and not (rel_d == "." and c.startswith("_"))]
    for a in archivos:
        if a in EXCLUIR_ARCHIVOS or (rel_d == "." and EXCLUIR_PATRON.match(a)):
            continue
        loc = os.path.join(d, a)
        rel = os.path.normpath(os.path.join(rel_d, a)).replace("\\", "/")
        srv = os.path.join(SERVIDOR_BACKUP, rel)
        if os.path.exists(srv) and filecmp.cmp(loc, srv, shallow=False):
            continue
        rutas.append((rel, os.path.getsize(loc)))

def pedir(item):
    rel, tam = item
    url = BASE_URL + urllib.parse.quote(rel) + "?verif=1"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 verificacion-graziani"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return rel, r.status, int(r.headers.get("Content-Length", -1)), r.headers.get("Content-Type", ""), tam
    except Exception as e:
        return rel, str(e), -1, "", tam

import urllib.parse
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(pedir, rutas))
mal = [r for r in res if r[1] != 200 or r[2] != r[4]]
tipos = sorted({(os.path.splitext(r[0])[1], r[3]) for r in res})
print(f"{len(res)} archivos consultados, {len(res) - len(mal)} OK (200 y mismo tamaño), {len(mal)} con diferencias")
for r in mal[:30]:
    print("  MAL", r)
print("tipos servidos:", tipos)
sys.exit(1 if mal else 0)
