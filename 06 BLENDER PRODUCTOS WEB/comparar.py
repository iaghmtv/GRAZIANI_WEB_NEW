# -*- coding: utf-8 -*-
r"""comparar.py <salida.png> <alto> <productos,...> <carpeta1> [<carpeta2> ...] — filas = carpetas (la actual de la web
primero), columnas = productos, todo sobre el celeste de la web #f1f9fd, recortado al alpha y a la misma altura."""
import sys, os
from PIL import Image, ImageDraw
out, H, prods, carpetas = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(","), sys.argv[4:]
ETIQ = [e for e in os.environ.get("ETIQUETAS", "").split(";") if e]   # nombres de fila opcionales
WEB = "E:/GRACIANI/WEB GRAZIANI/02 SITIO NUEVO/assets/botellas"
def cargar(carpeta, n):
    exts = (".png", ".webp")
    if carpeta.endswith("|webp"):                 # carpeta|webp = preferir el .webp (la web nueva) al .png viejo
        carpeta, exts = carpeta[:-5], (".webp", ".png")
    for e in exts:
        p = f"{carpeta}/{n}{e}"
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
            im = im.crop(bb) if bb else im
            return im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)
    return None
filas = [[cargar(c, n) for n in prods] for c in carpetas]
anchos = [max((f[i].width if f[i] else 0) for f in filas) for i in range(len(prods))]
W = sum(anchos) + 24 * (len(prods) + 1) + 150
hoja = Image.new("RGBA", (W, (H + 40) * len(carpetas) + 10), (241, 249, 253, 255))
d = ImageDraw.Draw(hoja)
for r, (c, fila) in enumerate(zip(carpetas, filas)):
    y = 10 + r * (H + 40)
    d.text((8, y + H // 2), (ETIQ[r] if r < len(ETIQ) else os.path.basename(c.split("|")[0].rstrip("/")))[:22], fill=(30, 30, 30))
    x = 150
    for i, im in enumerate(fila):
        if im:
            hoja.alpha_composite(im, (x + (anchos[i] - im.width) // 2, y + 20))
        if r == 0:
            d.text((x, y), prods[i], fill=(30, 30, 30))
        x += anchos[i] + 24
hoja.convert("RGB").save(out)
print(out, hoja.size)
