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
# Clara: la forma de la etiqueta (borde superior ondulado, círculo que sobresale) viene del canal alpha del
# recorte: la etiqueta es opaca y la botella semitransparente. Eco: banda recta detectada por el brillo del
# papel en el borde de la silueta. Las dos se ubican en metros desde la base (escala por el radio real) y se
# pintan sobre un mismo anillo (rango unión), rellenando con transparente lo que no es etiqueta.
PAPEL = np.array([245, 246, 244], np.float32)

def banda_rows(name, a):
    alpha = a[..., 3]; top, bot = bbox_rows(alpha); H = bot - top
    ys = np.arange(int(top + 0.18 * H), int(top + 0.56 * H))
    val = []
    for y in ys:
        c = np.where(alpha[y] > 20)[0]; w = c[-1] - c[0]
        if name == "agua":
            val.append(alpha[y, c[0] + w // 4:c[-1] - w // 4].mean() / 255)
        else:
            k = max(3, int(w * 0.03))
            val.append(np.concatenate([a[y, c[0]:c[0] + k, :3].mean(axis=1), a[y, c[-1] - k:c[-1], :3].mean(axis=1)]).mean())
    val = np.array(val)
    sel = ys[val > (0.45 if name == "agua" else 232)]
    y0, y1 = int(sel[0]), int(sel[-1])
    if name == "agua":
        y0 -= int(0.012 * H)                      # margen para el borde suave del círculo
    return y0, y1, top, bot, H

def medir(name):
    a = cargar(name); alpha = a[..., 3]
    y0, y1, top, bot, H = banda_rows(name, a)
    widths, cxs = [], []
    for y in range(int(top + 0.30 * H), int(top + 0.42 * H)):
        c = np.where(alpha[y] > 20)[0]
        widths.append((c[-1] - c[0]) / 2); cxs.append((c[-1] + c[0]) / 2)
    R = float(np.median(widths)); cx = float(np.median(cxs))
    px2m = r_lab / R                              # escala real: el radio en la etiqueta es el mismo en ambas
    z_top, z_bot = (bot - y0) * px2m, (bot - y1) * px2m
    return dict(a=a, y0=y0, y1=y1, R=R, cx=cx, z_top=z_top, z_bot=z_bot, H=H, top=top)

med = {n: medir(n) for n in ("agua", "eco")}
Z_MIN = min(m["z_bot"] for m in med.values()); Z_MAX = max(m["z_top"] for m in med.values())

def desenrollar(name, W=4096, Hh=1024):
    m = med[name]; a = m["a"]; R, cx = m["R"], m["cx"]
    r0 = int(round((Z_MAX - m["z_top"]) / (Z_MAX - Z_MIN) * Hh))
    r1 = int(round((Z_MAX - m["z_bot"]) / (Z_MAX - Z_MIN) * Hh))
    band = np.array(Image.fromarray(a[m["y0"]:m["y1"]]).resize((a.shape[1], max(2, r1 - r0)), Image.LANCZOS)).astype(np.float32)
    us = np.arange(W) / W
    thetas = (us - 0.5) * 360.0
    front = np.abs(thetas) <= ANG_MAX
    xs = cx + R * np.sin(np.radians(np.clip(thetas, -ANG_MAX, ANG_MAX)))
    xi = np.clip(np.round(xs).astype(int), 0, band.shape[1] - 1)
    samp = band[:, xi]                            # (h, W, 4): frente real; fuera del frente repite la columna límite
    tex = np.zeros((Hh, W, 4), np.float32)
    rgb = samp[..., :3].copy()
    if name == "agua":
        alpha = np.clip((samp[..., 3] / 255.0 - 0.2) / 0.6, 0, 1)   # etiqueta opaca -> 1, botella -> 0
    else:
        alpha = np.ones(samp.shape[:2], np.float32)
    # dorso: papel blanco con la forma del borde (alpha de la columna límite), fundido de 4°
    fade = 4.0
    w_front = np.clip((ANG_MAX + fade - np.abs(thetas)) / fade, 0, 1)[None, :, None]
    rgb = rgb * w_front + PAPEL[None, None, :] * (1 - w_front)
    tex[r0:r1, :, :3] = rgb
    tex[r0:r1, :, 3] = alpha * 255
    out = OUT + f"/etiqueta_{name}.png"
    Image.fromarray(tex.astype(np.uint8), "RGBA").save(out)
    return out, R, (m["y1"] - m["y0"])

info = {
    "alto_m": ALTO_M,
    "tapa_desde_z": round(tapa_z0, 5),
    "etiqueta_z": [round(float(Z_MIN), 5), round(float(Z_MAX), 5)],
    "etiqueta_z_agua": [round(float(med["agua"]["z_bot"]), 5), round(float(med["agua"]["z_top"]), 5)],
    "etiqueta_z_eco": [round(float(med["eco"]["z_bot"]), 5), round(float(med["eco"]["z_top"]), 5)],
    "r_etiqueta_m": round(r_lab, 5),
    "color_tapa_agua": color_tapa("agua"),
    "color_tapa_eco": color_tapa("eco"),
    "perfil": perfil,
}
for n in ("eco", "agua"):
    p, R, hpx = desenrollar(n)
    mm = med[n]
    print(f"etiqueta {n}: {p}  (R={R:.0f}px, filas {mm['y0']}-{mm['y1']} = {(mm['y0']-mm['top'])/mm['H']:.3f}-{(mm['y1']-mm['top'])/mm['H']:.3f} del alto, z={mm['z_bot']*1000:.1f}-{mm['z_top']*1000:.1f} mm)")
print(f"anillo etiqueta (unión): z={Z_MIN*1000:.1f}-{Z_MAX*1000:.1f} mm")
json.dump(info, open(OUT + "/perfil_botella.json", "w"), indent=1)
print(f"perfil: {len(perfil)} puntos, r_max={max(r for z, r in perfil):.4f} m, r_etiqueta={r_lab:.4f} m, tapa desde z={tapa_z0:.4f} m")
print("tapa agua:", info["color_tapa_agua"], " tapa eco:", info["color_tapa_eco"])
print("insumos en:", OUT)
