"""Persistência e CCD local do encontro B87, sem aprovar o elevador completo."""
import bpy,bmesh,hashlib,json,math,os,runpy,sys
from pathlib import Path
from mathutils import Matrix,Vector
import numpy as np

root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-finish-b87'
r=json.loads((out/'application.json').read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(root/r['file']).resolve() and scene.name==r['scene']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==r['file'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted()
checks=[]
for row in r['changes']+r['added_colliders']:
    obj=bpy.data.objects[row['object']];expected=row['after']['signature'] if 'after' in row else row['signature']
    assert sig(obj)==expected,obj.name
    bm=bmesh.new();bm.from_mesh(obj.data);deg=sum(f.calc_area()<1e-8 for f in bm.faces);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    assert not deg,obj.name
    if obj.name.startswith('SUPERIOR | parede lateral saguão'):assert not nonmanifold
    checks.append({'object':obj.name,'persisted':True,'degenerate':deg,'nonmanifold_edges':nonmanifold})
assert scene.objects['NAV | passarela superior']['boas_physical_enabled'] is False
assert scene.objects['NAV | passarela superior'].hide_get() and scene.objects['NAV | passarela superior'].hide_render
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
for file,digest in ((r['parent_file'],r['parent_sha256']),(r['file'],r['sha256'])):
    with (root/file).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest
profile=json.loads((root/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text(encoding='utf8'))
for row in r['added_colliders']:
    binding=[v for v in profile['collision_bindings'] if v['object']==row['object']];assert len(binding)==1 and binding[0]['source']==row['source']

def triangles(obj):
    obj.data.calc_loop_triangles();coordinates=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',coordinates)
    matrix=np.asarray(inv@wm(obj));pts=coordinates.reshape((-1,3))@matrix[:3,:3].T+matrix[:3,3]
    indices=np.empty(len(obj.data.loop_triangles)*3,dtype=np.int32);obj.data.loop_triangles.foreach_get('vertices',indices)
    return pts[indices.reshape((-1,3))]

sys.path.insert(0,str(root/'tools/world'))
from slice_geometry import capsule_distances
from character_support import capsule_support
floors=np.concatenate([triangles(scene.objects[n]) for n in ('SUPERIOR | piso saguão','LAC R30B | Passarela | piso paginado visual')])
parts=[];owners=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.constraints or obj.get('boas_role')=='SUPERSEDED_REFERENCE':continue
    cols=[c.name for c in obj.users_collection]
    if not any(c.startswith(('11 ELEVADOR','12 LACERDA','13 LACERDA','30 LACERDA','HERO | Lacerda')) for c in cols):continue
    if not obj.visible_get():continue
    matrix=inv@wm(obj);p=np.array([list(matrix@Vector(v)) for v in obj.bound_box]);low=p.min(axis=0);high=p.max(axis=0)
    if np.any(high<[-22,-2,69]) or np.any(low>[-17,2,73]):continue
    t=triangles(obj);parts.append(t);owners.extend([obj.name]*len(t))
tri=np.concatenate(parts);names=np.array(owners);lo=tri.min(axis=1);hi=tri.max(axis=1)
radius=.30;height=1.80;skin=.015;threshold=radius-skin

def ccd(a,b):
    ids=np.flatnonzero(np.all(hi>=np.minimum(a,b)-[.315,.315,.015],axis=1)&np.all(lo<=np.maximum(a,b)+[.315,.315,1.815],axis=1))
    if not len(ids):return {'clear':True,'samples':0}
    local=tri[ids];witness=None;count=0
    def interval(t0,t1,depth):
        nonlocal witness,count
        p=a+(b-a)*(t0+t1)/2;distance=capsule_distances(p,local,radius,height);count+=1
        k=int(distance.argmin());minimum=float(distance[k])
        if minimum<threshold:
            witness={'position':p.tolist(),'object':str(names[ids[k]]),'depth_beyond_skin':threshold-minimum,'classification':'SOLID_PENETRATION'};return False
        if minimum-threshold>np.linalg.norm(b-a)*(t1-t0)/2+1e-8:return True
        if depth>=12:
            witness={'position':p.tolist(),'object':str(names[ids[k]]),'classification':'NEEDS_REVIEW_CONVERGENCE'};return False
        return interval(t0,(t0+t1)/2,depth+1) and interval((t0+t1)/2,t1,depth+1)
    ok=interval(0,1,0);return {'clear':ok,'samples':count,'witness':witness}

routes=[]
for y in (-1.,0.,1.):
    poses=[];missing=[];first_block=None;checks_ccd=[]
    for x in np.linspace(-21.5,-17.5,81):
        z=capsule_support(float(x),y,floors,69.5,70.5,radius,skin)
        if z is None:missing.append([float(x),y]);continue
        p=np.array([x,y,z]);poses.append(p)
        ids=np.flatnonzero(np.all(hi>=p-[.315,.315,.015],axis=1)&np.all(lo<=p+[.315,.315,1.815],axis=1))
        if len(ids):
            dist=capsule_distances(p,tri[ids],radius,height);k=int(dist.argmin())
            if dist[k]<threshold and first_block is None:first_block={'position':p.tolist(),'object':str(names[ids[k]]),'depth_beyond_skin':float(threshold-dist[k])}
    for a,b in zip(poses,poses[1:]):
        result=ccd(a,b);checks_ccd.append(result)
        if not result['clear'] and first_block is None:first_block=result['witness']
    routes.append({'y':y,'samples':len(poses),'missing_support':missing,'first_block':first_block,'ccd_checks':len(checks_ccd),'ccd_clear':all(v['clear'] for v in checks_ccd),
                   'ccd_evaluations':sum(v['samples'] for v in checks_ccd),'maximum_base_delta':max((abs(b[2]-a[2]) for a,b in zip(poses,poses[1:])),default=None),
                   'status':'LOCAL_CLEAR' if not missing and first_block is None and all(v['clear'] for v in checks_ccd) else 'BLOCKED_OR_REVIEW'})
v={'revision':r['revision'],'pid':os.getpid(),'reopened':True,'mesh_checks':checks,'junction':routes,'shape':{'radius':radius,'height':height,'skin':skin,'maximum_step':.25},
   'scope':'Apoio esférico estático e CCD Lipschitz local de 4 m no encontro ponte/saguão; não é controller/poço/percurso inteiro.',
   'ssot_preserved':True,'parent_preserved':True,'collider_bindings_unique':True,'full_route_approved':False,'engine_verified':False,'production_ready':False}
(out/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
window=next(w for w in bpy.context.window_manager.windows if w.screen)
eye=M@Vector((-28,-38,88));target=M@Vector((-10,0,73));direction=target-eye
for area in window.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.region_3d.view_perspective='PERSP';space.region_3d.view_rotation=direction.to_track_quat('-Z','Y')
        space.region_3d.view_location=target;space.region_3d.view_distance=direction.length;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=False;area.tag_redraw()
with bpy.context.temp_override(window=window):runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b87-upper-finish.png'})
print(json.dumps({'revision':r['revision'],'reopened':True,'persisted':len(checks),'junction':[v['status'] for v in routes],'full_route_approved':False}))
