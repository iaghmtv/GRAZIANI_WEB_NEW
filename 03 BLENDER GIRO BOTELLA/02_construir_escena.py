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
BLEND_OUT = BASE + "/giro_botella_v005.blend"   # v005: giro con ease-in-out fuerte + motion blur (barrido), etiqueta Eco con contraste
GIRO_EASE = "CUBIC"        # curva del giro: arranca y termina suave, 3x la velocidad media a los 180° (cruce de etiquetas)
SHUTTER = 0.85             # motion blur: fracción del frame que expone (barrido en la parte rápida)
TAPA_ECO_ALTO = 0.66      # la tapa Eco es "short": 66 % del alto de la tapa Clara (referencia: render par de junio)
COLOR_TAPA_ECO = (0.018, 0.018, 0.02, 1.0)   # negra
FRAMES = 120
SWAP = (57, 64)            # cruce agua -> eco: centrado en los 180° (frame 60.5), en la parte más rápida del giro
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

# ---------------------------------------------------------------- sólidos de revolución: botella (sin tapa) y tapa aparte
def lathe(nombre, puntos_zr, z_ini, z_fin):
    """Cuerpo de revolución cerrado en el eje: (0,0,z_ini) -> perfil -> (0,0,z_fin)."""
    vs = [(0.0, 0.0, z_ini)] + [(r, 0.0, z) for z, r in puntos_zr] + [(0.0, 0.0, z_fin)]
    es = [(i, i + 1) for i in range(len(vs) - 1)]
    m = bpy.data.meshes.new("Perfil" + nombre); m.from_pydata(vs, es, [])
    o = bpy.data.objects.new(nombre, m); scene.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    sc = o.modifiers.new("Screw", "SCREW")
    sc.axis = "Z"; sc.angle = math.tau; sc.steps = 128; sc.render_steps = 128
    sc.screw_offset = 0.0; sc.iterations = 1
    sc.use_merge_vertices = True; sc.merge_threshold = 1e-5; sc.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier="Screw")
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    except Exception:
        bpy.ops.object.shade_smooth()
    return o

cuerpo = [(z, r) for z, r in perfil if z < Z_TAPA]
bot = lathe("Botella", cuerpo, cuerpo[0][0], Z_TAPA)          # sellada arriba (queda dentro de la tapa)
tapa_pts = [(z, r) for z, r in perfil if z >= Z_TAPA]
tapa = lathe("Tapa", tapa_pts, Z_TAPA, tapa_pts[-1][0])
tapa.parent = bot
# shape key "corta": la tapa Eco es más baja, anclada en su base
tapa.shape_key_add(name="Basis", from_mix=False)
sk = tapa.shape_key_add(name="corta", from_mix=False)
for i in range(len(tapa.data.vertices)):
    co = sk.data[i].co
    co.z = Z_TAPA + (co.z - Z_TAPA) * TAPA_ECO_ALTO
sk.value = 0.0; sk.keyframe_insert("value", frame=SWAP[0])
sk.value = 1.0; sk.keyframe_insert("value", frame=SWAP[1])
bpy.ops.object.select_all(action="DESELECT"); bot.select_set(True); bpy.context.view_layer.objects.active = bot

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
# tapa Clara azul (azul pleno tipo #4A80DB de la referencia; el medido en la foto salía pálido) -> tapa Eco negra
mix.inputs["Color1"].default_value = (0.10, 0.28, 0.72, 1.0)
mix.inputs["Color2"].default_value = COLOR_TAPA_ECO
keyframe_swap(mix.inputs["Fac"])
nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

bot.data.materials.append(mat_vidrio)
tapa.data.materials.append(mat_tapa)

# ---------------------------------------------------------------- gotas de condensación (malla propia, hija de la botella)
# Domos achatados apoyados en la superficie de revolución; giran con la botella y hacen legible el giro.
import numpy as np
N_GOTAS = 950
rng = np.random.default_rng(7)
zs_p = np.array([z for z, r in perfil]); rs_p = np.array([r for z, r in perfil])
def radio(z): return float(np.interp(z, zs_p, rs_p))
def normal_rz(z):
    dz = 0.0008
    dr = (radio(z + dz) - radio(z - dz)) / (2 * dz)
    n = np.array([1.0, -dr]); return n / np.linalg.norm(n)          # (n_r, n_z)
cands = []
zmin, zmax = 0.006, Z_TAPA - 0.004
while len(cands) < N_GOTAS:
    z = rng.uniform(zmin, zmax)
    if Z_LAB0 - 0.002 <= z <= Z_LAB1 + 0.002 and rng.random() > 0.12:
        continue                                                     # pocas gotas sobre la etiqueta
    r = radio(z)
    if r < 0.009 or rng.random() > r / rs_p.max():                   # sin gotas en el cuello; densidad ∝ perímetro
        continue
    cands.append((z, r, rng.uniform(0.0, math.tau)))
R_AN, S_SEG = 4, 12
gv, gf = [], []
for (z, r, th) in cands:
    s = rng.uniform(0.00045, 0.0021)                                 # radio de la gota: 0,45–2,1 mm
    h = rng.uniform(0.35, 0.62)                                      # achatamiento
    n_r, n_z = normal_rz(z)
    n3 = np.array([n_r * math.cos(th), n_r * math.sin(th), n_z]); n3 /= np.linalg.norm(n3)
    t1 = np.array([-math.sin(th), math.cos(th), 0.0]); t2 = np.cross(n3, t1)
    c = np.array([r * math.cos(th), r * math.sin(th), z]) - n3 * (s * h * 0.35)
    base = len(gv)
    gv.append(tuple(c + n3 * (s * h)))                               # polo
    for i in range(1, R_AN + 1):
        phi = (math.pi / 2) * i / R_AN
        for j in range(S_SEG):
            lam = math.tau * j / S_SEG
            x, y, zz = math.sin(phi) * math.cos(lam), math.sin(phi) * math.sin(lam), math.cos(phi)
            gv.append(tuple(c + t1 * (s * x) + t2 * (s * y) + n3 * (s * h * zz)))
    for j in range(S_SEG):
        gf.append((base, base + 1 + (j + 1) % S_SEG, base + 1 + j))
    for i in range(1, R_AN):
        for j in range(S_SEG):
            a = base + 1 + (i - 1) * S_SEG + j; b = base + 1 + (i - 1) * S_SEG + (j + 1) % S_SEG
            c2 = base + 1 + i * S_SEG + (j + 1) % S_SEG; d = base + 1 + i * S_SEG + j
            gf.append((a, b, c2, d))
gmesh = bpy.data.meshes.new("GotasMesh"); gmesh.from_pydata(gv, [], gf)
gotas = bpy.data.objects.new("Gotas", gmesh); scene.collection.objects.link(gotas)
bpy.ops.object.select_all(action="DESELECT"); gotas.select_set(True); bpy.context.view_layer.objects.active = gotas
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.shade_smooth()
gotas.parent = bot
mat_gota = bpy.data.materials.new("Gota")
nt = nodos(mat_gota)
out = nt.nodes.new("ShaderNodeOutputMaterial")
gl = nt.nodes.new("ShaderNodeBsdfGlass")
gl.inputs["Color"].default_value = (0.96, 0.99, 1.0, 1.0)
gl.inputs["Roughness"].default_value = 0.04
gl.inputs["IOR"].default_value = 1.33
nt.links.new(gl.outputs["BSDF"], out.inputs["Surface"])
gotas.data.materials.append(mat_gota)
print("Gotas:", len(cands))

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
        kp.interpolation = GIRO_EASE        # ease-in-out: lento al inicio y al final, rápido en el medio
        kp.easing = "EASE_IN_OUT"

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

fondo = plano_cordillera("Cordillera_Fondo", y=+1.6, ancho=4.0, flip=False, fuerza=0.55)   # detrás: se ve a través del agua
frente = plano_cordillera("Cordillera_Reflejo", y=-2.2, ancho=5.0, flip=True, fuerza=0.22) # delante: aparece en los reflejos (suave)
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
wbg.inputs["Strength"].default_value = 0.35
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

luz("Key", (-0.7, -0.9, 0.9), 55, 0.9, (1.0, 0.97, 0.93))
luz("Fill", (0.9, -0.8, 0.4), 20, 1.2, (0.92, 0.96, 1.0))
luz("Rim", (0.5, 0.9, 0.8), 45, 0.5, (1.0, 1.0, 1.0))

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
# barrido: motion blur real de Cycles (la etiqueta se desenfoca solo donde el giro es rápido)
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = SHUTTER
try:
    scene.cycles.motion_blur_position = "CENTER"
except Exception:
    pass
scene.cycles.film_transparent_roughness = 0.1
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 50
# AgX comprime las altas luces en vez de recortarlas: el vidrio no queda "quemado"
try:
    scene.view_settings.view_transform = "AgX"
except TypeError:
    scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "None"
scene.view_settings.exposure = -0.35
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
