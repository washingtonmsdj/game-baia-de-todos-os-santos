"""Reconciliação conjunta da face posterior com cobertura e envelope superior."""
import bpy,bmesh,json,hashlib,os,runpy,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96';base=Path(bpy.data.filepath);scene=bpy.context.scene
assert base.name=='salvador_lacerda_r30b95_limites_circulacoes_superiores.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
dest=root/'blender/salvador_lacerda_r30b96_encontro_corpo_cobertura.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
with base.open('rb') as f:parenthash=hashlib.file_digest(f,'sha256').hexdigest()
assert parenthash==cat['authoring_source']['sha256']
prior=json.loads((out/'before.json').read_text());assert not prior['geometry_session_delta']
recovery=json.loads((root/'artifacts/blender-sessions/current-session.json').read_text());assert (root/recovery['recovery_file']).exists()
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());layout=json.loads((root/'docs/reports/blender/lacerda-layout-b86/layout_source.json').read_text());ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
rows={r['object']:r for r in prior['rows']};wall='EDIFICIO | parede posterior alta'
names=[n for n,r in rows.items() if r['visible'] and r['properties'].get('boas_architectural_domain')=='UPPER_BUILDING' and n.startswith('EDIFICIO |') and 'posterior' in n]
assert len(names)==7 and wall in names
for n in names:assert sig(scene.objects[n])==rows[n]['signature'],n
z=cfg['levels']['upper_walkable'];target_x=layout['upper_building_x'][0];target_z=z+4.;dx=target_x-rows[wall]['bounds'][0][0];dz=target_z-rows[wall]['bounds'][2][0]
assert .15<dx<.2 and .07<dz<.1
assert abs(rows[wall]['bounds'][2][1]+dz-(z+14.))<1e-4
delta=Vector((dx,0.,dz));protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in names}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
def stats(mesh):
    bm=bmesh.new();bm.from_mesh(mesh);groups={}
    for f in bm.faces:
        key=tuple(sorted(tuple(round(float(x),6) for x in v.co) for v in f.verts));groups.setdefault(key,[]).append(f)
    q={'vertices':len(bm.verts),'faces':len(bm.faces),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'duplicate_face_groups':sum(len(v)>1 for v in groups.values()),'signed_volume':bm.calc_volume(signed=True)};bm.free();return q
buffers={}
for n in names:
    o=scene.objects[n];data=o.data.copy();data.name='B96 | '+n;T=inv@wm(o);back=wm(o).inverted()@M
    for v in data.vertices:v.co=back@(T@v.co+delta)
    data.update();q=stats(data)
    assert q['degenerate_faces']==q['nonmanifold_edges']==q['inconsistent_winding_edges']==q['duplicate_face_groups']==0,(n,q)
    buffers[n]=data
controls={'vertical_sources':['source:lacerda-issue22-sucop-23:+4.00 cobertura da passarela','source:lacerda-issue22-sucop-23:+14.00 cobertura do edifício'],'xy_envelope_source':'docs/reports/blender/lacerda-layout-b86/layout_source.json#/upper_building_x','xy_classification':'ADAPT_LOCAL / CANDIDATE_ENVELOPE_CONTINUITY','xy_not_as_built':True,'target_west_face_local_x':target_x,'target_wall_levels':[target_z,z+14.],'common_frame_delta':list(delta),'thickness_status':'INHERITED_CANDIDATE_UNCHANGED','genealogy':'B88 upper_building usa origem75.20; parede posterior legada inicia75.10. A diferença mapeada deixou base/término 0.08333m abaixo dos controles comuns. Parede também estava centrada no limite oeste, extrapolando a cobertura pela metade da espessura.','purpose':'Fechar encontro exterior parede/cobertura e cantos; não corrigir geografia ou acomodar cápsula.'}
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':parenthash,'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'session_recovery':recovery,'geometry_session_delta':prior['geometry_session_delta'],'controls':controls,'planned_changes':names,'terrain_signature':terrain,'proxy_signatures':proxy}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,data in buffers.items():
    o=scene.objects[n];o.data=data
    for k,v in {'boas_generated_revision':'R30B.96','boas_provenance_ids':json.dumps(['derived:lacerda-upper-body-b96']),'accuracy':'DOCUMENT_RELATIVE_LEVELS_CANDIDATE_UPPER_ENVELOPE','boas_fidelity_classification':'ADAPT_LOCAL','replacement_required':True,'boas_production_ready':False,'boas_structural_cause':'LEGACY_UPPER_BUILDING_BASE_AND_WEST_PLANE','boas_applied_frame_delta':json.dumps(list(delta))}.items():o[k]=v
for n,state in protected.items():
    o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
def bounds(o):
    p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
changes=[{'object':n,'before':{'signature':rows[n]['signature'],'bounds':rows[n]['bounds']},'after':{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n]),'mesh':stats(scene.objects[n].data)}} for n in names]
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile['collision_bindings']:
    if binding.get('source') in names or binding.get('source_object') in names:
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_BODY_RECONCILIATION_B96';invalidated.append(binding['object'])
scene['lacerda_revision']='R30B.96 | encontro posterior do corpo superior/cobertura';scene['boas_historic_movement_enabled']=False
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
r={**journal,'revision':'R30B.96','changes':changes,'added':[],'protected_object_count':len(protected),'invalidated_bindings':invalidated,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'terrain_changed':False,'proxy_b82_preserved':True,'production_ready':False,'reopened':False}
path=out/'application.json';path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.96','scope':'Grupo posterior reconciliado com envelope candidato/cotas superiores; poço intacto','movement_enabled':False,'evidence':path.relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Encontro posterior superior reconciliado por controles verticais e envelopeXY candidato; não certifica as-built/implantação/controller.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B96','changed':len(changes),'delta_local':list(delta),'file':r['file'],'sha256':r['sha256']},ensure_ascii=False))
