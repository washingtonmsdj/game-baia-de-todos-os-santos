"""Completa a correção da seleção B88 na coleção calibrada da ponte."""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-bridge-b92';out.mkdir(parents=True,exist_ok=True)
base=Path(bpy.data.filepath);assert base.name=='salvador_lacerda_r30b91_integridade_malha_e_apoios.blend';assert os.getpid()==16912
dest=root/'blender/salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text());prior=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/application.json').read_text())
assert prior['reopened'] and cat['authoring_source']['file']==prior['file']
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==prior['sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
legacy=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/remaining-legacy.json').read_text());rows={r['object']:r for r in legacy}
roof_name='CALIBRADO | passarela cobertura 28.71 x 6.00m';roof=bpy.context.scene.objects[roof_name]
retire=sorted(n for n in rows if n.startswith('CALIBRADO | montante passarela') or n.startswith('CALIBRADO | passarela viga lateral'))
assert len(retire)==20
assert all(sig(bpy.context.scene.objects[n])==rows[n]['signature'] for n in retire+[roof_name])
upper=cfg['levels']['upper_walkable'];p=[Vector(v) for v in cfg['polygons']['bridge']['points_local']]
area=sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
if area<0:p.reverse()
N=len(p);back=wm(roof).inverted()@M;mesh=bpy.data.meshes.new('B92 | cobertura da ponte documental')
mesh.from_pydata([tuple(back@Vector((v.x,v.y,z))) for z in (upper+3.75,upper+4.) for v in p],[],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)])
for mat in roof.data.materials:mesh.materials.append(mat)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-9 for f in bm.faces);bm.to_mesh(mesh);bm.free()
terrain=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];terrain_sig=sig(terrain)
proxy_col=bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'];proxy_sigs={o.name:sig(o) for o in proxy_col.objects}
def plain(value):
 if hasattr(value,'to_dict'):return {k:plain(v) for k,v in value.to_dict().items()}
 if hasattr(value,'to_list'):return value.to_list()
 return value
def props(o):return {k:plain(v) for k,v in o.items()}
# O proxy cita a laje histórica, mas seu contrato é separado. Comparar todos
# os metadados com B90 e restaurar somente eventuais anotações indevidas.
proxy=bpy.data.objects['B82 | upper_walkway'];before_proxy_props=props(proxy)
before_objs=set(bpy.data.objects);before_meshes=set(bpy.data.meshes);before_mats=set(bpy.data.materials)
with bpy.data.libraries.load(str(root/prior['parent_file']),link=False) as (available,requested):requested.objects=[proxy.name]
loaded=requested.objects[0];expected_proxy_props=props(loaded)
try:
 assert sig(loaded)==sig(proxy)
 delta={k for k in set(before_proxy_props)|set(expected_proxy_props) if before_proxy_props.get(k)!=expected_proxy_props.get(k)}
 assert delta.issubset({'boas_collision_validation','boas_physical_enabled'}),delta
 for k in delta:
  if k in expected_proxy_props:proxy[k]=expected_proxy_props[k]
  else:del proxy[k]
 assert props(proxy)==expected_proxy_props
finally:
 for o in set(bpy.data.objects)-before_objs:
  if not o.users_scene:bpy.data.objects.remove(o,do_unlink=True)
 for table,known in ((bpy.data.meshes,before_meshes),(bpy.data.materials,before_mats)):
  for data in set(table)-known:
   if not data.users:table.remove(data)
before={n:{'signature':sig(bpy.context.scene.objects[n]),'visible':bpy.context.scene.objects[n].visible_get()} for n in retire+[roof_name]}
roof.data=mesh
for k,v in {'boas_generated_revision':'R30B.92','boas_provenance_ids':json.dumps(['derived:lacerda-bridge-b92']),'boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','accuracy':'PROJECT_XY_AND_PRINTED_RELATIVE_TOP_LEGACY_THICKNESS','replacement_required':True,'boas_production_ready':False,'boas_location_id':'elevador-lacerda','boas_pending_gate':'ABSOLUTE_SSOT_PLACEMENT_AND_STRUCTURE_THICKNESS','dimensoes_status':'Contorno CAD SUCOP17; topo +4,00 SUCOP23; espessura candidata sem cota própria'}.items():roof[k]=v
for n in retire:
 o=bpy.context.scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_superseded_reason']='Esboço de ponte de 55,54m omitido na seleção B88; representação atual já existe no contorno documental';o['boas_provenance_ids']=json.dumps(['derived:lacerda-bridge-b92'])
 o['boas_superseded_by']='PASSARELA EXTERNA | caixilho / LAC R30B08 | passarela | viga longitudinal inferior'
assert sig(terrain)==terrain_sig and all(sig(bpy.data.objects[n])==s for n,s in proxy_sigs.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
changes=[{'object':n,'before':before[n],'after':{'signature':sig(bpy.context.scene.objects[n]),'visible':bpy.context.scene.objects[n].visible_get()},'operation':'PRESERVE_AS_REFERENCE' if n in retire else 'RECONSTRUCT_DOCUMENT_CONTOUR'} for n in retire+[roof_name]]
report={'revision':'R30B.92','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,'pid':os.getpid(),'scene':bpy.context.scene.name,'changes':changes,'sources':['source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],
 'proxy_metadata_restored':{'object':proxy.name,'changed_keys':sorted(delta),'source':prior['parent_file'],'expected':expected_proxy_props},'proxy_b82_preserved':True,'terrain_preserved':True,'ssot_sha256':ssot,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'production_ready':False,'reopened':False}
bpy.context.scene['lacerda_revision']='R30B.92 | ponte documental consolidada e malhas B91; implantação/instalação pendentes'
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'sha256':digest,'revision':'R30B.92','parent_file':report['parent_file'],'scene':report['scene'],'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Completa seleção da ponte: cobertura documental, 20 controles legados preservados fora da camada ativa; QA B91 preservada.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B92','file':report['file'],'sha256':digest,'changed_roof':1,'preserved_legacy_components':len(retire),'proxy_metadata_restored':sorted(delta)},ensure_ascii=False))
