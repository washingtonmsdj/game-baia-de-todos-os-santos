import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector
scene=bpy.data.scenes["ONIBUS | Integra 10011"]
bpy.context.window.scene=scene
root=bpy.data.objects["BUS_ROOT"]
cols={n:bpy.data.collections["BUS | "+n] for n in ["EXTERIOR","APRESENTACAO"]}
# Costura dos painéis: eliminar as arestas coincidentes entre segmentos.
for o in scene.objects:
    if o.type=='MESH' and o.name.startswith("BUS | Lateral"):
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Vidro fumê opaco no preview: evita ruído de transmissão e mantém material editável.
for m in bpy.data.materials:
    if m.name.startswith("BUS | Vidro"):
        p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs["Transmission Weight"].default_value=0
        p.inputs["Metallic"].default_value=.28
        p.inputs["Roughness"].default_value=.19
        p.inputs["Base Color"].default_value=(.035,.070,.088,1)
        m["nota"]="Vidro fumê de apresentação. Interior modelado separadamente; transparência para runtime a definir."
# O forro escuro frontal não pode atravessar o vidro.
for o in scene.objects:
    if o.name.startswith("BUS | Para-brisa bipartido"):
        for m in o.modifiers:
            if m.type=='SOLIDIFY':m.thickness=.006
        for v in o.data.vertices:v.co.y-=.028
    if o.name.startswith("BUS | Faixa superior Salvador"):
        o.location.x=math.copysign(1.278,o.location.x)
# Marca sobre campo branco arredondado da pintura.
white=bpy.data.materials["BUS | Branco perolado"];yellow=bpy.data.materials["BUS | Amarelo carroceria"]
for s in [-1,1]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(s*1.283,1.59,1.565))
    o=bpy.context.object;o.name="BUS | Campo branco marca"
    for c in list(o.users_collection):c.objects.unlink(o)
    cols["EXTERIOR"].objects.link(o);o.parent=root;o.dimensions=(.016,1.41,.55)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(white)
    mod=o.modifiers.new("Canto suave",'BEVEL');mod.width=.05;mod.segments=4
for o in scene.objects:
    if o.name.startswith("BUS | Marca lateral"):
        o.location.x=math.copysign(1.297,o.location.x);o.location.y=1.59;o.location.z=1.63
        o.data.size=.34;o.data.materials.clear();o.data.materials.append(yellow)
    if o.name.startswith("BUS | Cidade lateral"):
        o.location.x=math.copysign(1.299,o.location.x);o.location.y=1.59;o.location.z=1.43
# Enquadramento mais próximo ao nível de observação do veículo.
cam=scene.camera;cam.location=(15,-19,6.8);cam.rotation_euler=(Vector((0,0,1.50))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=14.6
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=root
root.select_set(True)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.shading.type='MATERIAL'
        a.spaces.active.overlay.show_overlays=False
        a.spaces.active.region_3d.view_perspective='CAMERA'
scene["modelagem"]="Exterior detalhado; interior em esboço; quadro 50 portas abertas; 75 elevador baixo. Sem testes/builds. Integração runtime pendente."
out=Path(bpy.data.filepath).parent/"assets"/"onibus_integra_10011_v01.blend"
bpy.data.libraries.write(str(out),{scene},fake_user=True,compress=True)
print("Ônibus salvo: "+str(out))
