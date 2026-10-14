"""Limites dos vestíbulos da prancha17, seção explicitamente candidata."""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;base=Path(bpy.data.filepath)
assert base.name=='salvador_lacerda_r30b96_encontro_corpo_cobertura.blend' and os.getpid()==16912 and not bpy.data.is_dirty
dest=root/'blender/salvador_lacerda_r30b97_limites_vestibulos_superiores.blend';assert not dest.exists()
assert shutil.disk_usage(root).free>base.stat().st_size*2
out=root/'docs/reports/blender/lacerda-vestibules-b97';cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
prior=json.loads((root/'docs/reports/blender/lacerda-body-b96/validation.json').read_text());protected={r['object']:sig(scene.objects[r['object']]) for r in prior['mesh_checks']}
states={o.name:(o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);z=cfg['levels']['upper_walkable'];up=[Vector(v) for v in cfg['polygons']['upper_floor']['points_local']]
width=.18;height=1.10
def cross(a,b):return a.x*b.y-a.y*b.x
def outline(path):
 a,b,c=path;d=(b-a).normalized();e=(c-b).normalized();n=Vector((d.y,-d.x));m=Vector((e.y,-e.x));p=b+n*width;q=b+m*width
 corner=p+d*(cross(q-p,e)/cross(d,e))
 return [a,b,c,c+m*width,corner,a+n*width]
def stats(data):
 bm=bmesh.new();bm.from_mesh(data);q={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0 and q['volume']>0,q
 return q
plans=[]
for label,indices in [('saída',(1,2,3)),('entrada',(6,7,8))]:
 path=[up[i] for i in indices];p=outline(path);count=len(p);name=f'B97 | acesso superior | guarda {label}'
 assert name not in bpy.data.objects
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([(v.x,v.y,lev) for lev in (z,z+height) for v in p],[],[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)])
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
 mesh.materials.append(scene.objects['B94 | saguão passarela | retorno norte | peitoril'].data.materials[0])
 plans.append((name,mesh,path,p,stats(mesh)))
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'terrain_signature':terrain,'proxy_signatures':proxy,'preserved_signatures':protected,'protected_object_count':len(states),'controls':{'source_id':'source:lacerda-issue22-sucop-17','document_note':'DEMOLIR FECHAMENTO EM ALVENARIA — MANTER GUARDA-CORPO','paths':{n:[list(v) for v in path] for n,_,path,_,_ in plans},'section_height_m':height,'section_thickness_m':width,'section_status':'APPROXIMATE_NOT_DOCUMENT_DIMENSION','placement_status':'DOCUMENT_RELATIVE_CONTOUR','existing_east_accesses':'INTENTIONALLY_OPEN','collision_enabled':False}}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
added=[];collection=scene.objects['SUPERIOR | piso saguão'].users_collection[0]
for name,mesh,path,p,q in plans:
 o=bpy.data.objects.new(name,mesh);collection.objects.link(o);o.matrix_world=M
 for k,v in {'boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','status':'GAMEPLAY_PROXY','accuracy':'APPROXIMATE','replacement_required':True,'boas_production_ready':False,'boas_generated_revision':'R30B.97','boas_provenance_ids':json.dumps(['derived:lacerda-upper-vestibules-b97']),'boas_pending_gate':'LACERDA_ARCHITECTURAL_REGISTRATION / guarda-corpo seção e as-built','boas_collision_enabled':False,'boas_source_object':'SUPERIOR | piso saguão'}.items():o[k]=v
 added.append({'object':name,'after':{'signature':sig(o)},'mesh':q,'outline_local':[list(v) for v in p]})
for n,state in states.items():
 o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert all(sig(scene.objects[n])==s for n,s in protected.items())
assert all(sig(bpy.data.objects[n])==s for n,s in proxy.items()) and sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain
scene['lacerda_revision']='R30B.97 | guardas candidatas nos vestíbulos; entradas livres';scene['boas_historic_movement_enabled']=False
r={**journal,'revision':'R30B.97','changes':[],'added':added,'invalidated_bindings':[],'reopened':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'production_ready':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text());entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':(out/'application.json').relative_to(root).as_posix(),'notes':'Guardas nos vestíbulos conforme limites da planta17; seção aproximada, sem promoção de fidelidade/controller.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'added':len(added),'preserved':len(states),'production_ready':False}))
