"""Completa os pisos documentados faltantes na B100, na sessão visível."""
import bpy, bmesh, json, hashlib, runpy, os, shutil
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
out=root/'docs/reports/blender/lacerda-floors-b101'
before=json.loads((out/'before.json').read_text()); cfg=json.loads((out/'controls.json').read_text())
base=Path(bpy.data.filepath); catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json'
cat=json.loads(catpath.read_text()); dest=root/'blender/salvador_lacerda_r30b101_pavimentos_estruturais.blend'
assert base.name=='salvador_lacerda_r30b100_corpo_superior_cobertura.blend'
assert os.getpid()==before['pid'] and scene.name==before['scene'] and not bpy.data.is_dirty
with base.open('rb') as f: base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==cat['authoring_source']['sha256'] and not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*2
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py')); sig=h['signature']; wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
assert not before['session_geometry_delta']
assert all(sig(scene.objects[n])==s for n,s in before['preserved_signatures'].items())
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest(); assert ssot==cfg['ssot_sha256']
terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
protected={o.name:(o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects}
anchor=scene.objects['B99 | cidade alta | laje subsolo 01 área documentada']
material=anchor.data.materials[0]; staged=[]
for spec in cfg['floors']:
    assert spec['object'] not in bpy.data.objects
    p=[Vector(v) for v in spec['outline_local']]; n=len(p); z=spec['top_z']; th=cfg['thickness_candidate_m']
    verts=[(v.x,v.y,height) for height in (z-th,z) for v in p]; faces=[]
    ids={tuple(v):i for i,v in enumerate(p)}
    for tri in tessellate_polygon([[Vector((v.x,v.y,0.)) for v in p]]):
        ix=[v if isinstance(v,int) else ids[(v.x,v.y)] for v in tri]
        faces.extend([tuple(reversed(ix)),tuple(i+n for i in ix)])
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    mesh=bpy.data.meshes.new(spec['object']); mesh.from_pydata(verts,[],faces); mesh.materials.append(material)
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh)
    q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume_m3':bm.calc_volume(signed=True)}; bm.free()
    assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0,q
    assert abs(q['signed_volume_m3']-spec['area_m2']*th)<.001,q
    mesh.update(); staged.append((spec,mesh,q))
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,
         'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'controls_file':(out/'controls.json').relative_to(root).as_posix(),
         'preserved_signatures':before['preserved_signatures'],'terrain_signature':terrain,'proxy_signatures':proxy,'protected_object_count':len(protected)}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
added=[]
for spec,mesh,q in staged:
    o=bpy.data.objects.new(spec['object'],mesh); anchor.users_collection[0].objects.link(o); o.matrix_world=M
    props={'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.101',
           'boas_provenance_ids':json.dumps(['derived:lacerda-structural-floors-b101']), 'boas_function':spec['function'],
           'boas_source_control':journal['controls_file'],'accuracy':cfg['accuracy'],'replacement_required':True,
           'boas_production_ready':False,'boas_collision_enabled':False,'boas_printed_level_offset_m':spec['printed_level_offset_m'],
           'boas_structural_thickness_status':'CANDIDATE_NOT_AS_BUILT','boas_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE'}
    for k,v in props.items(): o[k]=v
    added.append({'object':o.name,'after':{'signature':sig(o)},'mesh':q,'outline_local':spec['outline_local'],
                  'levels':[spec['top_z']-cfg['thickness_candidate_m'],spec['top_z']],'function':spec['function']})
for n,state in protected.items():
    o=scene.objects[n]
    assert (o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert all(sig(scene.objects[n])==s for n,s in before['preserved_signatures'].items())
assert all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
scene['lacerda_revision']='R30B.101 | pavimentos estruturais documentais'; scene['boas_historic_movement_enabled']=False
r={**journal,'revision':'R30B.101','changes':[],'added':added,'archived':[],'invalidated_bindings':[],
   'reopened':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'production_ready':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json'; profile=json.loads(profilepath.read_text())
profile.setdefault('revision_history',[]).append({'revision':'R30B.101','scope':'Pisos dos subsolos02/03, escada sem preenchimento; instalação congelada, espessuras candidatas','movement_enabled':False,'evidence':(out/'application.json').relative_to(root).as_posix()})
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,
       'status':'architectural_structure_candidate','production_ready':False,'evidence':(out/'application.json').relative_to(root).as_posix(),
       'notes':'Pisos documentados15/14 nos níveis−9,74/−19,85; contorno relativo e espessura candidata; sem mudança do poço ou instalação.'}
cat['revisions'].append(entry)
for k in ('authoring_source','validation_source'):cat[k]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'added':len(added),'existing_meshes_changed':0},ensure_ascii=False))
