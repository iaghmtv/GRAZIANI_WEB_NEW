# -*- coding: utf-8 -*-
"""
01_preparar_insumos.py  —  Insumos para el giro de la botella en Blender
  - perfil_botella.json : perfil de revolución (z, r) en metros, sacado de la silueta de la botella Eco
  - etiqueta_eco.png / etiqueta_agua.png : etiquetas desenrolladas 360° (u=0.5 es el frente) desde las fotos
  - colores de tapa (azul agua / gris eco)
Correr con el Python del sistema (usa Pillow + numpy):  python 01_preparar_insumos.py
"""
import os, json, math
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

BASE = "E:/GRACIANI/WEB GRAZIANI"
S3 = BASE + "/11 AJUSTE PRODUCTOS WEB"
OUT = BASE + "/03 BLENDER GIRO BOTELLA/insumos"
os.makedirs(OUT, exist_ok=True)
SRC = {
    "agua": S3 + "/Agua 500cc/Agua_500Cc_FondoTransparente_sinGotas.png",
    "eco":  S3 + "/Eco Agua/Botella_Clara_Graziani_500_ESTUDIO_REF_ALPHA_6000x6000.png",
}
ALTO_M = 0.21            # alto real de la botella con tapa (m)
TAPA_FRAC = 0.115        # la tapa ocupa este tramo desde arriba (fracción del alto)
LABEL_FRAC = (0.265, 0.455)   # banda de etiqueta, fracción del alto desde arriba
ANG_MAX = 78             # grados de frente utilizables de la foto (más allá está muy comprimido)

def cargar(name):
    im = Image.open(SRC[name]).convert("RGBA")
    return np.array(im)

def bbox_rows(alpha):
    rows = np.where(alpha.max(axis=1) > 20)[0]
    return int(rows[0]), int(rows[-1])

# ---------------- Perfil de revolución (silueta de la Eco: recorte opaco) ----------------
a = cargar("eco"); alpha = a[..., 3]
top, bot = bbox_rows(alpha); H = bot - top
px2m = ALTO_M / H
zs, rs = [], []
for y in range(top, bot + 1, 3):
    cols = np.where(alpha[y] > 20)[0]
    if len(cols) == 0:
        continue
    rs.append((cols[-1] - cols[0]) / 2 * px2m)
    zs.append((bot - y) * px2m)          # z = 0 en la base
zs = np.array(zs[::-1]); rs = np.array(rs[::-1])   # de abajo hacia arriba
k = 5
rs_s = np.convolve(np.pad(rs, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
rs_s[0] = min(rs_s[0], rs[0]); rs_s[-1] = min(rs_s[-1], rs[-1])
perfil = [[round(float(z), 5), round(float(r), 5)] for z, r in zip(zs, rs_s)]

lab_z1 = ALTO_M * (1 - LABEL_FRAC[0]); lab_z0 = ALTO_M * (1 - LABEL_FRAC[1])
r_lab = float(np.median([r for z, r in perfil if lab_z0 <= z <= lab_z1]))
tapa_z0 = ALTO_M * (1 - TAPA_FRAC)

# ---------------- Color de tapa (mediana de la zona de tapa) ----------------
def color_tapa(name):
    a = cargar(name); alpha = a[..., 3]; top, bot = bbox_rows(alpha); H = bot - top
    y0, y1 = int(top + 0.03 * H), int(top + 0.09 * H)
    zona = a[y0:y1]; m = zona[..., 3] > 200
    rgb = zona[..., :3][m]
    return [round(float(v) / 255, 4) for v in np.median(rgb, axis=0)]

# ---------------- Etiquetas desenrolladas ----------------
def desenrollar(name, W=4096, Hh=1024):
    a = cargar(name); alpha = a[..., 3]; top, bot = bbox_rows(alpha); H = bot - top
    y0, y1 = int(top + LABEL_FRAC[0] * H), int(top + LABEL_FRAC[1] * H)
    widths, cxs = [], []
    for y in range(y0, y1):
        c = np.where(alpha[y] > 20)[0]
        widths.append((c[-1] - c[0]) / 2); cxs.append((c[-1] + c[0]) / 2)
    R = float(np.median(widths)); cx = float(np.median(cxs))
    band = np.array(Image.fromarray(a[y0:y1]).resize((a.shape[1], Hh), Image.LANCZOS))
    us = np.arange(W) / W
    thetas = (us - 0.5) * 360.0
    front = np.abs(thetas) <= ANG_MAX
    xs = cx + R * np.sin(np.radians(thetas[front]))
    xi = np.clip(np.round(xs).astype(int), 0, band.shape[1] - 1)
    tex = np.zeros((Hh, W, 4), np.float32)
    tex[:, front] = band[:, xi].astype(np.float32)
    # dorso: relleno neutro (eco: blanco papel; agua: film claro translúcido)
    if name == "eco":
        fondo = np.array([244, 244, 241, 255], np.float32)
    else:
        med = np.median(band[:, xi][..., :3].reshape(-1, 3), axis=0)
        fondo = np.array([med[0], med[1], med[2], 255], np.float32)
    tex[:, ~front] = fondo
    # fundido de 4° a cada lado del límite del frente para no ver la costura
    fade = 4.0
    w_front = np.clip((ANG_MAX + fade - np.abs(thetas)) / fade, 0, 1)   # 1 dentro, 0 afuera
    # remuestrea los bordes del frente como referencia para fundir
    edge_cols = np.clip(np.round(cx + R * np.sin(np.radians(np.clip(thetas, -ANG_MAX, ANG_MAX)))).astype(int), 0, band.shape[1] - 1)
    ref = band[:, edge_cols].astype(np.float32)
    mezcla = ref * w_front[None, :, None] + fondo[None, None, :] * (1 - w_front[None, :, None])
    zona = (~front) & (w_front > 0)
    tex[:, zona] = mezcla[:, zona]
    tex[..., 3] = 255
    if name == "agua":
        # etiqueta film transparente: lo impreso (oscuro) opaco, lo claro deja ver el agua
        lum = tex[..., :3].mean(axis=2)
        tex[..., 3] = np.clip((240 - lum) / 110, 0.30, 1.0) * 255
    out = OUT + f"/etiqueta_{name}.png"
    Image.fromarray(tex.astype(np.uint8), "RGBA").save(out)
    return out, R, (y1 - y0)

info = {
    "alto_m": ALTO_M,
    "tapa_desde_z": round(tapa_z0, 5),
    "etiqueta_z": [round(lab_z0, 5), round(lab_z1, 5)],
    "r_etiqueta_m": round(r_lab, 5),
    "color_tapa_agua": color_tapa("agua"),
    "color_tapa_eco": color_tapa("eco"),
    "perfil": perfil,
}
for n in ("eco", "agua"):
    p, R, hpx = desenrollar(n)
    print(f"etiqueta {n}: {p}  (R={R:.0f}px, alto banda={hpx}px en la foto)")
json.dump(info, open(OUT + "/perfil_botella.json", "w"), indent=1)
print(f"perfil: {len(perfil)} puntos, r_max={max(r for z, r in perfil):.4f} m, r_etiqueta={r_lab:.4f} m, tapa desde z={tapa_z0:.4f} m")
print("tapa agua:", info["color_tapa_agua"], " tapa eco:", info["color_tapa_eco"])
print("insumos en:", OUT)
