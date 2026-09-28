# -*- coding: utf-8 -*-
r"""
05_render_extra.py — Tramos extra del giro para los videos 9:16 (misma escena v009; el .blend NO se guarda).

  blender -b giro_botella_v009.blend -P 05_render_extra.py -- entrada [--test]
        -> render_entrada\entrada_0001..0045.png
  blender -b giro_botella_v009.blend -P 05_render_extra.py -- vuelta [--test]
        -> render_vuelta\vuelta_0001..0120.png

entrada: la Clara entra girando HACIA ADELANTE (el mismo sentido del giro principal): -180° -> 0° en 45 frames
         (1,5 s), frenando con ease-out cuadrático (como el power2.out de la web). Etiqueta Clara y tapa azul fijas.
vuelta:  segundo giro de 3 vueltas en el mismo sentido que termina de nuevo en la Clara: la etiqueta cruza
         Eco -> Clara en los frames 44-56 y la tapa negra corta -> azul alta en 77-97 (los mismos tramos que la ida),
         así el video puede quedar en loop.
--test:  renderiza solo algunos frames a 24 samples en render_test_extra\ para revisar antes.
"""
import bpy, math, sys, os

BASE = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA"
argv = sys.argv[sys.argv.index("--") + 1:]
MODO = argv[0]
TEST = "--test" in argv
sc = bpy.context.scene
bot = bpy.data.objects["Botella"]
tapa = bpy.data.objects["Tapa"]
nt_et = bpy.data.materials["Etiqueta"].node_tree
nt_tapa = bpy.data.materials["Tapa"].node_tree
cruce = next(n for n in nt_et.nodes if n.bl_idname == "ShaderNodeValue")          # "Cruce etiqueta" 0 Clara / 1 Eco
mix_tapa = next(n for n in nt_tapa.nodes if n.bl_idname == "ShaderNodeMixRGB")    # 0 azul / 1 negra
sk = tapa.data.shape_keys.key_blocks["corta"]                                      # 0 alta / 1 corta

# fuera las animaciones de la ida: se rearman según el tramo
for idb in (bot, nt_et, nt_tapa, tapa.data.shape_keys):
    if idb.animation_data:
        idb.animation_data_clear()

def llave_cruce(v0, v1, f0, f1):
    s = cruce.outputs[0]
    s.default_value = v0; s.keyframe_insert("default_value", frame=f0)
    s.default_value = v1; s.keyframe_insert("default_value", frame=f1)

def llave_tapa(v0, v1, f0, f1):
    s = mix_tapa.inputs["Fac"]
    s.default_value = v0; s.keyframe_insert("default_value", frame=f0)
    s.default_value = v1; s.keyframe_insert("default_value", frame=f1)
    sk.value = v0; sk.keyframe_insert("value", frame=f0)
    sk.value = v1; sk.keyframe_insert("value", frame=f1)

def giro(ang0, ang1, f0, f1, interp, easing):
    bot.rotation_euler = (0.0, 0.0, ang0); bot.keyframe_insert("rotation_euler", index=2, frame=f0)
    bot.rotation_euler = (0.0, 0.0, ang1); bot.keyframe_insert("rotation_euler", index=2, frame=f1)
    for fc in bot.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = interp
            kp.easing = easing

if MODO == "entrada":
    FR = 45
    giro(-math.pi, 0.0, 1, FR, "QUAD", "EASE_OUT")
    cruce.outputs[0].default_value = 0.0                 # Clara
    mix_tapa.inputs["Fac"].default_value = 0.0            # tapa azul
    sk.value = 0.0                                        # tapa alta
    test_frames = (1, 12, 30, 45)
elif MODO == "vuelta":
    FR = 120
    giro(0.0, 3 * math.tau, 1, FR, "CUBIC", "EASE_IN_OUT")   # misma curva que la ida
    llave_cruce(1.0, 0.0, 44, 56)                              # Eco -> Clara con el giro rápido
    llave_tapa(1.0, 0.0, 77, 97)                               # negra corta -> azul alta en la desaceleración
    test_frames = (1, 50, 87, 120)
else:
    raise SystemExit("modo: entrada | vuelta")

sc.frame_start, sc.frame_end = 1, FR
if "--desde" in argv:                                    # retomar un render cortado desde ese frame
    sc.frame_start = int(argv[argv.index("--desde") + 1])

# GPU (OptiX) si hay y no se pidió --cpu (la GPU ocupada por otro trabajo): CPU con 16 hilos (la mitad)
if "--cpu" in argv:
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 16
else:
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        try:
            prefs.refresh_devices()
        except Exception:
            prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == "OPTIX"]
        for d in prefs.devices:
            d.use = d.type in ("OPTIX", "CPU")
        sc.cycles.device = "GPU" if gpus else "CPU"
    except Exception as e:
        sc.cycles.device = "CPU"; print("GPU no disponible:", e)
print("MODO", MODO, "frames", FR, "device", sc.cycles.device)

if TEST:
    sc.cycles.samples = 24
    os.makedirs(BASE + "/render_test_extra", exist_ok=True)
    for f in test_frames:
        sc.frame_set(f)
        sc.render.filepath = f"{BASE}/render_test_extra/{MODO}_{f:04d}.png"
        bpy.ops.render.render(write_still=True)
        print("TEST", sc.render.filepath, "rot", round(math.degrees(bot.rotation_euler[2]), 1),
              "cruce", round(cruce.outputs[0].default_value, 2), "tapa", round(mix_tapa.inputs["Fac"].default_value, 2))
else:
    os.makedirs(f"{BASE}/render_{MODO}", exist_ok=True)
    sc.render.filepath = f"{BASE}/render_{MODO}/{MODO}_"
    bpy.ops.render.render(animation=True)
    print("LISTO", MODO)
