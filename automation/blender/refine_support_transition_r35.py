"""Recompõe a transição lateral do apoio usando terreno B34 e limites do saguão.

A referência B34 é somente lida na sessão. Nenhuma estrutura é deslocada.
"""
import bpy,bmesh,json,hashlib,runpy
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json'
r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
assert 'support_lateral_transition' not in r['terrain_refinement']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
R=Matrix(r['tower_alignment']['rotation_world']);RI=R.inverted();rear=r['tower_alignment']['sea_face_x_from_upper_wall_m']
floor=scene.objects['SUPERIOR | piso saguão'];fp=[RI@wm(floor)@v.co for v in floor.data.vertices]
body=scene.objects[r['tower_alignment']['objects'][0]];bp=[RI@wm(body)@v.co for v in body.data.vertices]
y0,y1=min(p.y for p in fp),max(p.y for p in fp);b0,b1=min(p.y for p in bp),max(p.y for p in bp)
anchors=r['terrain_refinement']['support_profile_anchors']
def az(y,key):
    if y<=anchors[0]['y']:return anchors[0][key]
    if y>=anchors[-1]['y']:return anchors[-1][key]
    for a,b in zip(anchors,anchors[1:]):
        if a['y']<=y<=b['y']:return a[key]+(b[key]-a[key])*(y-a['y'])/(b['y']-a['y'])
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def weight(y):
    if y<b0:return ease((y-y0)/(b0-y0))
    if y>b1:return ease((y1-y)/(y1-b1))
    return 1
def profile(x,y):
    if x<=-22:return az(y,'z30')+(az(y,'z22')-az(y,'z30'))*(x+30)/8
    return az(y,'z22')+(az(y,'z20')-az(y,'z22'))*min(1,(x+22)/(rear+22))
def coords(o):
    a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a)
    m=np.array(wm(o));return a.reshape((-1,3))@m[:3,:3].T+m[:3,3]
def crop_bvh(o):
    world=coords(o);local=world@np.array(RI)[:3,:3].T
    me=o.data;me.calc_loop_triangles();idx=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',idx);idx=idx.reshape((-1,3))
    c=local[idx].mean(axis=1);mask=(c[:,0]>-34)&(c[:,0]<rear+4)&(c[:,1]>y0-4)&(c[:,1]<y1+4)
    selected=np.flatnonzero(mask);tris=idx[selected];used,inv=np.unique(tris,return_inverse=True)
    return BVHTree.FromPolygons([Vector(v) for v in world[used]],inv.reshape((-1,3)).tolist(),all_triangles=True),[me.polygons[me.loop_triangles[int(i)].polygon_index].material_index for i in selected]
source=scene.objects[r['terrain_names'][0]]
allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
def road_points(me):
    ids={v for p in me.polygons if p.material_index not in allowed for v in p.vertices}
    return {tuple(round(c,5) for c in me.vertices[i].co) for i in ids}
roads=road_points(source.data);loaded=[];rows=[]
parent=root/r['source_before']['file']
with parent.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['source_before']['sha256']
try:
    with bpy.data.libraries.load(str(parent),link=False) as (available,data):
        assert all(n in available.objects for n in r['terrain_names'])
        data.objects=list(r['terrain_names'])
    loaded=list(data.objects);original_by_name=dict(zip(r['terrain_names'],loaded))
    original_source_bvh,original_materials=crop_bvh(original_by_name[source.name])
    for name in r['terrain_names']:
        o=scene.objects[name];before=sig(o);original_bvh,_=crop_bvh(original_by_name[name]);mesh=o.data
        M=wm(o);I=M.inverted();world=coords(o);local=world@np.array(RI)[:3,:3].T
        nearby=(local[:,0]>-32)&(local[:,0]<rear+2)&(local[:,1]>y0-2)&(local[:,1]<y1+2)
        loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops)
        starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
        face_ids=np.flatnonzero(np.logical_or.reduceat(nearby[loops],starts))
        bm=bmesh.new();bm.from_mesh(mesh);bm.faces.ensure_lookup_table();region={bm.faces[int(i)] for i in face_ids};cache={}
        def permitted(f):
            if o==source:return f.material_index in allowed
            if f not in cache:
                p=M@f.calc_center_median();hit=original_source_bvh.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),250)
                cache[f]=hit[0] is not None and original_materials[hit[2]] in allowed
            return cache[f]
        for axis,value in ((R@Vector((1,0,0)),-30),(R@Vector((1,0,0)),rear),(R@Vector((1,0,0)),rear+.25),(R@Vector((0,1,0)),y0),(R@Vector((0,1,0)),b0),(R@Vector((0,1,0)),b1),(R@Vector((0,1,0)),y1)):
            faces=[f for f in region if f.is_valid and permitted(f)];geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(axis*value),plane_no=M.to_3x3().transposed()@axis,clear_inner=False,clear_outer=False)
            for g in result['geom_cut']:
                if hasattr(g,'link_faces'):region.update(g.link_faces)
        locked={v for f in bm.faces if o==source and f.material_index not in allowed for v in f.verts}
        locked.update(v for f in region if f.is_valid and not permitted(f) for v in f.verts)
        count=0;max_delta=0
        for v in {v for f in region if f.is_valid for v in f.verts}:
            if v in locked:continue
            w=M@v.co;p=RI@w;x,y=p.x,p.y
            if not(-30-.0001<=x<=rear+.2501 and y0-.0001<=y<=y1+.0001):continue
            hit=original_bvh.ray_cast(Vector((w.x,w.y,150)),Vector((0,0,-1)),250)
            if hit[0] is None:continue
            wt=weight(y)*(1-ease((x-rear)/.25) if x>rear else 1)
            z=hit[0].z+(profile(x,y)-hit[0].z)*wt
            if abs(z-w.z)<.00001:continue
            max_delta=max(max_delta,abs(z-w.z));w.z=z;v.co=I@w;count+=1
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
        rows.append({'object':name,'before':before,'after':sig(o),'changed_vertices':count,'max_abs_z_delta_m':max_delta})
    assert not roads-road_points(source.data),'Superfície de circulação deslocada'
    assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
finally:
    for o in loaded:
        mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if not mesh.users:bpy.data.meshes.remove(mesh)
r['terrain_refinement']['support_lateral_transition']={'classification':'ADAPT_LOCAL','original_terrain':r['source_before'],'limits_y_from_upper_floor_m':[y0,y1],'full_weight_y_from_support_m':[b0,b1],'method':'Recomposição a partir de B34; mesma interpolação longitudinal, peso suave até as bordas transversais do saguão. Corrige a parede de terreno lateral sem mover estrutura ou pista.','geometry':rows}
for row in rows:
    next(g for g in r['terrain_refinement']['geometry'] if g['object']==row['object'])['after']=row['after']
r['terrain_refinement']['source_road_positions_preserved']=len(roads)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_after':r['source_after'],'changed':[(g['object'],g['changed_vertices']) for g in rows],'road_positions_preserved':len(roads)},ensure_ascii=False))
