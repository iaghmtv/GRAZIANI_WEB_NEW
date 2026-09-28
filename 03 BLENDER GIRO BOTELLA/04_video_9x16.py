# -*- coding: utf-8 -*-
r"""
04_video_9x16.py — La animación de la botella sola, vertical 9:16 (1080x1920, 30 fps) con la cordillera fija de fondo,
sin texto.

  python 04_video_9x16.py --prueba          3 encuadres del fondo (Clara y Eco) en una hoja, para elegir
  python 04_video_9x16.py entrada [--x N]   versión con entrada: la botella aparece (fundido + sube, como en la web)
                                            girando HACIA ADELANTE (render_entrada, -180° -> 0°) 1,5 s, Clara 1 s,
                                            giro de 3 vueltas a Eco 4 s, Eco 2 s  = 8,5 s
  python 04_video_9x16.py loop [--x N]      versión en loop: Clara 0,75 s, giro a Eco 4 s, Eco 1,5 s, sigue girando
                                            para el mismo lado y vuelve a Clara (render_vuelta) 4 s, Clara 0,75 s
                                            = 11 s; el último cuadro es el primero: empalma sin salto

Cuadros de la botella (PNG con alfa, 800x2000, escena giro_botella_v009):
  render\giro_####.png (ida Clara -> Eco), render_entrada\entrada_####.png, render_vuelta\vuelta_####.png (05_render_extra.py)
Fondo: 02 SITIO NUEVO\assets\hero\cordillera.jpg, franja 9:16 centrada en x=1411 (el fondo de la botella en el hero),
ampliada con Lanczos y apenas desenfocada; velo azul marino (rgba 8,24,44) y halo oscuro detrás de la botella como en la web.
Salida: video_9x16_<versión>\giro9x16_####.png y el MP4 en 05 PREVIEWS.
"""
import os, sys, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA"
FUENTES = {"giro": BASE + "/render/giro_{:04d}.png", "entrada": BASE + "/render_entrada/entrada_{:04d}.png",
           "vuelta": BASE + "/render_vuelta/vuelta_{:04d}.png"}
FONDO = "E:/GRACIANI/WEB GRAZIANI/02 SITIO NUEVO/assets/hero/cordillera.jpg"
PREVIEWS = "E:/GRACIANI/WEB GRAZIANI/05 PREVIEWS"
FECHA = "2026-09-28"
W, H, FPS = 1080, 1920, 30
ALTO_BOTELLA = 0.80          # la botella ocupa el 80 % del alto del cuadro
CENTRO_Y = 0.53              # centro vertical de la botella (un poco abajo del medio)
SUAVIZADO = 1.3              # desenfoque del fondo (px a 1080 de ancho): la ampliación no se ve "crocante"
SUBIDA = 100                 # px que sube la botella al aparecer (los 48 px de la web a 1920 de alto)

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
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - cx) / (bw * 1.25)) ** 2 + ((yy - cy) / (bh * 0.62)) ** 2)
    alfa = np.clip(0.38 * (1 - r / 0.68), 0, 0.38)
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.fromarray(arr).filter(ImageFilter.GaussianBlur(9))

# geometría de la botella: unión de las cajas con alfa (la cámara es la misma en los tres tramos)
L = T = 10 ** 9; R = B = -1
for p in (FUENTES["giro"].format(1), FUENTES["giro"].format(60), FUENTES["giro"].format(120)):
    bb = Image.open(p).getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    L, T, R, B = min(L, bb[0]), min(T, bb[1]), max(R, bb[2]), max(B, bb[3])
escala = ALTO_BOTELLA * H / (B - T)
EJE_RENDER = 399.5                                   # eje de la botella en el render (medido en v009)
TAM = (round(800 * escala), round(2000 * escala))
OX = round(W / 2 - EJE_RENDER * escala)
OY = round(CENTRO_Y * H - (T + B) / 2 * escala)
BW, BH = (R - L) * escala, (B - T) * escala

def con_opacidad(im, op):
    if op >= 1:
        return im
    a = im.getchannel("A").point(lambda v: round(v * op))
    im = im.copy(); im.putalpha(a)
    return im

def cuadro(fondo, hl, fuente, i, op=1.0, dy=0):
    bot = Image.open(FUENTES[fuente].format(i + 1)).convert("RGBA").resize(TAM, Image.LANCZOS)
    out = fondo.copy()
    out.alpha_composite(con_opacidad(hl, op), (0, round(dy)))
    out.alpha_composite(con_opacidad(bot, op), (OX, OY + round(dy)))
    return out.convert("RGB")

def ease_out3(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3

def secuencia(version):
    """Lista de (tramo, índice 0-based, opacidad, desplazamiento y) por cada cuadro del video."""
    ida = [("giro", i, 1, 0) for i in range(120)]
    if version == "entrada":
        aparece = []
        for k in range(45):                              # 1,5 s de giro hacia adelante hasta quedar de frente
            e = ease_out3(k / 33)                        # fundido + subida en 1,1 s (power3.out, como la web)
            aparece.append(("entrada", k, e, SUBIDA * (1 - e)))
        return aparece + [("giro", 0, 1, 0)] * 30 + ida + [("giro", 119, 1, 0)] * 60
    if version == "loop":
        vuelta = [("vuelta", i, 1, 0) for i in range(120)]
        return [("giro", 0, 1, 0)] * 22 + ida + [("giro", 119, 1, 0)] * 45 + vuelta + [("giro", 0, 1, 0)] * 23
    raise SystemExit("versión: entrada | loop")

if "--prueba" in args:
    hl = halo(BW, BH, W / 2, CENTRO_Y * H)
    fotos = []
    for cx in (960, 1200, 1411):
        fnd = fondo_9x16(cx)
        for i in (0, 119):
            fotos.append((cx, i, cuadro(fnd, hl, "giro", i).resize((W // 3, H // 3), Image.LANCZOS)))
    hoja = Image.new("RGB", (6 * (W // 3) + 70, H // 3 + 40), (30, 30, 30))
    d = ImageDraw.Draw(hoja)
    for k, (cx, i, im) in enumerate(fotos):
        x = 10 + k * (W // 3 + 10)
        hoja.paste(im, (x, 30)); d.text((x, 8), f"x={cx}  cuadro {i + 1}", fill=(230, 230, 230))
    out = "C:/Users/Urano/AppData/Local/Temp/claude/E--GRACIANI-WEB-GRAZIANI/eed07efa-d6f6-48b9-a5ac-6238911fd8a3/scratchpad/prueba_9x16.png"
    hoja.save(out); print(out, hoja.size, "escala botella", round(escala, 3))
    sys.exit(0)

version = next((a for a in args if a in ("entrada", "loop")), None) or sys.exit("indicar versión: entrada | loop")
cx = arg("--x", 1411)
seq = secuencia(version)
for tramo in {s[0] for s in seq}:
    n = 45 if tramo == "entrada" else 120
    faltan = [i for i in range(n) if not os.path.exists(FUENTES[tramo].format(i + 1))]
    assert not faltan, f"faltan cuadros de {tramo}: {faltan[:5]}..."
fnd = fondo_9x16(cx)
hl = halo(BW, BH, W / 2, CENTRO_Y * H)
salida = f"{BASE}/video_9x16_{version}"
os.makedirs(salida, exist_ok=True)
for f in glob.glob(salida + "/giro9x16_*.png"):
    os.remove(f)
previo, img = None, None
for n, s in enumerate(seq):
    if s != previo:
        img = cuadro(fnd, hl, *s)
        previo = s
    img.save(f"{salida}/giro9x16_{n:04d}.png", compress_level=1)
print(f"{version}: {len(seq)} cuadros ({len(seq) / FPS:.2f} s) en {salida}  (fondo x={cx}, botella {BW:.0f}x{BH:.0f} px)")
mp4 = f"{PREVIEWS}/giro_botella_9x16_{'v2' if version == 'entrada' else 'loop'}_{FECHA}.mp4"
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{salida}/giro9x16_%04d.png",
       "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4]
subprocess.run(cmd, check=True)
print("MP4:", mp4, f"{os.path.getsize(mp4) / 1e6:.1f} MB")
