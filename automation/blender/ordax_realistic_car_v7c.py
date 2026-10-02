import base64, bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

SOURCE_URL='https://cdn.3dassets.dev/assets/18684/v1/model.glb'
SOURCE_PAGE='https://3dassets.dev/assets/transport-collection-hd-executive-sedan-cfa7dfcf'
TRANSFER_REL='automation/blender/assets/ordax_v7c_f62fbc1c83af4c1180440fd659d5142673625df3'
EXPECTED_SHA='4e110f8fc8bb4ef270d08b33524349020b727b129ca94858d5030e7a75bdebaa'
EXPECTED_SIZE=383416

blend_dir=Path(bpy.path.abspath('//')).resolve()
project=next((p for p in [blend_dir,*blend_dir.parents] if (p/'.git').exists()),None)
if project is None: raise RuntimeError(f'project root not found from {blend_dir}')
glb=project/'automation'/'blender'/'assets'/'executive_sedan_cc0.glb'
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
glb=asset_dir/'executive_sedan_cc0.glb'; tmp=glb.with_suffix('.glb.part'); tmp.write_bytes(raw); tmp.replace(glb)

before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb),import_pack_images=True)
imported=[o for o in bpy.data.objects if o not in before]
meshes=[o for o in imported if o.type=='MESH']
if not meshes:
    for o in imported: bpy.data.objects.remove(o,do_unlink=True)
    raise RuntimeError('GLB imported without meshes')

for o in list(before):
    if o.name in bpy.data.objects: bpy.data.objects.remove(o,do_unlink=True)

corners=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
minx,maxx=min(v.x for v in corners),max(v.x for v in corners)
miny,maxy=min(v.y for v in corners),max(v.y for v in corners)
minz=min(v.z for v in corners)
offset=Vector((-(minx+maxx)/2,-(miny+maxy)/2,-minz))
for o in imported:
    if o.parent is None: o.location+=offset

def pbsdf(m):
    if not m.use_nodes: m.use_nodes=True
    return m.node_tree.nodes.get('Principled BSDF')

paint=[]; glass=[]; rubber=[]
for m in bpy.data.materials:
    p=pbsdf(m)
    if not p: continue
    n=m.name.lower(); base=p.inputs.get('Base Color'); metal=p.inputs.get('Metallic'); rough=p.inputs.get('Roughness'); trans=p.inputs.get('Transmission Weight')
    if any(k in n for k in ('glass','window','windscreen','windshield')) or (trans and float(trans.default_value)>.15):
        glass.append(m)
        if base: base.default_value=(.010,.024,.040,1)
        if rough: rough.default_value=.08
        if trans: trans.default_value=.50
    elif any(k in n for k in ('rubber','tire','tyre')):
        rubber.append(m)
        if base: base.default_value=(.004,.005,.006,1)
        if rough: rough.default_value=.76
        if metal: metal.default_value=0.0
    elif any(k in n for k in ('paint','body','exterior','shell','panel')):
        paint.append(m)
        if base: base.default_value=(.015,.022,.035,1)
        if metal: metal.default_value=.80
        if rough: rough.default_value=.17

if not paint:
    body_words=('body','door','hood','bonnet','roof','fender','bumper','trunk','boot','quarter')
    for o in meshes:
        if not any(k in o.name.lower() for k in body_words): continue
        for slot in o.material_slots:
            m=slot.material
            if not m or m in glass or m in rubber: continue
            p=pbsdf(m)
            if p:
                p.inputs['Base Color'].default_value=(.015,.022,.035,1)
                p.inputs['Metallic'].default_value=.80
                p.inputs['Roughness'].default_value=.17
                if m not in paint: paint.append(m)

red=bpy.data.materials.get('ORDAX_V7C_Caliper') or bpy.data.materials.new('ORDAX_V7C_Caliper'); red.use_nodes=True
rp=red.node_tree.nodes.get('Principled BSDF'); rp.inputs['Base Color'].default_value=(.45,.008,.004,1); rp.inputs['Metallic'].default_value=.62; rp.inputs['Roughness'].default_value=.22
for o in meshes:
    if 'caliper' in o.name.lower():
        if len(o.data.materials): o.data.materials[0]=red
        else: o.data.materials.append(red)
    if not any(k in o.name.lower() for k in ('wheel','rim','tire','tyre','disc','caliper')):
        for poly in o.data.polygons: poly.use_smooth=True

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100; scene.world.color=(.025,.028,.035)
scene['ordax_realistic_car_revision']='v7c-cc0-executive-sedan'; scene['ordax_asset_source']=SOURCE_URL; scene['ordax_asset_page']=SOURCE_PAGE; scene['ordax_asset_license']='CC0 1.0 Universal'; scene['ordax_asset_sha256']=EXPECTED_SHA
print(json.dumps({'ok':True,'revision':'v7c','objects':len(imported),'meshes':len(meshes),'paint':[m.name for m in paint],'glass':[m.name for m in glass],'rubber':[m.name for m in rubber]}))
