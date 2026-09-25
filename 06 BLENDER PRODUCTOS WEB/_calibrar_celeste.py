# Qué valor lineal hace falta para que, con AgX + look, una emisión salga #f1f9fd en el PNG.
import bpy, sys
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.mesh.primitive_plane_add(size=2); pl = bpy.context.active_object
m = bpy.data.materials.new("E"); m.use_nodes = True; nt = m.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
em = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(em.outputs[0], out.inputs[0]); pl.data.materials.append(m)
cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"; cd.ortho_scale = 1.0
cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); cam.location = (0, 0, 2); sc.camera = cam
sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.use_denoising = False
sc.render.resolution_x = sc.render.resolution_y = 8
sc.view_settings.view_transform = "AgX"
OBJ = (241, 249, 253)
sc.view_settings.look = "AgX - Medium High Contrast"
mejor = None
for a in (0.45, 0.55, 0.65, 0.75):
    for b in (0.80, 0.88, 0.95):
        for k in (4.0, 5.0, 6.0, 7.5):
            em.inputs["Color"].default_value = (a, b, 1.0, 1)
            em.inputs["Strength"].default_value = k
            p = "C:/Users/Urano/AppData/Local/Temp/claude/E--GRACIANI-WEB-GRAZIANI/eed07efa-d6f6-48b9-a5ac-6238911fd8a3/scratchpad/cal_x.png"
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            im = bpy.data.images.load(p); px = [round(v * 255) for v in im.pixels[:3]]; bpy.data.images.remove(im)
            err = sum((x - y) ** 2 for x, y in zip(px, OBJ)) ** 0.5
            if mejor is None or err < mejor[0]:
                mejor = (err, a, b, k, px)
            print(f"CAL a={a} b={b} k={k} -> {px} err {err:.1f}")
print("MEJOR", mejor)
