"""QA métrico/mesh da estrutura, sem aprovar instalação ou controller."""
import bpy,bmesh,json,os,runpy,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-massing-b89'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b89_conjunto_arquitetonico_niveis.blend'
r88=json.loads((root/'docs/reports/blender/lacerda-massing-b88/application.json').read_text());report=json.loads((out/'application.json').read_text());cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
expected={r['object']:r.get('after',r)['signature'] for r in r88['changes']+r88['added']}
expected.update({r['object']:r['after']['signature'] for r in report['changes']})
checks=[]
for name,state in expected.items():
    o=bpy.context.scene.objects[name];assert sig(o)==state,name
    bm=bmesh.new();bm.from_mesh(o.data);zero=sum(f.calc_area()<1e-9 for f in bm.faces);open_edges=sum(not e.is_manifold for e in bm.edges);bm.free();assert zero==0,name
    checks.append({'object':name,'degenerate_faces':zero,'nonmanifold_edges':open_edges})
def bounds(name):
    o=bpy.context.scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
dim=[]
for name,polygon in [('SUPERIOR | piso saguão','upper_floor'),('TORRE | cornija galeria','new_gallery'),('LAC R30B | Passarela | piso paginado visual','bridge'),('INFERIOR | piso do saguão','lower_floor')]:
    bb=bounds(name);p=cfg['polygons'][polygon]['points_local'];desired=[[min(v[i] for v in p),max(v[i] for v in p)] for i in (0,1)]
    error=max(abs(bb[i][j]-desired[i][j]) for i in (0,1) for j in (0,1));assert error<.001
    assert next(r for r in checks if r['object']==name)['nonmanifold_edges']==0,name
    dim.append({'object':name,'polygon':polygon,'bounds':bb,'cad_bound_residual_m':error})
up=bounds('SUPERIOR | piso saguão')[2][1];down=bounds('INFERIOR | piso do saguão')[2][1]
assert abs(up-down-59.01)<.001
gate={'measured_relative_floor_difference_m':up-down,'printed_drawing_floor_difference_m':59.01,'upper_floor_z':up,'lower_floor_z':down,'level_difference_residual_m':abs(up-down-59.01)}
proof_path=root/'artifacts/blender-sessions/last-open.json';proof=json.loads(proof_path.read_text()) if proof_path.exists() else {}
reopened=proof.get('file')==report['file'] and proof.get('sha256')==report['sha256'] and proof.get('load_post_completed') is True
data={'revision':'R30B.89','file':report['file'],'scene':bpy.context.scene.name,'pid':os.getpid(),'reopened':reopened,'objects_checked':len(checks),'mesh_checks':checks,'dimension_checks':dim,'relative_levels':gate,'independent_ssot_registration':False,'installed_elevators_validated':False,'controller_validated':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'production_ready':False}
(out/'validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report['reopened']=reopened;report['mesh_and_document_dimensions_checked']=True
(out/'application.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':len(checks),'relative_levels':gate,'reopened':reopened,'production_ready':False},ensure_ascii=False))
