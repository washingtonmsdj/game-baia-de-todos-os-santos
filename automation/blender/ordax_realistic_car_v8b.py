import base64, bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

SOURCE_URL='https://cdn.3dassets.dev/assets/32490/v1/model.glb'
SOURCE_PAGE='https://3dassets.dev/assets/car-park-and-road-vehicle-fleet-saloon-ad831b1f'
TRANSFER_REL='automation/blender/assets/ordax_v8b_63a503f9f003a2aa272cb83b084f6ce48b509a6b'
EXPECTED_SHA='84a41ed86865353cf1e97dca9c240f05c4c4737e77886f893381b8b6be02d488'
EXPECTED_SIZE=955288

blend_dir=Path(bpy.path.abspath('//')).resolve()
project=next((p for p in [blend_dir,*blend_dir.parents] if (p/'.git').exists()),None)
if project is None: raise RuntimeError(f'project root not found from {blend_dir}')
glb=project/'automation'/'blender'/'assets'/'premium_saloon_cc0.glb'
if glb.is_file():
    raw=glb.read_bytes()
else:
    parts=sorted((project/TRANSFER_REL).glob('part*.txt'))
    if not parts: raise RuntimeError('Fonte GLB e transferência local ausentes')
    raw=base64.b64decode(''.join(p.read_text(encoding='utf-8') for p in parts),validate=True)
actual=hashlib.sha256(raw).hexdigest()
if len(raw)!=EXPECTED_SIZE or actual!=EXPECTED_SHA or raw[:4]!=b'glTF':
    raise RuntimeError(f'GLB validation failed bytes={len(raw)} sha={actual} magic={raw[:4]!r}')

asset_dir=project/'automation'/'blender'/'assets'; asset_dir.mkdir(parents=True,exist_ok=True)
glb=asset_dir/'premium_saloon_cc0.glb'; tmp=glb.with_suffix('.glb.part'); tmp.write_bytes(raw); tmp.replace(glb)

before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb),import_pack_images=True)
imported=[o for o in bpy.data.objects if o not in before]
meshes=[o for o in imported if o.type=='MESH']
if not meshes:
    for o in imported: bpy.data.objects.remove(o,do_unlink=True)
    raise RuntimeError('high-detail saloon imported without meshes')

for o in list(before):
    if o.name in bpy.data.objects: bpy.data.objects.remove(o,do_unlink=True)

corners=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
minx,maxx=min(v.x for v in corners),max(v.x for v in corners)
miny,maxy=min(v.y for v in corners),max(v.y for v in corners)
minz,maxz=min(v.z for v in corners),max(v.z for v in corners)
offset=Vector((-(minx+maxx)/2,-(miny+maxy)/2,-minz))
for o in imported:
    if o.parent is None: o.location+=offset

def pbsdf(m):
    if not m.use_nodes: m.use_nodes=True
    return m.node_tree.nodes.get('Principled BSDF')

paint=[]; glass=[]; rubber=[]; metal=[]
for m in bpy.data.materials:
    p=pbsdf(m)
    if not p: continue
    n=m.name.lower(); base=p.inputs.get('Base Color'); metallic=p.inputs.get('Metallic'); rough=p.inputs.get('Roughness'); trans=p.inputs.get('Transmission Weight')
    if any(k in n for k in ('glass','window','windscreen','windshield')) or (trans and float(trans.default_value)>.18):
        glass.append(m)
        if base: base.default_value=(.008,.020,.036,1)
        if rough: rough.default_value=.07
        if trans: trans.default_value=.58
    elif any(k in n for k in ('rubber','tire','tyre')):
        rubber.append(m)
        if base: base.default_value=(.003,.004,.005,1)
        if rough: rough.default_value=.74
        if metallic: metallic.default_value=0.0
    elif any(k in n for k in ('chrome','metal','rim','alloy','wheel')):
        metal.append(m)
        if metallic: metallic.default_value=.90
        if rough: rough.default_value=.13
    elif any(k in n for k in ('paint','body','exterior','shell','panel','car')):
        paint.append(m)
        if base: base.default_value=(.012,.020,.032,1)
        if metallic: metallic.default_value=.83
        if rough: rough.default_value=.16

if not paint:
    body_words=('body','door','hood','bonnet','roof','fender','bumper','trunk','boot','quarter','wing')
    for o in meshes:
        if not any(k in o.name.lower() for k in body_words): continue
        for slot in o.material_slots:
            m=slot.material
            if not m or m in glass or m in rubber or m in metal: continue
            p=pbsdf(m)
            if p:
                p.inputs['Base Color'].default_value=(.012,.020,.032,1)
                p.inputs['Metallic'].default_value=.83
                p.inputs['Roughness'].default_value=.16
                if m not in paint: paint.append(m)

red=bpy.data.materials.get('ORDAX_V8B_Caliper') or bpy.data.materials.new('ORDAX_V8B_Caliper'); red.use_nodes=True
rp=red.node_tree.nodes.get('Principled BSDF'); rp.inputs['Base Color'].default_value=(.50,.006,.003,1); rp.inputs['Metallic'].default_value=.65; rp.inputs['Roughness'].default_value=.20
for o in meshes:
    lname=o.name.lower()
    if 'caliper' in lname:
        if len(o.data.materials): o.data.materials[0]=red
        else: o.data.materials.append(red)
    if not any(k in lname for k in ('wheel','rim','tire','tyre','disc','caliper','grille')):
        for poly in o.data.polygons: poly.use_smooth=True

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100; scene.world.color=(.018,.021,.027)
scene['ordax_realistic_car_revision']='v8b-high-detail-cc0-saloon'; scene['ordax_asset_source']=SOURCE_URL; scene['ordax_asset_page']=SOURCE_PAGE; scene['ordax_asset_license']='CC0 1.0 Universal'; scene['ordax_asset_sha256']=EXPECTED_SHA
print(json.dumps({'ok':True,'revision':'v8b','objects':len(imported),'meshes':len(meshes),'bounds':[maxx-minx,maxy-miny,maxz-minz],'paint':[m.name for m in paint],'glass':[m.name for m in glass],'rubber':[m.name for m in rubber],'metal':[m.name for m in metal]}))
