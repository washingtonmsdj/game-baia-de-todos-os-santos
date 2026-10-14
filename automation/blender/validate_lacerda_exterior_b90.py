"""Validação consolidada B88–B90 na revisão reaberta, sem controller."""
import bpy,bmesh,json,os,runpy
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-massing-b90'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend'
reports=[json.loads((root/f'docs/reports/blender/lacerda-massing-b{n}/application.json').read_text()) for n in (88,89,90)]
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
expected={r['object']:r.get('after',r)['signature'] for r in reports[0]['changes']+reports[0]['added']}
expected.update({r['object']:r['after']['signature'] for r in reports[1]['changes']});expected.update({r['object']:r['after'] for r in reports[2]['changes']})
checks=[]
for name,state in expected.items():
    o=bpy.context.scene.objects[name];assert sig(o)==state,name
    bm=bmesh.new();bm.from_mesh(o.data);zero=sum(f.calc_area()<1e-9 for f in bm.faces);open_edges=sum(not e.is_manifold for e in bm.edges);bm.free();assert zero==0,name
    checks.append({'object':name,'degenerate_faces':zero,'nonmanifold_edges':open_edges})
def bounds(name):
    o=bpy.context.scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());dim=[]
for name,polygon in [('SUPERIOR | piso saguão','upper_floor'),('TORRE | cornija galeria','new_gallery'),('LAC R30B | Passarela | piso paginado visual','bridge'),('INFERIOR | piso do saguão','lower_floor')]:
    bb=bounds(name);p=cfg['polygons'][polygon]['points_local'];desired=[[min(v[i] for v in p),max(v[i] for v in p)] for i in (0,1)]
    error=max(abs(bb[i][j]-desired[i][j]) for i in (0,1) for j in (0,1));assert error<.001
    assert next(r for r in checks if r['object']==name)['nonmanifold_edges']==0,name
    dim.append({'object':name,'polygon':polygon,'bounds':bb,'cad_bound_residual_m':error})
up=bounds('SUPERIOR | piso saguão')[2][1];down=bounds('INFERIOR | piso do saguão')[2][1];roof=bounds('SUPERIOR | cobertura corpo elevado')[2][1];parapet=bounds('FACHADA SUPERIOR | platibanda')[2][1]
assert abs(up-down-59.01)<.001 and abs(roof-up-14)<.001 and abs(parapet-up-15.4)<.001
levels={'upper_minus_lower_m':up-down,'building_roof_above_upper_m':roof-up,'building_parapet_above_upper_m':parapet-up,'gallery_roof_above_upper_m':bounds('TORRE | teto galeria')[2][1]-up}
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text());assert proof['file']==reports[2]['file'] and proof['sha256']==reports[2]['sha256'] and proof['load_post_completed']
data={'revision':'R30B.90','file':reports[2]['file'],'scene':bpy.context.scene.name,'pid':os.getpid(),'reopened':True,'objects_checked':len(checks),'mesh_checks':checks,'dimension_checks':dim,'document_relative_levels':levels,'absolute_ssot_fit':'NOT_ACCEPTED','interior_layout':'NOT_VALIDATED','installed_elevators_validated':False,'controller_validated':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'production_ready':False}
(out/'validation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
reports[2]['reopened']=True;reports[2]['mesh_and_document_levels_checked']=True
(out/'application.json').write_text(json.dumps(reports[2],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':len(checks),'levels':levels,'reopened':True,'production_ready':False},ensure_ascii=False))
