"""B99: envoltória dos subsolos documentais, na única janela visível.

Preserva o núcleo existente. Seção e continuidade vertical são massing
candidata; não constituem projeto de instalação ou registro absoluto.
"""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import tessellate_polygon

root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;base=Path(bpy.data.filepath)
out=root/'docs/reports/blender/lacerda-structure-b99'
before=json.loads((out/'before.json').read_text());cfg=json.loads((out/'controls.json').read_text())
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
assert base.name=='salvador_lacerda_r30b98_frente_superior_reconciliada.blend'
assert os.getpid()==before['pid'] and scene.name==before['scene'] and not bpy.data.is_dirty
with base.open('rb') as f:base_hash=hashlib.file_digest(f,'sha256').hexdigest()
assert base_hash==cat['authoring_source']['sha256'] and not before['session_geometry_delta']
dest=root/'blender/salvador_lacerda_r30b99_subsolos_corpo_cidade_alta.blend'
assert not dest.exists() and shutil.disk_usage(root).free>base.stat().st_size*2
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
preserved=before['preserved_signatures']
assert all(sig(scene.objects[n])==s for n,s in preserved.items())
archive='B88 | cidade alta | alas estruturais sob edifício';legacy=scene.objects[archive]
assert not legacy.animation_data and not legacy.constraints
protected={o.name:(o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name!=archive}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']

def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def polygon(raw):
 p=[Vector(v) for v in raw]
 if (p[0]-p[-1]).length<1e-7:p.pop()
 assert min((a-b).length for a,b in zip(p,p[1:]+p[:1]))>1e-5
 if area(p)<0:p.reverse()
 return p
def inset(poly,t):
 q=[]
 for i,b in enumerate(poly):
  u=(b-poly[i-1]).normalized();v=(poly[(i+1)%len(poly)]-b).normalized()
  nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));p=b+nu*t;r=b+nv*t;cross=u.x*v.y-u.y*v.x
  if abs(cross)<1e-7:q.append(b+(nu+nv)*(.5*t))
  else:
   d=r-p;q.append(p+u*((d.x*v.y-d.y*v.x)/cross))
 assert min((a-b).length for a,b in zip(q,q[1:]+q[:1]))>1e-5 and area(q)>0
 return q
def quality(mesh):
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh)
 q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0 and q['volume']>0,q
 mesh.update();return q
buffers=[];material=legacy.data.materials[0]
def stage(name,verts,faces,kind,outline,zrange,expected_volume):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(material);q=quality(mesh)
 assert abs(q['volume']-expected_volume)<.005,(name,q['volume'],expected_volume)
 buffers.append((name,mesh,q,kind,outline,zrange))

outer=polygon(cfg['contour_local']);inner=inset(outer,cfg['wall_thickness_candidate']);n=len(outer)
z0=cfg['levels']['floor_subsolo02'];z1=cfg['levels']['upper_floor_underside']
verts=[(p.x,p.y,z) for z in (z0,z1) for loop in (outer,inner) for p in loop];faces=[]
for i in range(n):
 j=(i+1)%n
 faces.extend([(i,j,j+2*n,i+2*n),(i+n,i+3*n,j+3*n,j+n),(i,i+n,j+n,j),(i+2*n,j+2*n,j+3*n,i+3*n)])
stage('B99 | cidade alta | envoltória subsolos 15 16',verts,faces,'HOLLOW_BASEMENT_ENVELOPE',cfg['contour_local'],[z0,z1],(area(outer)-area(inner))*(z1-z0))
floor=polygon(cfg['floor16_local']);n=len(floor);zf=cfg['levels']['floor_subsolo01'];th=cfg['levels']['slab_thickness_candidate'];ids={tuple(v):i for i,v in enumerate(floor)};faces=[]
for tri in tessellate_polygon([[Vector((p.x,p.y,0.)) for p in floor]]):
 ix=[v if isinstance(v,int) else ids[(v.x,v.y)] for v in tri];faces.extend([tuple(reversed(ix)),tuple(i+n for i in ix)])
faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
stage('B99 | cidade alta | laje subsolo 01 área documentada',[(p.x,p.y,z) for z in (zf-th,zf) for p in floor],faces,'DOCUMENTED_FLOOR_EXCLUDING_HATCHED_CORE',cfg['floor16_local'],[zf-th,zf],area(floor)*th)
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':base_hash,'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'controls_file':(out/'controls.json').relative_to(root).as_posix(),'preserved_signatures':preserved,'terrain_signature':terrain,'proxy_signatures':proxy,'protected_object_count':len(protected),'planned_archive':[archive]}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
added=[];collection=legacy.users_collection[0]
for name,mesh,q,kind,outline,levels in buffers:
 assert name not in bpy.data.objects
 o=bpy.data.objects.new(name,mesh);collection.objects.link(o);o.matrix_world=M
 for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.99','boas_provenance_ids':json.dumps(['derived:lacerda-basement-envelope-b99']),'boas_function':kind,'boas_source_control':'docs/reports/blender/lacerda-structure-b99/controls.json','accuracy':'DOCUMENT_RELATIVE_CONTOUR_APPROXIMATE_SECTION_AND_LOWER_EXTRUSION','replacement_required':True,'boas_production_ready':False,'boas_collision_enabled':False,'boas_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE'}.items():o[k]=v
 added.append({'object':name,'after':{'signature':sig(o)},'mesh':q,'outline_local':outline,'levels':levels,'function':kind})
legacy.hide_set(True);legacy.hide_render=True;legacy['boas_active_authoring']=False;legacy['boas_role']='SUPERSEDED_REFERENCE';legacy['boas_archive_revision']='R30B.99';legacy['boas_replaced_by']=journal['controls_file']
archived=[{'object':archive,'before':preserved[archive],'after_signature':sig(legacy),'operation':'PRESERVE_SUPERSEDED_REFERENCE','reason':'Solid rectangle inherited from upper floor instead of stepped basement contour'}]
for name,state in protected.items():
 o=scene.objects[name];assert (o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,name
assert all(sig(scene.objects[n])==s for n,s in preserved.items()) and all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for b in profile['collision_bindings']:
 if b.get('source_object',b.get('source'))==archive:
  b['enabled']=False;b['validation_status']='INVALIDATED_BY_BASEMENT_B99';invalidated.append(b['object'])
scene['lacerda_revision']='R30B.99 | contorno dos subsolos e corpo da Cidade Alta';scene['boas_historic_movement_enabled']=False
r={**journal,'revision':'R30B.99','changes':[],'added':added,'archived':archived,'invalidated_bindings':invalidated,'reopened':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'production_ready':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.99','scope':'Envoltória dos subsolos; núcleo antigo intacto, seções candidatas; sem aprovação da instalação','movement_enabled':False,'evidence':(out/'application.json').relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':(out/'application.json').relative_to(root).as_posix(),'notes':'Subsolos SUCOP15/16, níveis23; contorno relativo, seção e extrapolação vertical candidatas; núcleo preservado.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'added':len(added),'archived_preserved':len(archived),'existing_geometry_changed':0},ensure_ascii=False))
