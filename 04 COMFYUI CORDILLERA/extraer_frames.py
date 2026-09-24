# -*- coding: utf-8 -*-
r"""
extraer_frames.py — Pasa el clip de la cordillera (MP4 de ComfyUI) a la secuencia que scrubea el hero web.

  python extraer_frames.py salida\cordillera_tilt_20260923.mp4 [--ancho 1920] [--frames 81] [--calidad 82]

Genera:  E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO\assets\hero\cordillera\cord_000.webp ... cord_NNN.webp
Después poner la cantidad en js/hero.js -> HERO.cordillera.frames
"""
import os, sys, subprocess, glob, shutil, tempfile
from PIL import Image

DEST = r"E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO\assets\hero\cordillera"
args = sys.argv[1:]
if not args:
    print(__doc__); sys.exit(1)
src = args[0]
ancho = int(args[args.index("--ancho") + 1]) if "--ancho" in args else 1920
nfr = int(args[args.index("--frames") + 1]) if "--frames" in args else None
q = int(args[args.index("--calidad") + 1]) if "--calidad" in args else 82

tmp = tempfile.mkdtemp(prefix="cord_")
if os.path.isdir(src):
    # carpeta de PNG (salida de encolar_wan.py)
    pngs = sorted(glob.glob(os.path.join(src, "*.png")))
else:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, os.path.join(tmp, "f_%04d.png")], check=True)
    pngs = sorted(glob.glob(os.path.join(tmp, "f_*.png")))
print(f"{len(pngs)} frames en el clip")
if nfr and nfr < len(pngs):
    idx = [round(i * (len(pngs) - 1) / (nfr - 1)) for i in range(nfr)]
    pngs = [pngs[i] for i in idx]
if os.path.isdir(DEST):
    shutil.rmtree(DEST)
os.makedirs(DEST, exist_ok=True)
total = 0
for i, p in enumerate(pngs):
    im = Image.open(p).convert("RGB")
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    out = os.path.join(DEST, f"cord_{i:03d}.webp")
    im.save(out, "WEBP", quality=q, method=5)
    total += os.path.getsize(out)
shutil.rmtree(tmp, ignore_errors=True)
print(f"{len(pngs)} frames de {im.width}x{im.height} -> {DEST}  ({total/1e6:.1f} MB)")
print(f"Ahora en 02 SITIO NUEVO\\js\\hero.js poné:  cordillera: {{ frames: {len(pngs)}, ... }}")
