# -*- coding: utf-8 -*-
r"""hoja.py <carpeta_render> <salida.png> [alto]  — hoja de contacto de los renders sobre el celeste de la web (#f1f9fd),
recortados a su alpha, en el orden del carrusel."""
import sys, os
from PIL import Image, ImageDraw
ORDEN = ["ecoagua500", "agua500", "agua1", "agua2", "agua6", "soda500", "soda1", "soda2", "soda225", "aguapremium",
         "sodapremium", "amargocitrus", "amargocordillerano", "amargolimon", "amargopomelo", "amargoserrano",
         "manzana", "naranja", "pomelo", "saborizada2l-naranja", "saborizada2l-manzana", "saborizada2l-pomelo"]
src, out = sys.argv[1], sys.argv[2]
H = int(sys.argv[3]) if len(sys.argv) > 3 else 360
ims = []
for n in ORDEN:
    p = next((f"{src}/{n}{e}" for e in (".png", ".webp") if os.path.exists(f"{src}/{n}{e}")), None)
    if not p:
        continue
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    ims.append((n, im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)))
W = sum(i.width for _, i in ims) + 14 * (len(ims) + 1)
hoja = Image.new("RGBA", (W, H + 44), (241, 249, 253, 255))
d = ImageDraw.Draw(hoja)
x = 14
for n, im in ims:
    hoja.alpha_composite(im, (x, 34)); d.text((x, 10), n[:16], fill=(40, 40, 40)); x += im.width + 14
hoja.convert("RGB").save(out)
print(out, hoja.size, len(ims), "productos")
