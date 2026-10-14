"""Reconciliação da frente oblíqua superior, preservando toda a referência antiga."""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import tessellate_polygon
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;base=Path(bpy.data.filepath);out=root/'docs/reports/blender/lacerda-completion-b98'
before=json.loads((out/'before.json').read_text());cfg=json.loads((out/'controls.json').read_text());catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
assert base.name=='salvador_lacerda_r30b97_limites_vestibulos_superiores.blend' and scene.name==before['scene'] and os.getpid()==before['pid'] and not bpy.data.is_dirty
assert before['session_geometry_delta']==[] and before['file_sha256']==cat['authoring_source']['sha256']
dest=root/'blender/salvador_lacerda_r30b98_frente_superior_reconciliada.blend';assert not dest.exists() and shutil.disk_usage(root).free>base.stat().st_size*2
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
rows={r['object']:r for r in before['rows']};archive=[r['object'] for r in before['rows'] if r['object'].startswith('FACHADA SUPERIOR |') and r['bounds'][2][1]<74.]
assert len(archive)==67;archive.append('FACHADA SUPERIOR | marquise longa')
for n in archive:assert sig(scene.objects[n])==rows[n]['signature'],n
assert not any(scene.objects[n].animation_data or scene.objects[n].constraints for n in archive)
protected={o.name:(o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in archive}
prior=json.loads((root/'docs/reports/blender/lacerda-vestibules-b97/application.json').read_text());preserved=dict(prior['preserved_signatures'])
for row in prior['added']:preserved[row['object']]=row['after']['signature']
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
def stats(data):
 bm=bmesh.new();bm.from_mesh(data);q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0 and q['volume']>0,q
 return q
buffers=[]
def prism(name,poly,z0,z1,material,source,function):
 p=[Vector((x,y,0.)) for x,y in poly];count=len(p);data=bpy.data.meshes.new(name)
 ids={tuple(v):i for i,v in enumerate(p)};faces=[]
 for tri in tessellate_polygon([p]):
  indices=[v if isinstance(v,int) else ids[tuple(v)] for v in tri];faces.extend([tuple(reversed(indices)),tuple(i+count for i in indices)])
 faces.extend((i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count))
 data.from_pydata([(v.x,v.y,z) for z in (z0,z1) for v in p],[],faces);data.materials.append(material)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update()
 buffers.append((name,data,stats(data),source,function,poly,[z0,z1]))
stone=scene.objects['FACHADA SUPERIOR | pilar térreo'].data.materials[0];shutter=scene.objects['FACHADA SUPERIOR | persiana lateral'].data.materials[0]
z=cfg['levels']['floor'];zc=cfg['levels']['ceiling'];zh=z+cfg['levels']['opening_height_candidate']
for p in cfg['pillars']:prism('B98 | frente superior | apoio '+p['id'][-1],p['points_local'],z,zc,stone,p['id'],'STRUCTURAL_PILLAR')
for i,p in enumerate(cfg['spans'],1):
 prism(f'B98 | frente superior | verga {i}',p['points_local'],zh,zc,stone,p['id'],'HEADER_CANDIDATE_HEIGHT')
 if p['function']!='MAIN_OPEN_ACCESS':prism(f'B98 | frente superior | fechamento rolo {i}',p['points_local'],z,zh,shutter,p['id'],'ROLLER_MASSING_APPROXIMATE')
journal={'file':dest.relative_to(root).as_posix(),'parent_file':before['file'],'parent_sha256':before['file_sha256'],'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'controls_file':(out/'controls.json').relative_to(root).as_posix(),'preserved_signatures':preserved,'terrain_signature':terrain,'proxy_signatures':proxy,'protected_object_count':len(protected),'planned_archive':archive}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
added=[];collection=scene.objects['SUPERIOR | piso saguão'].users_collection[0]
for name,data,q,src,function,poly,levels in buffers:
 assert name not in bpy.data.objects
 o=bpy.data.objects.new(name,data);collection.objects.link(o);o.matrix_world=M
 for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.98','boas_source_control':src,'boas_function':function,'boas_provenance_ids':json.dumps(['derived:lacerda-upper-completion-b98']),'accuracy':'DOCUMENT_RELATIVE_CONTOUR_WITH_CANDIDATE_SECTION','replacement_required':True,'boas_production_ready':False,'boas_collision_enabled':False}.items():o[k]=v
 added.append({'object':name,'after':{'signature':sig(o)},'mesh':q,'source_control':src,'outline_local':poly,'levels':levels,'function':function})
archived=[]
for n in archive:
 o=scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_archive_revision']='R30B.98';o['boas_replaced_by']='docs/reports/blender/lacerda-completion-b98/controls.json';assert sig(o)==rows[n]['signature']
 archived.append({'object':n,'before':rows[n]['signature'],'after_signature':sig(o),'operation':'PRESERVE_SUPERSEDED_REFERENCE','reason':'Legacy straight five-bay façade incompatible with controlled oblique four-support front' if 'marquise' not in n else cfg['canopy_decision']})
for n,state in protected.items():
 o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert all(sig(scene.objects[n])==s for n,s in preserved.items()) and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain and hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for b in profile['collision_bindings']:
 if b.get('source_object',b.get('source')) in archive:
  b['enabled']=False;b['validation_status']='INVALIDATED_BY_FRONT_B98';invalidated.append(b['object'])
scene['lacerda_revision']='R30B.98 | frente oblíqua, apoios, vãos e encontros superiores reconciliados';scene['boas_historic_movement_enabled']=False
r={**journal,'revision':'R30B.98','changes':[],'added':added,'archived':archived,'invalidated_bindings':invalidated,'reopened':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'production_ready':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.98','scope':'Frente superior reconciliada; referência legada preservada; instalação histórica permanece bloqueada','movement_enabled':False,'evidence':(out/'application.json').relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':(out/'application.json').relative_to(root).as_posix(),'notes':'Frente oblíqua CAD17/níveis23; seção/abertura/cortinas candidatas, referências anteriores preservadas.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'added':len(added),'archived_preserved':len(archived),'existing_geometry_changed':0},ensure_ascii=False))
