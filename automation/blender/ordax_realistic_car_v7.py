import bpy, json, math, os, urllib.request
from pathlib import Path
from mathutils import Vector

SOURCE_URL='https://cdn.3dassets.dev/assets/18684/v1/model.glb'
SOURCE_PAGE='https://3dassets.dev/assets/transport-collection-hd-executive-sedan-cfa7dfcf'
root=Path(bpy.path.abspath('//')).resolve()
if not str(root):
    root=Path.cwd().resolve()
asset_dir=root/'automation'/'blender'/'assets'
asset_dir.mkdir(parents=True,exist_ok=True)
glb=asset_dir/'executive_sedan_cc0.glb'
# Download fully before touching the existing V6 scene.
if not glb.exists() or glb.stat().st_size < 100000:
    tmp=glb.with_suffix('.download')
    with urllib.request.urlopen(SOURCE_URL,timeout=60) as r, tmp.open('wb') as f:
        while True:
            chunk=r.read(1024*256)
            if not chunk: break
            f.write(chunk)
    if tmp.stat().st_size < 100000:
        raise RuntimeError(f'asset download unexpectedly small: {tmp.stat().st_size}')
    tmp.replace(glb)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(glb),import_pack_images=True)
imported=[o for o in bpy.data.objects if o not in before]
if not imported:
    raise RuntimeError('GLB import produced no Blender objects')

# Normalize placement: centre footprint at world origin and put tyres at Z=0.
corners=[]
for o in imported:
    if o.type=='MESH':
        corners.extend(o.matrix_world @ Vector(c) for c in o.bound_box)
if not corners:
    raise RuntimeError('Imported sedan contains no mesh bounds')
minx=min(v.x for v in corners); maxx=max(v.x for v in corners)
miny=min(v.y for v in corners); maxy=max(v.y for v in corners)
minz=min(v.z for v in corners)
offset=Vector((-(minx+maxx)/2,-(miny+maxy)/2,-minz))
roots=[o for o in imported if o.parent is None]
for o in roots: o.location += offset

# Materials tuned toward the dark premium reference while preserving source detail.
def principled(m):
    if not m.use_nodes: m.use_nodes=True
    return m.node_tree.nodes.get('Principled BSDF')
paint_candidates=[]; glass_candidates=[]; rubber_candidates=[]
for m in bpy.data.materials:
    p=principled(m)
    if not p: continue
    n=m.name.lower()
    base=p.inputs.get('Base Color')
    metallic=p.inputs.get('Metallic')
    rough=p.inputs.get('Roughness')
    trans=p.inputs.get('Transmission Weight')
    alpha=p.inputs.get('Alpha')
    if any(k in n for k in ('glass','window','windscreen','windshield')) or (trans and float(trans.default_value)>.15):
        glass_candidates.append(m)
        if base: base.default_value=(0.012,0.026,0.045,1)
        if rough: rough.default_value=.08
        if trans: trans.default_value=.62
        p.inputs['IOR'].default_value=1.45
    elif any(k in n for k in ('rubber','tyre','tire')):
        rubber_candidates.append(m)
        if base: base.default_value=(.006,.007,.009,1)
        if rough: rough.default_value=.73
        if metallic: metallic.default_value=0.0
    elif any(k in n for k in ('paint','body','carpaint','exterior','panel')):
        paint_candidates.append(m)
        if base: base.default_value=(.018,.026,.040,1)
        if metallic: metallic.default_value=.78
        if rough: rough.default_value=.17

# Fallback: identify large exterior meshes by object name if material names are generic.
if not paint_candidates:
    body_words=('body','shell','door','bonnet','hood','boot','trunk','bumper','fender','wing','roof')
    for o in imported:
        if o.type!='MESH' or not any(k in o.name.lower() for k in body_words): continue
        for slot in o.material_slots:
            if slot.material and slot.material not in glass_candidates and slot.material not in rubber_candidates:
                p=principled(slot.material)
                if p:
                    p.inputs['Base Color'].default_value=(.018,.026,.040,1)
                    p.inputs['Metallic'].default_value=.78
                    p.inputs['Roughness'].default_value=.17
                    paint_candidates.append(slot.material)

# Add subtle red caliper material to explicitly identifiable accent/caliper nodes.
red=bpy.data.materials.get('ORDAX_V7_RedCaliper') or bpy.data.materials.new('ORDAX_V7_RedCaliper'); red.use_nodes=True
rp=red.node_tree.nodes.get('Principled BSDF'); rp.inputs['Base Color'].default_value=(.42,.008,.004,1); rp.inputs['Metallic'].default_value=.62; rp.inputs['Roughness'].default_value=.22
for o in imported:
    if o.type=='MESH' and any(k in o.name.lower() for k in ('caliper','accent')):
        if len(o.data.materials): o.data.materials[0]=red
        else: o.data.materials.append(red)

# Smooth faceted body panels, but keep wheel/mechanical hard edges intact.
for o in imported:
    if o.type!='MESH': continue
    lname=o.name.lower()
    if not any(k in lname for k in ('wheel','tyre','tire','disc','caliper','accent')):
        for face in o.data.polygons: face.use_smooth=True

sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=100
sc.world.color=(.025,.028,.035)
sc['ordax_realistic_car_revision']='v7-cc0-executive-sedan'
sc['ordax_asset_source']=SOURCE_URL
sc['ordax_asset_page']=SOURCE_PAGE
sc['ordax_asset_license']='CC0 1.0 Universal'
sc['ordax_asset_dimensions_m']='2.27 x 1.57 x 5.20'
print(json.dumps({'ok':True,'revision':'v7','objects':len(imported),'materials':len(bpy.data.materials),'paint_candidates':[m.name for m in paint_candidates],'glass_candidates':[m.name for m in glass_candidates]}))