# -*- coding: utf-8 -*-
"""Renderiza un rango de frames del .blend por CPU (cuando la GPU está ocupada por otro trabajo).
blender -b giro_botella_v008.blend -P _render_cpu.py -- DESDE HASTA HILOS
Mismas opciones de render que el .blend (samples, motion blur, denoise); salida render/giro_####.png."""
import bpy, sys

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
desde, hasta, hilos = (int(a) for a in (args + ["57", "120", "8"])[:3])
sc = bpy.context.scene
sc.cycles.device = "CPU"
sc.render.threads_mode = "FIXED"
sc.render.threads = hilos
sc.frame_start, sc.frame_end = desde, hasta
sc.render.filepath = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA/render/giro_"
print(f"CPU {hilos} hilos, frames {desde}-{hasta}, samples {sc.cycles.samples}")
bpy.ops.render.render(animation=True)
print("Animación renderizada (CPU)", desde, hasta)
