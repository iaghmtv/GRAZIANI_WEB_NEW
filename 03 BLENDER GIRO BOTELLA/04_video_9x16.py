# -*- coding: utf-8 -*-
r"""
04_video_9x16.py — La animación de la botella sola, vertical 9:16 (1080x1920) con la cordillera fija de fondo, sin texto.

  python 04_video_9x16.py --prueba            3 encuadres del fondo (cuadro 1 y 120) en una hoja, para elegir
  python 04_video_9x16.py [--x 1411]          compone los cuadros y arma el MP4

Toma los PNG del render de Blender (render\giro_0001..0120.png, 800x2000 con alfa, v009) y los compone sobre
02 SITIO NUEVO\assets\hero\cordillera.jpg recortada a 9:16 (la foto es 16:9 de 1917x1079: la franja vertical se
amplía con Lanczos y se suaviza apenas, como un fondo fuera de foco). Mismo tratamiento que el hero de la web:
velo azul marino arriba (rgba 8,24,44) y el halo oscuro detrás de la botella.

Tiempos (30 fps): entrada con un pequeño giro (cuadros 24 -> 1, ease-out, como al cargar la web) 0,8 s,
Clara de frente 1 s, giro de 3 vueltas con cambio a Eco (1 -> 120) 4 s, Eco de frente 2 s  = 7,8 s.
Salida: cuadros compuestos en video_9x16\giro9x16_####.png y el MP4 en 05 PREVIEWS.
"""
import os, sys, glob, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA"
RENDER = BASE + "/render"
FONDO = "E:/GRACIANI/WEB GRAZIANI/02 SITIO NUEVO/assets/hero/cordillera.jpg"
SALIDA = BASE + "/video_9x16"
PREVIEWS = "E:/GRACIANI/WEB GRAZIANI/05 PREVIEWS"
W, H, FPS = 1080, 1920, 30
ALTO_BOTELLA = 0.80          # la botella ocupa el 80 % del alto del cuadro
CENTRO_Y = 0.53              # centro vertical de la botella (un poco abajo del medio)
SUAVIZADO = 1.3              # desenfoque del fondo (px a 1080 de ancho): la ampliación no se ve "crocante"

args = sys.argv[1:]
def arg(n, d):
    return type(d)(args[args.index(n) + 1]) if n in args else d

def fondo_9x16(cx):
    """Franja vertical 9:16 de la foto centrada en cx (px de la foto original), ampliada a 1080x1920 y tratada."""
    foto = Image.open(FONDO).convert("RGB")
    fw, fh = foto.size
    cw = round(fh * W / H)
    x0 = int(min(max(cx - cw / 2, 0), fw - cw))
    im = foto.crop((x0, 0, x0 + cw, fh)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(SUAVIZADO))
    a = np.asarray(im, np.float32) / 255.0
    y = np.linspace(0, 1, H)[:, None, None]
    marino = np.array([8, 24, 44], np.float32) / 255.0
    velo = np.clip(0.42 * (1 - y / 0.38), 0, None)            # arriba: como el degradé del hero (0,35 -> 0)
    velo = velo + np.clip(0.30 * (y - 0.70) / 0.30, 0, None)   # abajo: asienta la base de la botella
    velo = velo + 0.10                                          # tono general del hero (la foto cruda es más blanca)
    a = a * (1 - velo) + marino * velo
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

def halo(bw, bh, cx, cy):
    """Halo oscuro detrás de la botella (radial-gradient rgba(0,0,0,.38) -> 0 al 68 %, blur 6px en la web)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ex, ey = bw * 1.25, bh * 0.62
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - cx) / ex) ** 2 + ((yy - cy) / ey) ** 2)
    alfa = np.clip(0.38 * (1 - r / 0.68), 0, 0.38)
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.fromarray(arr).filter(ImageFilter.GaussianBlur(9))

# geometría de la botella: caja con alfa del render (igual en todos los cuadros; se toma la unión)
pngs = sorted(glob.glob(RENDER + "/giro_*.png"))
assert len(pngs) == 120, f"faltan cuadros del render: {len(pngs)}"
L = T = 10 ** 9; R = B = -1
for p in (pngs[0], pngs[59], pngs[-1]):
    bb = Image.open(p).getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    L, T, R, B = min(L, bb[0]), min(T, bb[1]), max(R, bb[2]), max(B, bb[3])
escala = ALTO_BOTELLA * H / (B - T)
eje_render = 399.5                                   # eje de la botella en el render (medido en v009)
tam = (round(800 * escala), round(2000 * escala))
ox = round(W / 2 - eje_render * escala)
oy = round(CENTRO_Y * H - (T + B) / 2 * escala)
bw, bh = (R - L) * escala, (B - T) * escala

def cuadro(fondo_rgba, halo_rgba, i):
    bot = Image.open(pngs[i]).convert("RGBA").resize(tam, Image.LANCZOS)
    out = fondo_rgba.copy()
    out.alpha_composite(halo_rgba)
    out.alpha_composite(bot, (ox, oy))
    return out.convert("RGB")

if "--prueba" in args:
    hl = halo(bw, bh, W / 2, CENTRO_Y * H)
    fotos = []
    for cx in (960, 1200, 1411):
        fnd = fondo_9x16(cx)
        for i in (0, 119):
            fotos.append((cx, i, cuadro(fnd, hl, i).resize((W // 3, H // 3), Image.LANCZOS)))
    hoja = Image.new("RGB", (6 * (W // 3) + 70, H // 3 + 40), (30, 30, 30))
    d = ImageDraw.Draw(hoja)
    for k, (cx, i, im) in enumerate(fotos):
        x = 10 + k * (W // 3 + 10)
        hoja.paste(im, (x, 30)); d.text((x, 8), f"x={cx}  cuadro {i + 1}", fill=(230, 230, 230))
    out = "C:/Users/Urano/AppData/Local/Temp/claude/E--GRACIANI-WEB-GRAZIANI/eed07efa-d6f6-48b9-a5ac-6238911fd8a3/scratchpad/prueba_9x16.png"
    hoja.save(out); print(out, hoja.size, "escala botella", round(escala, 3))
    sys.exit(0)

cx = arg("--x", 1411)
fnd = fondo_9x16(cx)
hl = halo(bw, bh, W / 2, CENTRO_Y * H)
# línea de tiempo: índices de cuadro del render (0-based) por cada cuadro de video
entrada = [23 - round(23 * (1 - (1 - k / 23) ** 2)) for k in range(24)]   # 23 -> 0 con ease-out (power2.out)
seq = entrada + [0] * 30 + list(range(120)) + [119] * 60
os.makedirs(SALIDA, exist_ok=True)
for f in glob.glob(SALIDA + "/giro9x16_*.png"):
    os.remove(f)
cache = {}
for n, i in enumerate(seq):
    if i not in cache:
        cache = {i: cuadro(fnd, hl, i)}
    cache[i].save(f"{SALIDA}/giro9x16_{n:04d}.png", compress_level=1)
print(f"{len(seq)} cuadros ({len(seq) / FPS:.1f} s) en {SALIDA}  (fondo x={cx}, botella {bw:.0f}x{bh:.0f} px)")
mp4 = f"{PREVIEWS}/giro_botella_9x16_2026-09-28.mp4"
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{SALIDA}/giro9x16_%04d.png",
       "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4]
subprocess.run(cmd, check=True)
print("MP4:", mp4, f"{os.path.getsize(mp4) / 1e6:.1f} MB")
