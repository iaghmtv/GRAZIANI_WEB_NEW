# -*- coding: utf-8 -*-
r"""
03_exportar_frames_web.py — Pasa los PNG renderizados (render/giro_####.png) a la secuencia que scrubea el hero web.

  python 03_exportar_frames_web.py [--alto 1000] [--calidad 82]

Recorta al contenido con alpha (mismo encuadre para todos los frames), escala y guarda:
  E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO\assets\hero\giro\giro_000.webp ... giro_NNN.webp
Después poner la cantidad en js/hero.js -> HERO.giro.frames
"""
import os, sys, glob, shutil
from PIL import Image

SRC = r"E:\GRACIANI\WEB GRAZIANI\03 BLENDER GIRO BOTELLA\render"
DEST = r"E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO\assets\hero\giro"
args = sys.argv[1:]
alto = int(args[args.index("--alto") + 1]) if "--alto" in args else 1000
q = int(args[args.index("--calidad") + 1]) if "--calidad" in args else 82

pngs = sorted(glob.glob(os.path.join(SRC, "giro_*.png")))
if not pngs:
    print("No hay frames en", SRC); sys.exit(1)
# encuadre común: unión de las cajas con alpha de todos los frames (la silueta casi no cambia al girar)
L = T = 10**9; R = B = -1
for p in pngs:
    bb = Image.open(p).convert("RGBA").getbbox()
    if bb:
        L, T, R, B = min(L, bb[0]), min(T, bb[1]), max(R, bb[2]), max(B, bb[3])
pad = int((B - T) * 0.02)
box = (max(0, L - pad), max(0, T - pad), R + pad, B + pad)
if os.path.isdir(DEST):
    shutil.rmtree(DEST)
os.makedirs(DEST, exist_ok=True)
total = 0
for i, p in enumerate(pngs):
    im = Image.open(p).convert("RGBA").crop(box)
    im = im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)
    out = os.path.join(DEST, f"giro_{i:03d}.webp")
    im.save(out, "WEBP", quality=q, method=5)
    total += os.path.getsize(out)
print(f"{len(pngs)} frames de {im.width}x{im.height} -> {DEST}  ({total/1e6:.1f} MB, {total/len(pngs)/1e3:.0f} KB c/u)")
print(f"Ahora en 02 SITIO NUEVO\\js\\hero.js poné:  giro: {{ frames: {len(pngs)}, ... }}")
