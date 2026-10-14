"""Lambril sem faces colapsadas e validação limitada do encontro B84."""
import bpy,bmesh,json,runpy,math,os,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-glazing-b84'
report=json.loads((OUT/'application.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/report['file']).resolve()
h=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']);inv=M.inverted();scene=bpy.context.scene
names=[n for n in report['changed_objects'] if 'Lambril' in n]
with bpy.data.libraries.load(str(ROOT/report['parent_file']),link=False) as (available,requested):requested.objects=list(names)
for name,src in zip(names,requested.objects):
    ob=scene.objects[name];mesh=src.data.copy();mesh.materials.clear()
    for mat in ob.data.materials:mesh.materials.append(mat)
    tw=wm(ob);ti=tw.inverted();p=[inv@tw@v.co for v in mesh.vertices];lo=min(v.z for v in p);hi=max(v.z for v in p);top=report['panels'][0]['glass_z'][0]-.025
    for v,q in zip(mesh.vertices,p):q.z=lo+(q.z-lo)*(top-lo)/(hi-lo);v.co=ti@M@q
    ob.data=mesh;bpy.data.objects.remove(src,do_unlink=True)
baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf8'));unexpected=[]
for name,old in baseline.items():
    o=scene.objects.get(name)
    if not o:unexpected.append(name);continue
    try:actual=sig(o)
    except RuntimeError:actual={'type':o.type,'basis':[list(r) for r in o.matrix_basis],'data':o.data.name if o.data else None}
    if name not in report['changed_objects'] and actual!=old:unexpected.append(name)
assert not unexpected,str(unexpected)
checks=[];tris=[]
for name in report['changed_objects']:
    ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
    result={'object':name,'degenerate':sum(f.calc_area()<1e-8 for f in bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges)};bm.free();assert not result['degenerate'] and not result['nonmanifold'];checks.append(result)
    ob.data.calc_loop_triangles();vs=[list(wm(ob)@v.co) for v in ob.data.vertices];tris.extend([[vs[i] for i in t.vertices] for t in ob.data.loop_triangles])
sys.path.insert(0,str(ROOT/'tools/world'));import numpy as np
from slice_geometry import capsule_distances
qa=json.loads((ROOT/'docs/reports/blender/lacerda-corridor/walkability_candidate_b77.json').read_text(encoding='utf8'));samples=0;hits=[]
tri=np.array(tris);lo=tri.min(axis=1);hi=tri.max(axis=1)
for a,b in zip(qa['routes']['upper']['points'],qa['routes']['upper']['points'][1:]):
    for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.05)+1)):
        p=np.array(a)+(np.array(b)-a)*t;samples+=1
        near=np.all(hi>=p-np.array([.315,.315,.015]),axis=1)&np.all(lo<=p+np.array([.315,.315,1.815]),axis=1)
        if near.any() and float(capsule_distances(p,tri[near],.30,1.80).min())<.285:hits.append(p.tolist())
assert not hits
assert len(bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects)==70
assert hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()==report['ssot_sha256']
# Enquadramento externo, na mesma cena histórica completa.
eye=M@Vector((-22,-23,80));target=M@Vector((-5.35,-5.8,72.3));direction=target-eye
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.region_3d.view_perspective='PERSP';sp.region_3d.view_rotation=direction.to_track_quat('-Z','Y');sp.region_3d.view_location=target;sp.region_3d.view_distance=direction.length;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/report['file']),compress=True,check_existing=False)
with (ROOT/report['file']).open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(OUT/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
catpath=ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text(encoding='utf8'))
for entry in [cat['authoring_source'],cat['validation_source']]+cat['revisions']:
    if entry['file']==report['file']:entry['sha256']=report['sha256']
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
validation={'passed':True,'pid':os.getpid(),'checks':checks,'baseline_objects_checked':len(baseline),'unexpected_changes':unexpected,'upper_capsule_samples':samples,'upper_capsule_penetrations':hits,'scope':'Quatro malhas alteradas versus percurso superior; não certifica poço ou trajeto completo','colliders_preserved':True,'ssot_preserved':True,'proxy_preserved':True,'production_ready':False}
(OUT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(validation,ensure_ascii=False))
