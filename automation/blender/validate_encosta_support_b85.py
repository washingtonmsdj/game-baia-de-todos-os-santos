"""QA da revisão localizada B85, após reabertura na mesma janela."""
import bpy,json,runpy,bmesh,hashlib,math,sys,os
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-proportions-b85';r=json.loads((OUT/'application.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/r['file']).resolve()
assert bpy.context.scene.name=='SALVADOR | ESBOCO OFICIAL'
proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==r['file'] and proof['load_post_completed']
h=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix'];scene=bpy.context.scene;checks=[];tris=[]
for row in r['changed_meshes']:
    ob=scene.objects[row['object']];assert sig(ob)==row['after']['signature']
    bm=bmesh.new();bm.from_mesh(ob.data);deg=sum(f.calc_area()<1e-8 for f in bm.faces);bm.free();assert not deg
    checks.append({'object':ob.name,'persisted':True,'degenerate':deg})
    ob.data.calc_loop_triangles();pts=[list(wm(ob)@v.co) for v in ob.data.vertices];tris.extend([[pts[i] for i in t.vertices] for t in ob.data.loop_triangles])
sys.path.insert(0,str(ROOT/'tools/world'));import numpy as np
from slice_geometry import capsule_distances
qa=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/walkability_candidate_b77.json').read_text(encoding='utf8'));tri=np.array(tris);lo=tri.min(axis=1);hi=tri.max(axis=1);routes={}
for name in ('upper','lower'):
    points=qa['routes'][name]['points'];samples=0;hits=[]
    for a,b in zip(points,points[1:]):
        for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.05)+1)):
            p=np.array(a)+(np.array(b)-a)*t;samples+=1
            near=np.all(hi>=p-np.array([.315,.315,.015]),axis=1)&np.all(lo<=p+np.array([.315,.315,1.815]),axis=1)
            if near.any() and float(capsule_distances(p,tri[near],.30,1.80).min())<.285:hits.append(p.tolist())
    routes[name]={'samples':samples,'new_mesh_penetrations':hits}
assert all(not v['new_mesh_penetrations'] for v in routes.values())
assert hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
with (ROOT/r['parent_file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['parent_sha256']
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame'])
eye=M@Vector((-55,-75,85));target=M@Vector((-25,0,48));direction=target-eye
screen=bpy.context.screen or next((w.screen for w in bpy.context.window_manager.windows if w.screen),None)
assert screen is not None, 'Janela visível não localizada; QA visual pendente'
for area in screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.region_3d.view_perspective='PERSP';sp.region_3d.view_rotation=direction.to_track_quat('-Z','Y');sp.region_3d.view_location=target;sp.region_3d.view_distance=direction.length;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;area.tag_redraw()
v={'passed':True,'reopened':True,'pid':os.getpid(),'checks':checks,'route_checks':routes,'scope':'Somente seis malhas B85 contra rotas candidatas históricas; não valida poço ou percurso inteiro','ssot_preserved':True,'b84_preserved':True,'low_city_tower_unchanged':True,'bridge_unchanged':True,'production_ready':False}
(OUT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r['reopened']=True;(OUT/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(ROOT/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'b85-encosta-support.png'})
print(json.dumps(v,ensure_ascii=False))
