"""Controles e malha local do conjunto fotografado, sem mutações da cena."""
import bpy,json,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'artifacts/palacio-rio-branco';scene=bpy.context.scene
r=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'))
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix'];R=Matrix(r['tower_alignment']['rotation_world']);I=R.inverted()
visible=set()
def visit(layer,parent=True):
    c=layer.collection;ok=parent and not c.hide_render and not layer.exclude
    if ok:visible.add(c.name)
    for child in layer.children:visit(child,ok)
visit(bpy.context.view_layer.layer_collection)
rows=[]
for o in scene.objects:
    if (o.type not in ('MESH','CURVE','FONT') and not o.instance_collection) or o.hide_render or o.hide_get() or not any(c.name in visible for c in o.users_collection):continue
    if o.type=='MESH' and len(o.data.vertices)<10000:pts=[I@wm(o)@v.co for v in o.data.vertices]
    elif o.instance_collection:pts=[I@wm(o)@Vector((0,0,0))]
    else:pts=[I@wm(o)@Vector(p) for p in o.bound_box]
    if not pts:continue
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    if hi[0]<-220 or lo[0]>100 or hi[1]<-170 or lo[1]>230:continue
    rows.append({'name':o.name,'collections':[c.name for c in o.users_collection],'min':lo,'max':hi,'location':o.get('boas_location_id'),'materials':[m.name if m else None for m in getattr(o.data,'materials',[])]})
source=scene.objects[r['terrain_names'][0]];me=source.data;M=wm(source);a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);mat=np.array(M);world=a.reshape((-1,3))@mat[:3,:3].T+mat[:3,3];local=world@np.array(I)[:3,:3].T
me.calc_loop_triangles();idx=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',idx);idx=idx.reshape((-1,3));polygon=np.empty(len(me.loop_triangles),dtype=np.int32);me.loop_triangles.foreach_get('polygon_index',polygon);mi=np.empty(len(me.polygons),dtype=np.int32);me.polygons.foreach_get('material_index',mi);mi=mi[polygon]
bbmin=local[idx].min(axis=1);bbmax=local[idx].max(axis=1);mask=(bbmax[:,0]>-52)&(bbmin[:,0]<10)&(bbmax[:,1]>-35)&(bbmin[:,1]<42)
used,inv=np.unique(idx[mask],return_inverse=True)
np.savez_compressed(out/'support_mesh_r35.npz',vertices=local[used],triangles=inv.reshape((-1,3)),materials=mi[mask],original_ids=used)
bvh=BVHTree.FromPolygons([Vector(v) for v in world[used]],inv.reshape((-1,3)).tolist(),all_triangles=True);mats=mi[mask];samples=[]
for y in (-15,-10,-5,0,4.25,8,13,18,25):
    row=[]
    for x in (-40,-35,-30,-27,-25,-22,-20,-16,-12,-8,-4,0):
        hit=bvh.ray_cast(R@Vector((x,y,130)),Vector((0,0,-1)),220)
        row.append([x,round(hit[0].z,3) if hit[0] else None,int(mats[hit[2]]) if hit[0] else None])
    samples.append({'y':y,'xz_material':row})
(out/'context_r35.json').write_text(json.dumps({'file':bpy.data.filepath,'visible_collections':sorted(visible),'objects':rows,'materials':[m.name for m in me.materials],'samples':samples},ensure_ascii=False,indent=2),encoding='utf8')
