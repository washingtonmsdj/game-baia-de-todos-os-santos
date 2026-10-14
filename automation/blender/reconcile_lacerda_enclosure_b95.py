"""Limites superiores da planta17, sem esticar vidro ou bloquear entradas."""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;base=Path(bpy.data.filepath);out=root/'docs/reports/blender/lacerda-enclosure-b95'
assert base.name=='salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
assert not bpy.data.is_dirty,'Há edição pendente na janela; não substituir silenciosamente'
dest=root/'blender/salvador_lacerda_r30b95_limites_circulacoes_superiores.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
with base.open('rb') as f:parenthash=hashlib.file_digest(f,'sha256').hexdigest()
assert parenthash==cat['authoring_source']['sha256']
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());prior=json.loads((out/'before.json').read_text());rows={v['object']:v for v in prior['rows']}
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted();z=cfg['levels']['upper_walkable']
upper=[Vector(p) for p in cfg['polygons']['upper_floor']['points_local']];bp=[Vector(p) for p in cfg['polygons']['bridge']['points_local']]
targets={'SUPERIOR | parede lateral saguão.001':upper[1].x,'SUPERIOR | parede lateral saguão':upper[8].x}
beam='SUPERIOR | posterior sobre passarela'
archived=[n for n in rows if 'posterior lateral' in n];assert len(archived)==6
edited=set(targets)|{beam};allowed=edited|set(archived)
for n in allowed:assert sig(scene.objects[n])==rows[n]['signature'],n
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in allowed}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
def stats(data):
    bm=bmesh.new();bm.from_mesh(data);groups={}
    for f in bm.faces:
        key=tuple(sorted(tuple(round(float(v),6) for v in p.co) for p in f.verts));groups.setdefault(key,[]).append(f)
    q={'vertices':len(bm.verts),'faces':len(bm.faces),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'duplicate_face_groups':sum(len(v)>1 for v in groups.values()),'signed_volume':bm.calc_volume(signed=True)};bm.free();return q
def approve(data,label):
    q=stats(data);assert q['degenerate_faces']==q['nonmanifold_edges']==q['inconsistent_winding_edges']==q['duplicate_face_groups']==0 and q['signed_volume']>0,(label,q)
def clipped_wall(o,x):
    data=o.data.copy();data.name='B95 | '+o.name;T=inv@wm(o)
    for v in data.vertices:v.co=T@v.co
    bm=bmesh.new();bm.from_mesh(data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=Vector((x,0.,0.)),plane_no=Vector((1.,0.,0.)),clear_outer=True,clear_inner=False)
    border=[e for e in bm.edges if e.is_boundary]
    assert all(all(abs(v.co.x-x)<1e-4 for v in e.verts) for e in border),'Não fechar bordas que não vieram do corte'
    filled=bmesh.ops.holes_fill(bm,edges=border,sides=0)['faces']
    for f in filled:
        neighbors=[g for e in f.edges for g in e.link_faces if g!=f]
        if neighbors:f.material_index=neighbors[0].material_index
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    back=wm(o).inverted()@M
    for v in data.vertices:v.co=back@v.co
    data.update();approve(data,o.name);return data
buffers={n:clipped_wall(scene.objects[n],x) for n,x in targets.items()}
o=scene.objects[beam];a,b=bp[1],bp[2];inward=Vector((1.,0.))*.18;p=[a,b,b+inward,a+inward]
data=bpy.data.meshes.new('B95 | verga no portal CAD');back=wm(o).inverted()@M
data.from_pydata([tuple(back@Vector((v.x,v.y,level))) for level in (z+3.75,z+4.) for v in p],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for mat in o.data.materials:data.materials.append(mat)
bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update();approve(data,beam);buffers[beam]=data
before={n:{'signature':sig(scene.objects[n]),'bounds':rows[n]['bounds'],'visible':scene.objects[n].visible_get()} for n in allowed}
controls={'source':'source:lacerda-issue22-sucop-17','source_controls':'docs/reports/blender/lacerda-massing-b88/architectural-controls.json','north_glazing_end':list(upper[1]),'south_glazing_end':list(upper[8]),'bridge_portal':[list(bp[1]),list(bp[2])],'header_levels':[z+3.75,z+4.],'header_thickness_m':.18,'thickness_status':'INHERITED_CANDIDATE','intentional_open_areas':['ENTRADA 15.17m²','SAÍDA 20.10m²'],'accuracy':'DOCUMENT_RELATIVE_CONTOURS_NOT_AS_BUILT'}
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':parenthash,'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'before':before,'controls':controls,'planned_changes':sorted(edited),'planned_archive':archived,'terrain_signature':terrain,'proxy_signatures':proxy}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for n,data in buffers.items():
    o=scene.objects[n];o.data=data
    for k,v in {'boas_generated_revision':'R30B.95','boas_provenance_ids':json.dumps(['derived:lacerda-upper-enclosure-b95']),'accuracy':'DOCUMENT_CONTOURS_INHERITED_THICKNESS','replacement_required':True,'boas_production_ready':False,'boas_role':'ARCHITECTURAL_MODEL_CANDIDATE'}.items():o[k]=v
for n in archived:
    o=scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_replaced_by']='B94 | saguão passarela | retorno '+('norte' if n.endswith('.001') else 'sul');o['boas_archive_revision']='R30B.95'
    assert sig(o)==before[n]['signature'],n
for n,state in protected.items():
    o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
def bounds(o):
    p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
changes=[{'object':n,'operation':'CLIP_AT_DOCUMENTED_END' if n in targets else 'RECONSTRUCT_HEADER_AT_ROOF','before':before[n],'after':{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n]),'mesh':stats(scene.objects[n].data)}} for n in sorted(edited)]
archive=[{'object':n,'operation':'PRESERVE_SUPERSEDED_REFERENCE','before':before[n],'after':{'signature':sig(scene.objects[n]),'visible':False}} for n in archived]
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile['collision_bindings']:
    if binding.get('source') in allowed or binding.get('source_object') in allowed:
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_ENCLOSURE_B95';invalidated.append(binding['object'])
scene['lacerda_revision']='R30B.95 | limites superiores documentais; referências obsoletas separadas';scene['boas_historic_movement_enabled']=False
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
r={**journal,'revision':'R30B.95','changes':changes,'archived':archive,'added':[],'protected_object_count':len(protected),'invalidated_bindings':invalidated,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'terrain_changed':False,'proxy_b82_preserved':True,'production_ready':False,'reopened':False}
path=out/'application.json';path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.95','scope':'Limites das circulações superiores e verga; referências anteriores preservadas','movement_enabled':False,'evidence':path.relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Limites das circulações superiores conforme planta17; instalação/controller e implantação ainda pendentes.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B95','changed':len(changes),'archived_preserved':len(archive),'file':r['file'],'sha256':r['sha256']},ensure_ascii=False))
