"""Confere reabertura, escopo, malha e passagem no encontro corrigido B83."""
import bpy,bmesh,json,runpy,math,hashlib,os,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-consolidation-b83'
r=json.loads((OUT/'application.json').read_text(encoding='utf8'));assert Path(bpy.data.filepath).resolve()==(ROOT/r['file']).resolve()
scene=bpy.context.scene;assert scene.name=='SALVADOR | ESBOCO OFICIAL'
proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==r['file'] and proof['load_post_completed']
helper=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=helper['signature'];wm=helper['world_matrix']
baseline=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/protected_original_components.json').read_text(encoding='utf8'));changes={v['object']:v['after'] for v in r['changed_meshes']};unexpected=[]
for name,old in baseline.items():
    ob=scene.objects.get(name)
    if ob is None:unexpected.append({'name':name,'reason':'missing'});continue
    try:actual=sig(ob)
    except RuntimeError:actual={'type':ob.type,'basis':[list(row) for row in ob.matrix_basis],'data':ob.data.name if ob.data else None}
    if actual!=changes.get(name,old):unexpected.append({'name':name,'reason':'component_difference'})
assert not unexpected,str(unexpected[:10])
M=Matrix(r['migration_source'] and json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inverse=M.inverted()
walls=['SUPERIOR | posterior lateral','SUPERIOR | posterior lateral.001'];probes=[];checks=[];triangles=[]
for i,name in enumerate(walls):
    ob=scene.objects[name];world=wm(ob);verts=[world@v.co for v in ob.data.vertices];local=[inverse@p for p in verts];edge=max(p.y for p in local) if i==0 else min(p.y for p in local)
    bm=bmesh.new();bm.from_mesh(ob.data);check={'object':name,'gap':abs(edge-(-3 if i==0 else 3)),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-8 for f in bm.faces)};bm.free()
    collider=scene.objects['B83 | COLLISION | '+name];check['collider_error']=max((wm(collider)@a.co-b).length for a,b in zip(collider.data.vertices,verts));checks.append(check)
    ob.data.calc_loop_triangles();faces=[tuple(t.vertices) for t in ob.data.loop_triangles];tree=BVHTree.FromPolygons(verts,faces,all_triangles=True)
    for j in range(1,9):
        y=(-4.7+(1.7*j/9)) if i==0 else (3+1.7*j/9)
        for z in (70.4,71.8,73.3):probes.append(tree.ray_cast(M@Vector((-4,y,z)),M.to_3x3()@Vector((-1,0,0)),2)[0] is not None)
for name in changes:
    ob=scene.objects[name];ob.data.calc_loop_triangles();verts=[list(wm(ob)@v.co) for v in ob.data.vertices];triangles.extend([[verts[k] for k in t.vertices] for t in ob.data.loop_triangles])
sys.path.insert(0,str(ROOT/'tools/world'));import numpy as np
from slice_geometry import capsule_distances
qa=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/walkability_candidate_b77.json').read_text(encoding='utf8'));blockers=[];samples=0;tri=np.array(triangles)
for a,b in zip(qa['routes']['upper']['points'],qa['routes']['upper']['points'][1:]):
    for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.05)+1)):
        p=np.array(a)+(np.array(b)-a)*t;d=float(capsule_distances(p,tri,.30,1.80).min());samples+=1
        if d<.285:blockers.append({'foot':p.tolist(),'distance':d})
assert all(probes) and all(c['gap']<1e-5 and not c['nonmanifold'] and not c['degenerate'] and c['collider_error']<1e-5 for c in checks)
assert not blockers,str(blockers[:3])
assert len(bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects)==70
assert hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
report={'passed':True,'reopened':True,'pid':os.getpid(),'revision':'R30B.83','historical_components_checked':len(baseline),'unexpected_changes':unexpected,'authorized_mesh_changes':list(changes),'checks':checks,'closed_probes':sum(probes),'total_probes':len(probes),'capsule_samples':samples,'capsule_blockers':blockers,'capsule_scope':'Upper route against seven changed meshes only; full shaft and route remain independent blocked gates','proxy_objects_preserved':70,'ssot_preserved':True,'production_ready':False}
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b83-reopened.png'})
print(json.dumps(report,ensure_ascii=False))
