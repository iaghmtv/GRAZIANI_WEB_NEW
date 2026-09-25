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
    if name == "eco":
        # el render de referencia viene lavado: más contraste (negro del círculo) y saturación (verdes)
        from PIL import ImageEnhance
        im8 = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
        im8 = ImageEnhance.Contrast(im8).enhance(1.45)
        im8 = ImageEnhance.Color(im8).enhance(1.8)
        rgb = np.array(im8).astype(np.float32)
    tex[r0:r1, :, :3] = rgb
    tex[r0:r1, :, 3] = alpha * 255
    out = OUT + f"/etiqueta_{name}.png"
    Image.fromarray(tex.astype(np.uint8), "RGBA").save(out)
    return out, R, (m["y1"] - m["y0"])


# ---------------- Etiqueta DOBLE: Clara al frente (u 0.25-0.75), Eco en el dorso (u 0.75-1 y 0-0.25) ----------------
# Al girar entra la otra etiqueta; no hay relleno de dorso ni fundido. El anillo usa el rango z de la Clara y la Eco
# se apoya en la misma base (su banda es 1,7 mm más baja). Cada etiqueta llena ±90° comprimiendo los ±ANG_MAX útiles de la foto.
def doble(W=4096, Hh=1024):
    from PIL import ImageEnhance
    zt, zb = med["agua"]["z_top"], med["agua"]["z_bot"]
    tex = np.zeros((Hh, W, 4), np.float32)
    us = np.arange(W) / W
    theta = (us - 0.5) * 360.0
    for name, centro in (("agua", 0.0), ("eco", 180.0)):
        m = med[name]; a = m["a"]; R, cx = m["R"], m["cx"]
        rel = ((theta - centro + 180.0) % 360.0) - 180.0
        sel = np.abs(rel) <= 90.0
        th_photo = rel[sel] * (ANG_MAX / 90.0)
        xs = cx + R * np.sin(np.radians(th_photo))
        xi = np.clip(np.round(xs).astype(int), 0, a.shape[1] - 1)
        alto_rel = (m["z_top"] - m["z_bot"]) / (zt - zb)          # la Eco es apenas más baja: se apoya en la base
        h = max(2, int(round(Hh * min(alto_rel, 1.0))))
        band = np.array(Image.fromarray(a[m["y0"]:m["y1"]]).resize((a.shape[1], h), Image.LANCZOS)).astype(np.float32)
        samp = band[:, xi]
        rgb = samp[..., :3]
        if name == "agua":
            alpha = np.clip((samp[..., 3] / 255.0 - 0.2) / 0.6, 0, 1)
        else:
            im8 = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
            im8 = ImageEnhance.Color(ImageEnhance.Contrast(im8).enhance(1.45)).enhance(1.8)
            rgb = np.array(im8).astype(np.float32)
            alpha = np.ones(samp.shape[:2], np.float32)
        r0 = Hh - h
        cols = np.where(sel)[0]
        tex[r0:Hh, cols, :3] = rgb
        tex[r0:Hh, cols, 3] = alpha * 255
    out = OUT + "/etiqueta_doble.png"
    Image.fromarray(tex.astype(np.uint8), "RGBA").save(out)
    return out, zb, zt

DOBLE_PATH, Z_DOBLE_MIN, Z_DOBLE_MAX = doble()
print(f"etiqueta doble: {DOBLE_PATH}  anillo z={Z_DOBLE_MIN*1000:.1f}-{Z_DOBLE_MAX*1000:.1f} mm")


# ---------------- Etiquetas ORIGINALES planas (proyecto E:/GRACIANI/Botellas Finales/textures) ----------------
# Clara: agua-sin-gas-500-topaz (RGBA con el recorte real de la ola, la "calada"). Eco: arte a 2 tintas + su máscara
# de roughness (blanco = papel, negro = tintas). Se recorta la marca de registro oscura del borde derecho, se rota cada
# una para que quede de frente (u = 0.5) el mismo logo que muestran las fotos de producto, y se reducen a 4096 px.
TEX_ORIG = "E:/GRACIANI/Botellas Finales/textures"
ORIG = {
    #        color                                                         máscara roughness                                                     logo de frente  umbral oscuro
    "clara": (TEX_ORIG + "/agua-sin-gas-500-topaz-high fidelity-4x.png", None,                                                                1,              110),
    "eco":   (TEX_ORIG + "/eco agua graziani SIN TRAMA x 500cc orig 2 tintas rgb.png",
              TEX_ORIG + "/eco agua graziani SIN TRAMA x 500cc orig 2 tintas rgb rougnes.png",                                               0,              60),
}
W_OUT = 4096

def fin_util(a):
    """Primera columna de la marca de registro oscura del borde derecho (o el ancho si no hay)."""
    h, w = a.shape[:2]
    lum = a[..., :3].mean(axis=2)
    alpha = a[..., 3]
    zona = slice(int(h * 0.72), int(h * 0.97))
    oscuro = ((lum[zona] < 70) & (alpha[zona] > 200)).mean(axis=0)
    cols = np.where(oscuro[int(w * 0.95):] > 0.8)[0]
    return w if len(cols) == 0 else int(w * 0.95) + int(cols[0]) - 12

def centros_logo(a, x_fin, umbral):
    """x de los dos círculos oscuros del logo: perfil de columnas oscuras en la franja media, suavizado."""
    h = a.shape[0]
    lum = a[:, :x_fin, :3].mean(axis=2)
    perfil = ((lum[int(h * 0.25):int(h * 0.75)] < umbral) & (a[int(h * 0.25):int(h * 0.75), :x_fin, 3] > 200)).mean(axis=0)
    k = max(3, x_fin // 20)
    perfil = np.convolve(perfil, np.ones(k) / k, mode="same")
    picos, q = [], perfil.copy()
    for _ in range(2):
        i = int(np.argmax(q)); picos.append(i)
        q[max(0, i - x_fin // 8):i + x_fin // 8] = 0
    return sorted(picos)

def centro_disco(a, cx0, nombre, banda=(0.28, 0.52), umbral=0.12):
    """x del centro del DISCO del logo (azul oscuro en la Clara, negro en la Eco): punto medio de su extensión
    horizontal en una franja. Un círculo es simétrico respecto de su eje vertical en cualquier franja, así que
    el texto oscuro vecino ("Cont. Neto 500cc") ya no corre el centro como en el pico de centros_logo()."""
    h, w = a.shape[:2]
    f = a[int(h * banda[0]):int(h * banda[1])].astype(np.int16)
    r, g, b, al = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    if nombre == "clara":
        m = ((r + g + b) / 3 < 150) & (b > r + 25) & (al > 200)
    else:
        m = (np.maximum(np.maximum(r, g), b) < 90) & (al > 200)
    k = max(9, w // 450)
    p = np.convolve(m.mean(axis=0), np.ones(k) / k, mode="same")
    ventana = slice(max(0, cx0 - w // 10), min(w, cx0 + w // 10))
    pico = ventana.start + int(np.argmax(p[ventana]))
    hueco = max(4, w // 250)          # tolera las letras blancas dentro del disco, no el blanco que lo rodea
    def extremo(paso):
        x, ult = pico, pico
        while 0 <= x < w and abs(x - ult) <= hueco:
            if p[x] > umbral:
                ult = x
            x += paso
        return ult
    return (extremo(-1) + extremo(+1)) / 2

def preparar(nombre):
    f_color, f_mask, frente, umbral = ORIG[nombre]
    a = np.array(Image.open(f_color).convert("RGBA"))
    x_fin = fin_util(a.astype(np.float32))
    logos = centros_logo(a.astype(np.float32), x_fin, umbral)
    cx = logos[frente]
    # v009: el primer frame debe mostrar el logo de frente -> se afina con el borde del disco (en la Clara el pico
    # caía 15,6° corrido hacia "Cont. Neto 500cc"; en la Eco 1,5°)
    prov = np.roll(a[:, :x_fin], x_fin // 2 - cx, axis=1)
    ajuste = round(centro_disco(prov, x_fin // 2, nombre) - x_fin // 2)
    del prov
    cx += ajuste
    shift = x_fin // 2 - cx
    def rodar(arr):
        return np.roll(arr[:, :x_fin], shift, axis=1)
    col = rodar(a)
    h_out = round(col.shape[0] * W_OUT / col.shape[1])
    im = Image.fromarray(col, "RGBA").convert("RGBa").resize((W_OUT, h_out), Image.LANCZOS).convert("RGBA")
    im.save(OUT + f"/etiqueta_{nombre}_orig.png")
    if f_mask:
        m = np.array(Image.open(f_mask).convert("L"))
        mk = Image.fromarray(rodar(m[:, :, None])[:, :, 0], "L").resize((W_OUT, h_out), Image.LANCZOS)
    else:
        rgb = np.array(im).astype(np.float32)
        lum = rgb[..., :3].mean(axis=2)
        mk = Image.fromarray((np.clip((lum - 110.0) / 125.0, 0, 1) * 255).astype(np.uint8), "L")
    mk.save(OUT + f"/etiqueta_{nombre}_mask.png")
    print(f"etiqueta {nombre}: original {a.shape[1]}x{a.shape[0]}, util hasta x={x_fin} ({x_fin/a.shape[1]*100:.1f} %), "
          f"logos en x={logos} ({[round(l/x_fin, 3) for l in logos]}), de frente el {frente+1}º -> {W_OUT}x{h_out}; "
          f"ajuste por disco {ajuste:+d} px = {ajuste/x_fin*360:+.2f}°, costura a {((shift % x_fin)/x_fin - 0.5)*360:+.1f}° del frente")
    return x_fin / a.shape[0]            # aspecto útil ancho/alto

asp_cl = preparar("clara")
asp_ec = preparar("eco")
CIRC = 2 * math.pi * (r_lab + 0.0007)    # mismo radio que el cilindro de etiqueta de la escena
H_ET = CIRC / asp_ec
ZC_ET = (med["eco"]["z_bot"] + med["eco"]["z_top"]) / 2     # centro de la etiqueta en la foto de la Eco (misma botella)
Z_ET0, Z_ET1 = ZC_ET - H_ET / 2, ZC_ET + H_ET / 2
print(f"anillo etiquetas originales: alto {H_ET*1000:.1f} mm (circunferencia {CIRC*1000:.1f} mm / aspecto {asp_ec:.3f}), "
      f"z={Z_ET0*1000:.1f}-{Z_ET1*1000:.1f} mm (aspecto Clara {asp_cl:.3f})")

info = {
    "alto_m": ALTO_M,
    "tapa_desde_z": round(tapa_z0, 5),
    "etiqueta_z": [round(float(Z_ET0), 5), round(float(Z_ET1), 5)],
    "etiqueta_doble": "etiqueta_doble.png",
    "etiqueta_clara": "etiqueta_clara_orig.png",
    "etiqueta_clara_mask": "etiqueta_clara_mask.png",
    "etiqueta_eco": "etiqueta_eco_orig.png",
    "etiqueta_eco_mask": "etiqueta_eco_mask.png",
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
