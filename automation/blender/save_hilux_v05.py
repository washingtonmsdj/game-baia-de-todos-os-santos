"""Encerra a revisão com batentes internos e inscrições conformadas sem clipping."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene;assert scene.name=='VIATURA | Rondesp Hilux marrom v05'
for o in scene.objects:
    if 'Batente B' in o.name or 'Soleira interna' in o.name:o.location.x=.790 if o.location.x>0 else -.790
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in scene.objects:
    if o.type!='MESH' or not any(c.name in ['RDP01 | CARROCERIA','RDP01 | PORTAS'] for c in o.users_collection):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(vs);vs.extend(ev.matrix_world@v.co for v in m.vertices);fs.extend(tuple(base+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
for o in scene.objects:
    if o.type!='MESH' or not o.get('boas_inscription_text'):continue
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    long=[e for e in bm.edges if e.calc_length()>.012]
    if long:bmesh.ops.subdivide_edges(bm,edges=long,cuts=5,use_grid_fill=True)
    bm.to_mesh(o.data);bm.free()
    for v in o.data.vertices:
        p=o.matrix_world@v.co;side=1 if p.x>0 else -1
        hit,normal,index,d=bvh.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),2)
        if hit is not None:v.co=o.matrix_world.inverted()@(hit+Vector((side*.002,0,0)))
    o.data.update();o['boas_decal_clearance_m']=.002;o['boas_decal_method']='malha subdividida e conformada à chapa avaliada'
bpy.context.view_layer.update()
scene.display.shading.studiolight_rotate_z=.55
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v05-frente-geometria.png');bpy.ops.render.render(write_still=True)
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v05.blend'
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
p=repo/'docs/reports/blender/rondesp_marrom_v05.json';r=json.loads(p.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),inscriptions='malhas adaptativas conformadas à carroceria; batentes e soleiras realmente internos',source_saved=True)
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
