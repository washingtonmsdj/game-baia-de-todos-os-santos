"""Exporta o carro existente por append na mesma janela, preservando a cidade."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
source=root/'automation/blender/ordax_car_realistic_v14_reference_cleanup.blend'
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=list(src.objects)
added=set(bpy.data.objects)-before
coll=bpy.data.collections.new('TEMP | EXPORT CARRO');bpy.context.scene.collection.children.link(coll)
objects=[]
try:
    for o in added:
        coll.objects.link(o)
        if o.type in {'MESH','CURVE'} and not o.hide_render and not o.hide_viewport and (o.name.startswith('ORDAX') or o.name.startswith('saloon') or 'wheel' in o.name.lower()):
            objects.append(o)
    bpy.context.view_layer.update()
    corners=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in corners) for i in range(3)));hi=Vector(tuple(max(v[i] for v in corners) for i in range(3)));size=hi-lo
    # Source front is -Y, exported glTF front becomes +Z. Set origin at tire contact.
    offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        world=o.matrix_world.copy();o.parent=None;o.matrix_world=world; o.location-=offset;o.select_set(True)
    out=root/'prototypes/threejs-water-lab/public/assets/vehicles/car-v14.glb';out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
    meta={'asset_id':'vehicle-existing-saloon-v14','source':source.relative_to(root).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions_m':[round(size.x,5),round(size.z,5),round(size.y,5)],'dimensions_classification':'medidas da malha existente, não do fabricante','front_runtime':'+Z','objects':len(objects)}
    out.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(meta))
finally:
    for o in added:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(coll)
