# -*- coding: utf-8 -*-
"""
02_construir_escena.py  —  Giro de la botella Clara -> Eco Agua para el hero web (Blender 4.5+, Cycles)

Construye la escena desde cero con los insumos de 01_preparar_insumos.py:
  - botella como sólido de revolución (perfil de la silueta real), vidrio/agua IOR 1.4
  - tapa con color que cruza de azul (Clara) a gris (Eco) en el giro
  - etiqueta cilíndrica con dos texturas (agua / eco) que se cruzan cuando el dorso mira a cámara
  - la foto de la cordillera como entorno: plano detrás (refracción) y plano delante (reflejo),
    ambos invisibles a cámara; película transparente -> PNG con alpha para componer en la web
  - 120 frames: 0° -> 360°, cruce agua->eco entre los frames 55 y 65 (180°)

Uso (desde la carpeta 03 BLENDER GIRO BOTELLA):
  blender -b -P 02_construir_escena.py                 -> construye y guarda giro_botella_v001.blend
  blender -b -P 02_construir_escena.py -- --test       -> además renderiza frames 1, 60 y 100 a render_test/
  blender -b -P 02_construir_escena.py -- --render     -> renderiza la animación completa a render/giro_####.png
"""
import bpy, json, math, os, sys

BASE = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA"
INS = BASE + "/insumos"
CORD = "E:/GRACIANI/WEB GRAZIANI/02 SITIO NUEVO/assets/hero/cordillera.jpg"
BLEND_OUT = BASE + "/giro_botella_v001.blend"
FRAMES = 120
SWAP = (55, 65)            # cruce agua -> eco (la etiqueta mira al dorso alrededor del frame 60)
RES = (800, 2000)          # encuadre vertical, igual que el placeholder web (giro_###.webp)
SAMPLES_FULL, SAMPLES_TEST = 64, 24   # con denoise, 64 alcanza para web (~10 s/frame en RTX 4090)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE_TEST, MODE_RENDER = "--test" in argv, "--render" in argv

info = json.load(open(INS + "/perfil_botella.json"))
ALTO = info["alto_m"]
perfil = info["perfil"]                     # [[z, r], ...] de abajo hacia arriba
Z_TAPA = info["tapa_desde_z"]
Z_LAB0, Z_LAB1 = info["etiqueta_z"]
R_LAB = info["r_etiqueta_m"]

# ---------------------------------------------------------------- escena limpia
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

def nodos(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt

def keyframe_swap(socket):
    """0 antes del cruce, 1 después (curva suave entre SWAP[0] y SWAP[1])."""
    socket.default_value = 0.0
    socket.keyframe_insert("default_value", frame=SWAP[0])
    socket.default_value = 1.0
    socket.keyframe_insert("default_value", frame=SWAP[1])

# ---------------------------------------------------------------- botella (sólido de revolución)
verts = [(0.0, 0.0, perfil[0][0])] + [(r, 0.0, z) for z, r in perfil] + [(0.0, 0.0, perfil[-1][0])]
edges = [(i, i + 1) for i in range(len(verts) - 1)]
mesh = bpy.data.meshes.new("PerfilBotella")
mesh.from_pydata(verts, edges, [])
bot = bpy.data.objects.new("Botella", mesh)
scene.collection.objects.link(bot)
bpy.context.view_layer.objects.active = bot
bot.select_set(True)
screw = bot.modifiers.new("Screw", "SCREW")
screw.axis = "Z"; screw.angle = math.tau; screw.steps = 128; screw.render_steps = 128
screw.screw_offset = 0.0; screw.iterations = 1
screw.use_merge_vertices = True; screw.merge_threshold = 1e-5; screw.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier="Screw")
try:
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
except Exception:
    bpy.ops.object.shade_smooth()

mat_vidrio = bpy.data.materials.new("Vidrio_Agua")
nt = nodos(mat_vidrio)
out = nt.nodes.new("ShaderNodeOutputMaterial")
glass = nt.nodes.new("ShaderNodeBsdfGlass")
glass.inputs["Color"].default_value = (0.90, 0.97, 1.0, 1.0)
glass.inputs["Roughness"].default_value = 0.02
glass.inputs["IOR"].default_value = 1.40
nt.links.new(glass.outputs["BSDF"], out.inputs["Surface"])

mat_tapa = bpy.data.materials.new("Tapa")
nt = nodos(mat_tapa)
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.6           # plástico mate: el reflejo de la nieve no lo lava
try:
    bsdf.inputs["Specular IOR Level"].default_value = 0.15
except KeyError:
    pass
mix = nt.nodes.new("ShaderNodeMixRGB")
# los colores medidos en la foto ya incluyen su iluminación: se bajan un 25 % para que el render los devuelva
ca = [v * 0.75 for v in info["color_tapa_agua"]]
ce = [v * 0.75 for v in info["color_tapa_eco"]]
mix.inputs["Color1"].default_value = (ca[0], ca[1], ca[2], 1.0)
mix.inputs["Color2"].default_value = (ce[0], ce[1], ce[2], 1.0)
keyframe_swap(mix.inputs["Fac"])
nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

bot.data.materials.append(mat_vidrio)
bot.data.materials.append(mat_tapa)
for p in bot.data.polygons:
    cz = sum(bot.data.vertices[v].co.z for v in p.vertices) / len(p.vertices)
    p.material_index = 1 if cz >= Z_TAPA else 0

# ---------------------------------------------------------------- etiqueta (cilindro con UV propio)
SEG = 128
r_e = R_LAB + 0.0007   # apenas por fuera del vidrio para que no lo atraviese
lv, lf, luv = [], [], []
for j, z in enumerate((Z_LAB0, Z_LAB1)):
    for i in range(SEG + 1):
        # u=0.5 al frente (-Y). u crece en sentido antihorario visto desde arriba
        u = i / SEG
        ang = (u - 0.5) * math.tau - math.pi / 2   # u=0.5 -> ángulo -90° (= -Y)
        lv.append((r_e * math.cos(ang), r_e * math.sin(ang), z))
for i in range(SEG):
    a0, a1, b0, b1 = i, i + 1, SEG + 1 + i, SEG + 1 + i + 1
    lf.append((a0, a1, b1, b0))
    luv.append([(a0 / SEG, 0.0), (a1 / SEG, 0.0), (a1 / SEG, 1.0), (a0 / SEG, 1.0)])
lmesh = bpy.data.meshes.new("EtiquetaMesh")
lmesh.from_pydata(lv, [], lf)
uv = lmesh.uv_layers.new(name="UVMap")
k = 0
for f in luv:
    for (u, v) in f:
        uv.data[k].uv = (u, v); k += 1
etiqueta = bpy.data.objects.new("Etiqueta", lmesh)
scene.collection.objects.link(etiqueta)
bpy.ops.object.select_all(action="DESELECT")
etiqueta.select_set(True); bpy.context.view_layer.objects.active = etiqueta
bpy.ops.object.shade_smooth()
etiqueta.parent = bot

mat_et = bpy.data.materials.new("Etiqueta")
nt = nodos(mat_et)
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.62          # papel/film mate: que no se lave con el brillo
try:
    bsdf.inputs["Specular IOR Level"].default_value = 0.22
except KeyError:
    pass
tex_a = nt.nodes.new("ShaderNodeTexImage"); tex_a.image = bpy.data.images.load(INS + "/etiqueta_agua.png"); tex_a.label = "Etiqueta Agua"
tex_e = nt.nodes.new("ShaderNodeTexImage"); tex_e.image = bpy.data.images.load(INS + "/etiqueta_eco.png"); tex_e.label = "Etiqueta Eco"
mix_c = nt.nodes.new("ShaderNodeMixRGB"); mix_c.label = "Cruce color"
mix_a = nt.nodes.new("ShaderNodeMixRGB"); mix_a.label = "Cruce alpha"
keyframe_swap(mix_c.inputs["Fac"]); keyframe_swap(mix_a.inputs["Fac"])
nt.links.new(tex_a.outputs["Color"], mix_c.inputs["Color1"]); nt.links.new(tex_e.outputs["Color"], mix_c.inputs["Color2"])
nt.links.new(tex_a.outputs["Alpha"], mix_a.inputs["Color1"]); nt.links.new(tex_e.outputs["Alpha"], mix_a.inputs["Color2"])
nt.links.new(mix_c.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(mix_a.outputs["Color"], bsdf.inputs["Alpha"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
etiqueta.data.materials.append(mat_et)

# ---------------------------------------------------------------- giro 0 -> 360°
bot.rotation_euler = (0.0, 0.0, 0.0)
bot.keyframe_insert("rotation_euler", index=2, frame=1)
bot.rotation_euler = (0.0, 0.0, math.tau)
bot.keyframe_insert("rotation_euler", index=2, frame=FRAMES)
for fc in bot.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# ---------------------------------------------------------------- entorno: cordillera refractada y reflejada
def plano_cordillera(nombre, y, ancho, flip, fuerza=0.75):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, y, ALTO / 2))
    p = bpy.context.active_object
    p.name = nombre
    p.rotation_euler = (math.pi / 2, 0.0, 0.0 if not flip else math.pi)   # vertical, mirando a la botella
    p.scale = (ancho, ancho * 1079 / 1917, 1.0)
    m = bpy.data.materials.new(nombre)
    nt = nodos(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = fuerza
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(CORD)
    nt.links.new(tx.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    p.data.materials.append(m)
    p.visible_camera = False
    p.visible_shadow = False
    return p

fondo = plano_cordillera("Cordillera_Fondo", y=+1.6, ancho=4.0, flip=False, fuerza=0.75)   # detrás: se ve a través del agua
frente = plano_cordillera("Cordillera_Reflejo", y=-2.2, ancho=5.0, flip=True, fuerza=0.30) # delante: aparece en los reflejos (suave)
frente.visible_transmission = False
frente.visible_diffuse = False

world = bpy.data.worlds.new("Cielo") if not scene.world else scene.world
scene.world = world
world.use_nodes = True
wn = world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
wout = wn.nodes.new("ShaderNodeOutputWorld")
wbg = wn.nodes.new("ShaderNodeBackground")
wbg.inputs["Color"].default_value = (0.62, 0.76, 0.92, 1.0)
wbg.inputs["Strength"].default_value = 0.45
wn.links.new(wbg.outputs["Background"], wout.inputs["Surface"])

# ---------------------------------------------------------------- luces y cámara
target = bpy.data.objects.new("Centro", None)
target.location = (0.0, 0.0, ALTO / 2)
scene.collection.objects.link(target)

def luz(nombre, loc, energia, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(nombre, "AREA")
    ld.energy = energia; ld.size = size; ld.color = color
    lo = bpy.data.objects.new(nombre, ld)
    lo.location = loc
    scene.collection.objects.link(lo)
    c = lo.constraints.new("TRACK_TO"); c.target = target; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return lo

luz("Key", (-0.7, -0.9, 0.9), 80, 0.9, (1.0, 0.97, 0.93))
luz("Fill", (0.9, -0.8, 0.4), 28, 1.2, (0.92, 0.96, 1.0))
luz("Rim", (0.5, 0.9, 0.8), 60, 0.5, (1.0, 1.0, 1.0))

cam_d = bpy.data.cameras.new("Camara")
cam_d.lens = 100.0
cam_d.sensor_fit = "VERTICAL"
cam_d.sensor_height = 36.0
fov_v = 2 * math.atan(cam_d.sensor_height / (2 * cam_d.lens))
alto_visible = ALTO / 0.86                          # la botella ocupa el 86 % del alto del cuadro
dist = alto_visible / (2 * math.tan(fov_v / 2))
cam = bpy.data.objects.new("Camara", cam_d)
cam.location = (0.0, -dist, ALTO / 2)
scene.collection.objects.link(cam)
c = cam.constraints.new("TRACK_TO"); c.target = target; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
scene.camera = cam

# ---------------------------------------------------------------- render
scene.render.engine = "CYCLES"
scene.cycles.samples = SAMPLES_TEST if MODE_TEST else SAMPLES_FULL
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12
scene.cycles.glossy_bounces = 6
scene.cycles.transparent_max_bounces = 12
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.film_transparent = True
scene.cycles.film_transparent_glass = True
scene.cycles.film_transparent_roughness = 0.1
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 50
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = -0.6
scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = 30
scene.render.filepath = BASE + "/render/giro_"

# GPU si hay (OptiX/CUDA); si no, CPU
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    usado = None
    for tipo in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = tipo
            try:
                prefs.refresh_devices()
            except Exception:
                prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == tipo]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type in (tipo, "CPU")
                usado = tipo
                break
        except Exception:
            continue
    scene.cycles.device = "GPU" if usado else "CPU"
    print("Cycles device:", scene.cycles.device, usado or "")
except Exception as e:
    print("GPU no configurada, CPU:", e)

os.makedirs(BASE + "/render", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("Guardado:", BLEND_OUT)

if MODE_TEST:
    os.makedirs(BASE + "/render_test", exist_ok=True)
    for f in (1, 60, 100):
        scene.frame_set(f)
        scene.render.filepath = BASE + f"/render_test/test_{f:04d}.png"
        bpy.ops.render.render(write_still=True)
        print("Render test:", scene.render.filepath)
    scene.render.filepath = BASE + "/render/giro_"
elif MODE_RENDER:
    bpy.ops.render.render(animation=True)
    print("Animación renderizada en", BASE + "/render/")
