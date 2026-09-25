# -*- coding: utf-8 -*-
r"""
productos_web.py — Re-render de las botellas del carrusel de Productos para la web (fondo celeste #f1f9fd).

Abre una escena de producto del proyecto Botellas Finales SIN GUARDARLA (los .blend del usuario no se modifican):
  junio: E:\GRACIANI\Botellas Finales\Graziani Botellas_FondosNuevosColores_Camara 90 mm_Amargos Nuevas Etiqueta verde EXP tapa shortclaude 1.blend
         (toda la línea; la 500 cc ya tiene la etiqueta Eco verde; amargos con la etiqueta "Nueva Versión")
  abril: E:\GRACIANI\Botellas Finales\Graziani Botellas_FondosNuevosColores_Camara 90 mm.blend
         (amargos con las etiquetas que muestra hoy la web; 500 cc Clara)
Por cada producto deja visible solo su colección (con su SetLight) y lo encuadra con una cámara propia.

  blender -b "<blend>" -P productos_web.py -- modo=web productos=agua1,soda2|todos res=100 samples=256 device=GPU
                        [look="AgX - Medium High Contrast"] [flags=1] [base_brillo=1] [renombrar=agua500>ecoagua500]
                        [salida=<carpeta>]

modo=base  la escena como está (ciclorama blanco + esfera de luz visibles): así se hicieron los PNG de la web actual.
modo=web   - lo que se ve A TRAVÉS del vidrio es el celeste de la página (mundo con Light Path: rayos de transmisión =
             celeste calibrado para salir #f1f9fd con AgX; reflejos = el HDRI de estudio de la escena);
           - la esfera de luz y el ciclorama siguen iluminando pero no se ven de fondo ni a través del vidrio;
           - dos banderas negras a los costados dibujan el borde de la botella (contraste sobre fondo claro);
           - sin gotas (a 250 px de alto se leían como suciedad); look de AgX con más contraste.
"""
import bpy, sys, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ARGS = dict(a.split("=", 1) for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if "=" in a)
MODO = ARGS.get("modo", "web")
RES = int(ARGS.get("res", "25"))
SAMPLES = int(ARGS.get("samples", "32"))
DEVICE = ARGS.get("device", "CPU")
LOOK = ARGS.get("look", "AgX - Medium High Contrast")
FLAGS = ARGS.get("flags", "1") == "1"
BASE_BRILLO = ARGS.get("base_brillo", "1") == "1"     # el ciclorama blanco se sigue viendo en los reflejos
SALIDA = ARGS.get("salida", "E:/GRACIANI/WEB GRAZIANI/06 BLENDER PRODUCTOS WEB/render_" + MODO)
RENOMBRAR = dict(r.split(">") for r in ARGS.get("renombrar", "").split(",") if ">" in r)
CELESTE_TRANS = ((0.55, 0.88, 1.0, 1.0), 6.0)          # sale (241, 248, 251) con AgX Medium High Contrast (calibrado)
# Líquidos de color: con el contraluz a 6 AgX los lleva al pastel (desatura lo muy luminoso). Se les baja el contraluz;
# el fondo no se ve (película transparente), solo tiñe lo que se ve a través del líquido.
FUERZA_COLOR = float(ARGS.get("fuerza_color", "2.0"))
DE_COLOR = ("amargo", "manzana", "naranja", "pomelo", "saborizada")
FRAME = (1000, 2000)                                   # vertical 1:2; la botella ocupa ~92 % del alto
LENTE = 85.0

# producto web -> (colección, cámara de referencia: de ella sale el "frente")
PRODUCTOS = {
    "agua500":              ("Agua_Clara Graziani_Sin Gas 500Cc", "Camera-70mm"),
    "agua1":                ("Agua Sin Gas_1 Lt", "Camera-70mm.005"),
    "agua2":                ("Agua Sin Gas 2 Lt", "Camera-nieve.004"),
    "agua6":                ("Agua SIn Gas 6Lt", "Camera-nieve.003"),
    "aguapremium":          ("Agua Premium_500Cc", "Camera-nieve.005"),
    "soda500":              ("Soda 500Cc", "Camera-70"),
    "soda1":                ("Soda_1Lt", "Camera-70mm.001"),
    "soda2":                ("Soda_Sifon 2Lt", "Camera-70mm.003"),
    "soda225":              ("Soda_2.25 Lt", "Camera-70mm.002"),
    "sodapremium":          ("Premium_Soda_500Cc", "Camera-70mm.004"),
    "amargocitrus":         ("Amargo Citrus", "Camera-Amargo"),
    "amargocordillerano":   ("Amargo Cordillerano", "Camera-Amargo"),
    "amargolimon":          ("Amargo Limon", "Camera-Amargo"),
    "amargopomelo":         ("Amargo Pomelo", "Camera-Amargo"),
    "amargoserrano":        ("Amargo Serrano", "Camera-Amargo"),
    "manzana":              ("Premium_Jugos _sabores Manzana", "Camera-Jugos"),
    "naranja":              ("Premium_Jugos _sabores Naranja", "Camera-Jugos"),
    "pomelo":               ("Premium_Jugos _sabores Pomelo", "Camera-Jugos"),
    "saborizada2l-naranja": ("Agua Siaborizada Naranaja 2 Lt", "Camera-nieve.006"),
    "saborizada2l-manzana": ("Agua Siaborizada Manzana 2 Lt", "Camera-nieve.002"),
    "saborizada2l-pomelo":  ("Agua Siaborizada Pomelo 2 Lt", "Camera-nieve.001"),
}
lista = [p for p in PRODUCTOS if bpy.data.collections.get(PRODUCTOS[p][0])] if ARGS.get("productos", "todos") == "todos" \
    else ARGS["productos"].split(",")

sc = bpy.context.scene
vl = sc.view_layers[0]

BUSCAR_EN = ["E:/GRACIANI/Botellas Finales/textures", "E:/GRACIANI/Botellas Finales"]
def reparar_texturas():
    """Las imágenes con ruta rota (el proyecto original vivía en otra carpeta) se buscan por nombre en textures\."""
    faltan = []
    for im in bpy.data.images:
        if im.source != "FILE" or im.packed_file:
            continue
        ruta = bpy.path.abspath(im.filepath)
        if os.path.exists(ruta):
            continue
        base = os.path.basename(im.filepath.replace("\\", "/"))
        nueva = next((f"{d}/{base}" for d in BUSCAR_EN if os.path.exists(f"{d}/{base}")), None)
        if nueva:
            im.filepath = nueva; im.reload(); print("TEXTURA reenlazada:", base, "->", nueva)
        else:
            faltan.append(base)
    print("TEXTURAS sin archivo:", faltan)
reparar_texturas()

# Tapas que en el .blend no tienen el color del producto real (lineal):
#  Eco 500: negra (en el .blend de junio quedó gris clara)
#  agua 2 L: azul como en la web (usa el material gris compartido " Plastic_Bottle", ver HANDOFF de Botellas Finales)
TAPAS = {"ecoagua500": (0.012, 0.012, 0.014), "agua2": (0.03, 0.22, 0.62)}
def tapa_color(objs, nombre):
    color = TAPAS[nombre]
    m = bpy.data.materials.get("WEB_tapa_" + nombre) or bpy.data.materials.new("WEB_tapa_" + nombre)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = 0.35
    for o in objs:
        if "tapa" in o.name.lower():
            for sl in o.material_slots:
                sl.link = "OBJECT"; sl.material = m
            print("TAPA", nombre, color, "->", o.name)

def recorrer(lc, padres=()):
    """(layer_collection, nombres de los padres) de arriba hacia abajo, sin la raíz."""
    for c in lc.children:
        yield c, padres
        yield from recorrer(c, padres + (c.name,))

def solo(coleccion):
    """Deja en la vista solo la colección del producto (con todos sus hijos), su cadena de padres y el ciclorama.
    De arriba hacia abajo y SIN tocar la raíz: al incluir un padre Blender restaura el estado previo de sus hijas,
    por eso cada hija se fija después que su padre."""
    guardar = {"Base"}
    for lc, padres in recorrer(vl.layer_collection):
        if lc.name == coleccion:
            guardar |= set(padres) | {lc.name}
            def sub(x):
                guardar.add(x.name)
                for c in x.children:
                    sub(c)
            sub(lc)
    for lc, padres in recorrer(vl.layer_collection):
        lc.exclude = lc.name not in guardar

def config_render():
    sc.render.engine = "CYCLES"
    sc.cycles.device = DEVICE
    if DEVICE == "GPU":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        try:
            prefs.refresh_devices()
        except Exception:
            prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type in ("OPTIX", "CPU")
    else:
        sc.render.threads_mode = "FIXED"; sc.render.threads = 16
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.sample_clamp_indirect = 3.0      # plástico transparente = fireflies (lección del proyecto Cenital)
    sc.cycles.sample_clamp_direct = 15.0
    sc.render.resolution_x, sc.render.resolution_y = FRAME
    sc.render.resolution_percentage = RES
    sc.render.film_transparent = True
    sc.cycles.film_transparent_glass = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"

def mundo_web():
    """Rayos de transmisión -> celeste de la página; el resto (reflejos, luz difusa) -> el HDRI de estudio de siempre."""
    nt = sc.world.node_tree
    out = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputWorld")
    previo = out.inputs["Surface"].links[0].from_socket
    lp = nt.nodes.new("ShaderNodeLightPath")
    global CEL
    cel = CEL = nt.nodes.new("ShaderNodeBackground")
    cel.inputs["Color"].default_value, cel.inputs["Strength"].default_value = CELESTE_TRANS
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Transmission Ray"], mix.inputs["Fac"])
    nt.links.new(previo, mix.inputs[1])
    nt.links.new(cel.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])

def preparar_web():
    for n in ("Sphere LUZ", "BAse_Blanco"):
        o = bpy.data.objects.get(n)
        if o:
            o.visible_camera = False          # no aparece de fondo
            o.visible_transmission = False    # a través del vidrio no se ve blanco: se ve el mundo celeste
            if n == "BAse_Blanco":
                o.visible_glossy = BASE_BRILLO
    for o in bpy.data.objects:
        if "gotas" in o.name.lower():
            o.hide_render = True
    mundo_web()
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = float(ARGS.get("exposicion", "0"))
    try:
        sc.view_settings.look = LOOK
    except TypeError:
        print("look no disponible:", LOOK)

MAT_BANDERA = None
def banderas(centro, alto, ancho, cam):
    """Dos banderas negras altas a los costados, un poco detrás de la botella: el borde del vidrio las refleja y
    refracta como una línea oscura (lo que en foto de producto se hace con cartulinas negras). No se ven a cámara
    ni le sacan luz a la etiqueta."""
    global MAT_BANDERA
    for o in [o for o in bpy.data.objects if o.name.startswith("WEB_bandera")]:
        bpy.data.objects.remove(o, do_unlink=True)
    if not FLAGS:
        return
    if MAT_BANDERA is None:
        MAT_BANDERA = bpy.data.materials.new("WEB_bandera_negra")
        MAT_BANDERA.use_nodes = True
        b = MAT_BANDERA.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (0.003, 0.003, 0.003, 1)
        b.inputs["Roughness"].default_value = 1.0
        try:
            b.inputs["Specular IOR Level"].default_value = 0.0
        except KeyError:
            pass
    der = (cam.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
    fwd = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    for lado in (-1, 1):
        me = bpy.data.meshes.new("WEB_bandera")
        w, h = alto * 0.9, alto * 2.4
        me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
        ob = bpy.data.objects.new(f"WEB_bandera_{'izq' if lado < 0 else 'der'}", me)
        sc.collection.objects.link(ob)
        ob.location = centro + der * lado * (ancho * 0.5 + alto * 0.55) + fwd * (alto * 0.25)
        mira = centro - ob.location
        mira.z = 0
        ob.rotation_euler = mira.to_track_quat("-Y", "Z").to_euler()
        ob.data.materials.append(MAT_BANDERA)
        ob.visible_camera = False
        ob.visible_shadow = False
        ob.visible_diffuse = False

FRONTAL = float(ARGS.get("frontal", "0"))     # W de la luz frontal de relleno, referidos a 0,6 m (se escala con la distancia)
FRONTAL_EN = ("agua500", "ecoagua500")        # etiquetas de papel perlado: sin relleno el blanco se ve gris
def luz_frontal(centro, alto, objs, nombre):
    """Relleno frontal grande desde la cámara, enlazado (light linking) SOLO a la etiqueta: el papel blanco deja de
    verse gris y el vidrio, los líquidos y las otras etiquetas no cambian."""
    ob = bpy.data.objects.get("WEB_frontal")
    if FRONTAL <= 0 or nombre not in FRONTAL_EN:
        if ob: ob.hide_render = True
        return
    if ob is None:
        ld = bpy.data.lights.new("WEB_frontal", "AREA"); ld.shape = "RECTANGLE"
        ob = bpy.data.objects.new("WEB_frontal", ld); sc.collection.objects.link(ob)
    up = (CAM.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    ob.location = CAM.location + up * alto * 0.35
    ob.rotation_euler = (centro - ob.location).to_track_quat("-Z", "Y").to_euler()
    d = (centro - ob.location).length
    ob.data.size, ob.data.size_y = alto * 1.2, alto * 1.6
    ob.data.energy = FRONTAL * (d / 0.6) ** 2
    ob.visible_glossy = False; ob.visible_transmission = False; ob.visible_camera = False
    rc = bpy.data.collections.get("WEB_receptores") or bpy.data.collections.new("WEB_receptores")
    for o in list(rc.objects):
        rc.objects.unlink(o)
    for o in objs:
        if "etiqueta" in o.name.lower():
            rc.objects.link(o)
    ob.light_linking.receiver_collection = rc
    ob.hide_render = False
    print("FRONTAL", nombre, f"{ob.data.energy:.1f} W ->", [o.name for o in rc.objects])

CEL = None
CAM = None
def encuadrar(objs, cam_ref):
    """Cámara 85 mm nivelada a media altura de la botella, mirando en la dirección (horizontal) de la cámara del
    producto; la distancia se ajusta para que la botella ocupe el 92 % del alto (o del ancho si es más ancha)."""
    global CAM
    if CAM is None:
        cd = bpy.data.cameras.new("WEB_cam"); cd.lens = LENTE; cd.sensor_fit = "AUTO"; cd.sensor_width = 36.0
        cd.clip_start = 0.01; cd.clip_end = 100.0
        CAM = bpy.data.objects.new("WEB_cam", cd); sc.collection.objects.link(CAM)
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centro = (lo + hi) / 2
    f = cam_ref.matrix_world.to_3x3() @ Vector((0, 0, -1)); f.z = 0; f.normalize()
    CAM.rotation_euler = f.to_track_quat("-Z", "Y").to_euler()
    sc.camera = CAM
    a, b = 0.05, 20.0
    for _ in range(40):
        d = (a + b) / 2
        CAM.location = centro - f * d
        bpy.context.view_layer.update()
        pr = [world_to_camera_view(sc, CAM, p) for p in pts]
        ext = max(max(q.y for q in pr) - min(q.y for q in pr), max(q.x for q in pr) - min(q.x for q in pr))
        if ext > 0.92:
            a = d
        else:
            b = d
    CAM.location = centro - f * b
    return centro, hi.z - lo.z, max(hi.x - lo.x, hi.y - lo.y)

config_render()
if MODO == "web":
    preparar_web()
os.makedirs(SALIDA, exist_ok=True)
print("MODO", MODO, "res", RES, "% samples", SAMPLES, DEVICE, "look", sc.view_settings.look, "flags", FLAGS,
      "base_brillo", BASE_BRILLO, "->", SALIDA)
for p in lista:
    col, cam_ref = PRODUCTOS[p]
    solo(col)
    bpy.context.view_layer.update()
    objs = [o for o in vl.objects if o.type == "MESH" and o.visible_get() and not o.hide_render
            and not o.name.startswith("WEB_") and o.name not in ("Sphere LUZ", "BAse_Blanco")]
    centro, alto, ancho = encuadrar(objs, bpy.data.objects[cam_ref])
    if MODO == "web":
        banderas(centro, alto, ancho, CAM)
        luz_frontal(centro, alto, objs, RENOMBRAR.get(p, p))
        CEL.inputs["Strength"].default_value = FUERZA_COLOR if any(k in p for k in DE_COLOR) else CELESTE_TRANS[1]
    nombre = RENOMBRAR.get(p, p)
    if nombre in TAPAS:
        tapa_color(objs, nombre)
    print(f"PRODUCTO {nombre}: col={col} ref={cam_ref} alto={alto*100:.1f} cm dist={(CAM.location-centro).length:.2f} m "
          f"mallas={[o.name for o in objs]}")
    sc.render.filepath = f"{SALIDA}/{nombre}.png"
    bpy.ops.render.render(write_still=True)
    print("OK", sc.render.filepath)
print("FIN")
