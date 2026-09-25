# -*- coding: utf-8 -*-
r"""
exportar_web.py — Pasa los renders finales a las imágenes del carrusel de Productos (WebP con alpha, 900 px de alto)
y actualiza js\productos.js para que las use.

  python exportar_web.py

Origen:  E:\GRACIANI\WEB GRAZIANI\06 BLENDER PRODUCTOS WEB\render_final_junio\<producto>.png  (toda la línea)
         E:\GRACIANI\WEB GRAZIANI\06 BLENDER PRODUCTOS WEB\render_final_abril\agua500.png      (Clara 500, etiqueta topaz)
Destino: E:\GRACIANI\WEB GRAZIANI\02 SITIO NUEVO\assets\botellas\<producto>.webp

No se exportan (siguen las imágenes actuales):
  - amargos: el único .blend con sus texturas tiene la etiqueta "Nueva Versión" (la web muestra la anterior);
    los renders con la etiqueta nueva quedan en render_final_junio\ por si se decide cambiarlos.
  - saborizadas 2 L: las imágenes del cliente se ven mejor que el render (el líquido sale mostaza).
  - saborizadas 500 (manzana, naranja, pomelo): en el .blend el líquido tiene otro tono (la naranja sale amarilla y el
    pomelo gris) y bajar el contraluz no lo corrige; las actuales se ven mejor.
Las que se re-renderizan son las transparentes (aguas, sodas, Eco, Clara, Premium): eran las que se veían lechosas.
"""
import os, re
from PIL import Image, ImageChops, ImageFilter

BASE = "E:/GRACIANI/WEB GRAZIANI/06 BLENDER PRODUCTOS WEB"
SITIO = "E:/GRACIANI/WEB GRAZIANI/02 SITIO NUEVO"
DEST = SITIO + "/assets/botellas"
ORIGEN = {"agua500": "render_final_abril"}
PRODUCTOS = ["ecoagua500", "agua500", "agua1", "agua2", "agua6", "aguapremium", "soda500", "soda1", "soda2",
             "soda225", "sodapremium"]
ALTO = 900
VERSION = "20260925b"

total = 0
for p in PRODUCTOS:
    src = f"{BASE}/{ORIGEN.get(p, 'render_final_junio')}/{p}.png"
    im = Image.open(src).convert("RGBA")
    # los renders del .blend de junio traen puntitos de alfa muy tenue (<= 12/255) sueltos por todo el cuadro:
    # se anulan fuera de la silueta de la botella (alfa > 20, ensanchada 6 px) para que el recorte ajuste a la botella
    a = im.getchannel("A")
    nucleo = a.point(lambda v: 255 if v > 20 else 0).filter(ImageFilter.MaxFilter(13))
    im.putalpha(ImageChops.multiply(a, nucleo))
    bb = im.getchannel("A").point(lambda v: 255 if v > 2 else 0).getbbox()
    pad = round((bb[3] - bb[1]) * 0.008)
    bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad))
    im = im.crop(bb)
    # escalar premultiplicado: sin halo claro en el borde del vidrio
    im = im.convert("RGBa").resize((round(im.width * ALTO / im.height), ALTO), Image.LANCZOS).convert("RGBA")
    out = f"{DEST}/{p}.webp"
    im.save(out, "WEBP", quality=88, method=6)
    total += os.path.getsize(out)
    print(f"{p:14s} {im.width}x{im.height}  {os.path.getsize(out) // 1024} KB  <- {src}")
print(f"{len(PRODUCTOS)} imágenes, {total / 1e6:.2f} MB en {DEST}")

# productos.js: las exportadas pasan a .webp con ?v= (ecoagua500.webp cambia de contenido con el mismo nombre)
js = SITIO + "/js/productos.js"
s = open(js, encoding="utf-8", newline="").read()      # newline="": respeta los finales de línea del archivo
for p in PRODUCTOS:
    s, n = re.subn(rf'imagen: "assets/botellas/{re.escape(p)}\.(png|webp)(\?v=[0-9a-z]+)?"',
                   f'imagen: "assets/botellas/{p}.webp?v={VERSION}"', s)
    if n != 1:
        print("OJO productos.js:", p, "reemplazos", n)
open(js, "w", encoding="utf-8", newline="").write(s)
print("productos.js actualizado")
