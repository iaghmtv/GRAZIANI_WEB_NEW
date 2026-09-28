r"""Publica 02 SITIO NUEVO en el hosting oficial (hidraembotelladora.com, /public_html) por FTP-TLS.

  python ftp_publicar.py              simulación: lista qué se subiría (no toca el servidor)
  python ftp_publicar.py --publicar   backup de lo que se va a pisar + subida + verificación de tamaños

- Sube solo lo nuevo o distinto: compara byte a byte cada archivo con el backup del servidor
  (01 SITIO ORIGINAL (backup FTP 2026-09-23)\public_html, que coincide con el servidor: ver inventario_2026-09-28.json).
- NUNCA borra nada del servidor (lo que ya no se usa queda como está).
- Antes de pisar un archivo existente lo baja a 00 HERRAMIENTAS\backup_predeploy_<fecha>\public_html\...
- No sube archivos de trabajo (capturas, prototipos, hojas de preview) ni cgi-bin / .htaccess / .well-known.
- Credenciales: se leen del .ENV y no se imprimen.
"""
import re, ftplib, os, sys, filecmp, datetime

ENV = r"E:\GRACIANI\WEB GRAZIANI\GRAZIANI WEB DATA.ENV"
LOCAL = r"E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO"
SERVIDOR_BACKUP = r"E:\GRACIANI\WEB GRAZIANI\01 SITIO ORIGINAL (backup FTP 2026-09-23)\public_html"
AQUI = os.path.dirname(os.path.abspath(__file__))
FECHA = datetime.date.today().isoformat()
PREDEPLOY = os.path.join(AQUI, f"backup_predeploy_{FECHA}", "public_html")
LOG = os.path.join(AQUI, f"publicacion_{FECHA}.log")
ROOT = "/public_html"

EXCLUIR_ARCHIVOS = {"_captura_movil.html", "_captura_productos.html", "hero.html", "pagina-anterior.html",
                    ".htaccess", ".DS_Store", "Thumbs.db", "desktop.ini"}
EXCLUIR_CARPETAS = {"cgi-bin", ".well-known", ".git"}
EXCLUIR_PATRON = re.compile(r"^(hero_.*|pagina_completa_.*)\.jpg$")   # hojas de preview que quedaron en la raíz

def lista_a_subir():
    subir = []   # (relativa con /, ruta local, existe_en_servidor)
    for d, carpetas, archivos in os.walk(LOCAL):
        rel_d = os.path.relpath(d, LOCAL)
        carpetas[:] = [c for c in carpetas if c not in EXCLUIR_CARPETAS and not (rel_d == "." and c.startswith("_"))]
        for a in archivos:
            if a in EXCLUIR_ARCHIVOS or (rel_d == "." and EXCLUIR_PATRON.match(a)):
                continue
            loc = os.path.join(d, a)
            rel = os.path.normpath(os.path.join(rel_d, a)).replace("\\", "/")
            srv = os.path.join(SERVIDOR_BACKUP, rel)
            existe = os.path.exists(srv)
            if existe and filecmp.cmp(loc, srv, shallow=False):
                continue
            subir.append((rel, loc, existe))
    return sorted(subir)

subir = lista_a_subir()
pisa = [s for s in subir if s[2]]
total = sum(os.path.getsize(s[1]) for s in subir)
print(f"{len(subir)} archivos a subir ({total / 1e6:.1f} MB): {len(subir) - len(pisa)} nuevos, {len(pisa)} reemplazan a uno existente")
for rel, _, existe in subir:
    if existe or not re.search(r"/(giro|cordillera)/", rel):
        print(("  PISA  " if existe else "  nuevo ") + rel)
print("  (+ secuencias de frames nuevas en assets/hero/giro y assets/hero/cordillera)")
if "--publicar" not in sys.argv:
    print("\nSimulación: no se tocó el servidor. Para publicar: python ftp_publicar.py --publicar")
    sys.exit(0)

txt = open(ENV, encoding="utf-8", errors="replace").read()
blk = txt[txt.find("FTP"):]
host = re.search(r"host:\s*(\S+)", blk).group(1)
user = re.search(r"usr:\s*(\S+)", blk).group(1)
pw = re.search(r"psw:\s*(\S+)", blk).group(1)

def conectar():
    f = ftplib.FTP_TLS(timeout=120)
    f.connect(host, 21); f.auth(); f.login(user, pw); f.prot_p(); f.set_pasv(True)
    return f

log = open(LOG, "a", encoding="utf-8")
def anotar(t):
    print(t); log.write(t + "\n"); log.flush()

ftp = conectar()
anotar(f"== {datetime.datetime.now():%Y-%m-%d %H:%M:%S} publicación: {len(subir)} archivos, {total / 1e6:.1f} MB")

# 1) backup de lo que se va a pisar (tal cual está hoy en el servidor)
for rel, _, _ in pisa:
    dst = os.path.join(PREDEPLOY, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fh:
        ftp.retrbinary(f"RETR {ROOT}/{rel}", fh.write)
    anotar(f"backup {rel} ({os.path.getsize(dst)} B)")

# 2) subida (crea las carpetas que falten)
hechas = set()
def asegurar_carpeta(rel_dir):
    partes = [p for p in rel_dir.split("/") if p]
    for i in range(1, len(partes) + 1):
        ruta = ROOT + "/" + "/".join(partes[:i])
        if ruta in hechas:
            continue
        try:
            ftp.mkd(ruta); anotar(f"carpeta {ruta}")
        except ftplib.error_perm:
            pass
        hechas.add(ruta)

errores = []
for n, (rel, loc, existe) in enumerate(subir, 1):
    asegurar_carpeta(os.path.dirname(rel))
    for intento in range(3):
        try:
            with open(loc, "rb") as fh:
                ftp.storbinary(f"STOR {ROOT}/{rel}", fh)
            ftp.voidcmd("TYPE I")
            remoto = ftp.size(f"{ROOT}/{rel}")
            local = os.path.getsize(loc)
            if remoto != local:
                raise IOError(f"tamaño {remoto} != {local}")
            if n % 25 == 0 or existe or not re.search(r"/(giro|cordillera)/", rel):
                anotar(f"[{n}/{len(subir)}] {'pisado' if existe else 'subido'} {rel} ({local} B)")
            break
        except Exception as e:
            anotar(f"reintento {intento + 1} {rel}: {e}")
            try:
                ftp.quit()
            except Exception:
                pass
            ftp = conectar()
    else:
        errores.append(rel)

ftp.quit()
anotar(f"== fin: {len(subir) - len(errores)} ok, {len(errores)} con error {errores}")
anotar(f"backup de lo pisado: {PREDEPLOY}")
