"""Cotas exteriores +14,00 cobertura / +15,40 platibanda, prancha 23."""
import bpy,bmesh,json,hashlib,runpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-massing-b90';out.mkdir(parents=True,exist_ok=True)
base=Path(bpy.data.filepath);assert base.name=='salvador_lacerda_r30b89_conjunto_arquitetonico_niveis.blend'
dest=root/'blender/salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend';assert not dest.exists()
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());upper=cfg['levels']['upper_walkable']
targets={'FACHADA SUPERIOR | platibanda':(upper+14.,upper+15.40),'EDIFICIO | platibanda lateral':(upper+14.,upper+15.40),'EDIFICIO | platibanda lateral.001':(upper+14.,upper+15.40),'SUPERIOR | cobertura corpo elevado':(upper+13.75,upper+14.),'EDIFICIO | cobertura':(upper+13.88,upper+14.)}
scene=bpy.context.scene
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
staged=[];changes=[]
for n,(bottom,top) in targets.items():
    o=scene.objects[n];tr=inv@wm(o);back=wm(o).inverted()@M;p=[tr@v.co for v in o.data.vertices];a=min(v.z for v in p);b=max(v.z for v in p);assert b-a>.01
    before=sig(o);mesh=o.data.copy()
    for v in mesh.vertices:
        q=tr@v.co;q.z=bottom+(q.z-a)*(top-bottom)/(b-a);v.co=back@q
    bm=bmesh.new();bm.from_mesh(mesh);assert not any(f.calc_area()<1e-9 for f in bm.faces);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    staged.append((o,mesh));changes.append({'object':n,'before':before,'before_levels':[a,b],'after_levels':[bottom,top],'source':'source:lacerda-issue22-sucop-23','printed_levels':[14.,15.4] if 'platibanda' in n else [None,14.],'scope':'somente Z de envoltória/cobertura; XY e layout não certificados'})
for o,mesh in staged:
    o.data=mesh;o['boas_generated_revision']='R30B.90';o['boas_provenance_ids']=json.dumps(['derived:lacerda-massing-b90']);o['boas_exterior_level_status']='PROJECT_PRINTED_RELATIVE_LEVEL';o['replacement_required']=True;o['boas_production_ready']=False
for r in changes:r['after']=sig(scene.objects[r['object']])
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
scene['lacerda_revision']='R30B.90 | estrutura/cotas exteriores SUCOP; implantação e interiores pendentes'
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text());base_hash=cat['authoring_source']['sha256']
report={'revision':'R30B.90','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,'scene':scene.name,'pid':os.getpid(),'changes':changes,'ssot_sha256':ssot,'terrain_preserved':True,'proxy_b82_preserved':True,'production_ready':False,'reopened':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'source_level_crop':'artifacts/lacerda-proportions/sheet23-levels.png'}
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.90','parent_file':report['parent_file'],'sha256':digest,'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Envoltória relativa SUCOP, ponte/torres/saguões e níveis exteriores; implantação e as-built ainda pendentes.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B90','changes':len(changes),'file':report['file'],'sha256':digest}))
