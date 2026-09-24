# -*- coding: utf-8 -*-
"""Prueba de contraste de la etiqueta Eco (frame final). No guarda el .blend.
blender -b giro_botella_v008.blend -P _prueba_contraste.py
Salida: render_test/contraste_<variante>.png (recorte de la etiqueta)"""
import bpy

BASE = "E:/GRACIANI/WEB GRAZIANI/03 BLENDER GIRO BOTELLA"
sc = bpy.context.scene
sc.frame_set(119)
sc.cycles.samples = 24
sc.render.use_border = True
sc.render.use_crop_to_border = True
sc.render.border_min_x, sc.render.border_max_x = 0.20, 0.80
sc.render.border_min_y, sc.render.border_max_y = 0.48, 0.80

mat = bpy.data.materials["Etiqueta"]
nt = mat.node_tree
bsdf = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"][0]
def mapa(entrada):
    for l in nt.links:
        if l.to_node == bsdf and l.to_socket.name == entrada and l.from_node.bl_idname == "ShaderNodeMapRange":
            return l.from_node
m_rough, m_spec = mapa("Roughness"), mapa("Specular IOR Level")
# nodo de saturación para la Eco (entre su textura y la mezcla), neutro por defecto
t_ec = [n for n in nt.nodes if n.bl_idname == "ShaderNodeTexImage" and "eco_orig" in n.image.name][0]
mix_col = [l.to_node for l in nt.links if l.from_node == t_ec and l.from_socket.name == "Color"][0]
hsv = nt.nodes.new("ShaderNodeHueSaturation")
bc = nt.nodes.new("ShaderNodeBrightContrast")
nt.links.new(t_ec.outputs["Color"], hsv.inputs["Color"])
nt.links.new(hsv.outputs["Color"], bc.inputs["Color"])
nt.links.new(bc.outputs["Color"], mix_col.inputs["Color2"])
key = bpy.data.objects["Key"].data

def variante(nombre, ink_spec=0.10, ink_rough=0.55, exp=-0.2, look="AgX - Medium High Contrast", sat=1.0, contr=0.0, key_e=55):
    m_spec.inputs["To Min"].default_value = ink_spec
    m_rough.inputs["To Min"].default_value = ink_rough
    sc.view_settings.exposure = exp
    sc.view_settings.look = look
    hsv.inputs["Saturation"].default_value = sat
    bc.inputs["Contrast"].default_value = contr
    key.energy = key_e
    sc.render.filepath = f"{BASE}/render_test/contraste_{nombre}.png"
    bpy.ops.render.render(write_still=True)
    print("variante", nombre, "->", sc.render.filepath)

variante("1_actual")
variante("2_tinta_sin_brillo", ink_spec=0.0, ink_rough=0.45)
variante("3_menos_exposicion", ink_spec=0.0, ink_rough=0.45, exp=-0.5)
variante("4_saturacion", ink_spec=0.0, ink_rough=0.45, sat=1.35, contr=0.12)
variante("5_punchy", ink_spec=0.0, ink_rough=0.45, look="AgX - Punchy")
variante("6_key_suave", ink_spec=0.0, ink_rough=0.45, key_e=35, sat=1.35, contr=0.12)
