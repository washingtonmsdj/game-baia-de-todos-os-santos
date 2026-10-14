"""Finalização da mutação B93 já aplicada; não reexecutar buffers na sessão."""
import bpy,bmesh,json,hashlib,os,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-lower-structure-b93'
base=Path(bpy.data.filepath);assert base.name=='salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend'
dest=root/'blender/salvador_lacerda_r30b93_estrutura_inferior_documental.blend';assert not dest.exists()
scene=bpy.context.scene;assert scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
cfg=json.loads((out/'controls.json').read_text());before=json.loads((out/'before.json').read_text());rows={r['object']:r for r in before['rows']}
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
with base.open('rb') as f:parenthash=hashlib.file_digest(f,'sha256').hexdigest()
assert parenthash==cat['authoring_source']['sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
mutate=['INFERIOR | cobertura do saguão','INFERIOR | parede lateral','INFERIOR | parede lateral.001','CASCA | parede lateral']
legacy=[r['object'] for r in rows.values() if r['visible'] and (r['object'].startswith('FACHADA INFERIOR |') or r['object'].startswith('LAC R30B03 | Cidade Baixa |') or r['object'].startswith('LAC R30B07 | Cidade Baixa |') or r['object'].startswith('LAC R30B02 | Rodape escuro | INFERIOR |') or r['object']=='CALIBRADO | marquise baixa')]
def bounds(o):
    p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
def stats(o,strict=True):
    bm=bmesh.new();bm.from_mesh(o.data);d={'vertices':len(bm.verts),'faces':len(bm.faces),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)};bm.free()
    if strict:assert d['degenerate_faces']==d['nonmanifold_edges']==d['inconsistent_winding_edges']==0 and d['signed_volume']>0,(o.name,d)
    return d
top=cfg['levels']['roof_world'];floor=cfg['levels']['hall_floor_world'];bottom=top-.25
assert abs(bounds(scene.objects[mutate[0]])[2][1]-top)<1e-4
for n in mutate[1:3]:assert abs(bounds(scene.objects[n])[2][1]-bottom)<1e-4 and abs(bounds(scene.objects[n])[2][0]-floor)<1e-4
assert abs(bounds(scene.objects[mutate[3]])[2][0]-top)<1e-4
for n in mutate:assert scene.objects[n].get('boas_generated_revision')=='R30B.93'
for n in legacy:
    o=scene.objects[n];assert sig(o)==rows[n]['signature'] and o.hide_get() and o.hide_render and o.get('boas_role')=='SUPERSEDED_REFERENCE',n
protected=0
for n,row in rows.items():
    if n in mutate+legacy:continue
    o=scene.objects[n];assert sig(o)==row['signature'] and o.visible_get()==row['visible'],n;protected+=1
names=['B93 | frente inferior | pilar documental '+str(i) for i in range(1,5)]
added=[]
for i,n in enumerate(names):
    o=scene.objects[n];assert json.loads(o['boas_cad_curve_ids'])==cfg['pillars'][i]['cad_curve_ids']
    bb=bounds(o);assert abs(bb[2][0]-(floor-.25))<1e-4 and abs(bb[2][1]-bottom)<1e-4
    added.append({'object':n,'signature':sig(o),'mesh':stats(o),'control':cfg['pillars'][i]['id']})
# Os proxies pertencem a outra cena do mesmo arquivo. A comparação com B92
# será feita após a reabertura B93, pois Blender não importa o arquivo atual.
proxynames=[o.name for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects]
def plain(v):
    if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
    if hasattr(v,'to_list'):return v.to_list()
    return v
proxy={}
for n in proxynames:
    o=bpy.data.objects[n]
    proxy[n]={'signature':sig(o),'properties':{k:plain(v) for k,v in o.items()}}
terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
changes=[{'object':n,'before':{'signature':rows[n]['signature'],'bounds':rows[n]['bounds'],'visible':rows[n]['visible']},'after':{'signature':sig(scene.objects[n]),'visible':scene.objects[n].visible_get(),'mesh':stats(scene.objects[n],n not in legacy)},'operation':'PRESERVE_AS_REFERENCE' if n in legacy else 'RECONCILE_DOCUMENT_ROOF_LEVEL'} for n in mutate+legacy]
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile.get('collision_bindings',[]):
    if binding.get('source') in mutate+legacy or binding.get('source_object') in mutate+legacy:
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_RELATIVE_STRUCTURE_B93';invalidated.append(binding['object'])
report={'revision':'R30B.93','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':parenthash,'pid':os.getpid(),'scene':scene.name,'changes':changes,'added':added,'protected_object_count':protected,'proxy_before':proxy,'terrain_signature':terrain,'ssot_sha256':ssot,'levels':cfg['levels'],'roof_delta_applied':top-rows[mutate[0]]['bounds'][2][1],'legacy_front_preserved':len(legacy),'invalidated_bindings':invalidated,'terrain_samples_before':before['terrain_samples'],'absolute_map_placement':'NEEDS_REVIEW','LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'production_ready':False,'reopened':False,
 'staging_note':'Triangulação degenerada do hatch rejeitada antes de aplicar; ear clipping double mantém envoltória. Finalização após corrigir acesso à coleção B82 pertencente a outra cena.'}
scene['lacerda_revision']='R30B.93 | estrutura inferior relativa documental; implantação/instalação pendentes';scene['boas_historic_movement_enabled']=False
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.93','scope':'Cota documental da cobertura inferior e quatro apoios frontais; sem implantação/controller aprovado','movement_enabled':False,'evidence':path.relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.93','parent_file':report['parent_file'],'sha256':report['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Cota inferior -53.17 e quatro apoios CAD12; implantação absoluta e instalação não aprovadas.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B93','file':report['file'],'sha256':report['sha256'],'pillars_added':len(added),'legacy_front_preserved':len(legacy),'production_ready':False},ensure_ascii=False))
