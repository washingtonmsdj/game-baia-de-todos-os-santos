"""Reconstrução delimitada do corpo superior; única sessão Blender visível."""
import bpy,bmesh,json,runpy,hashlib,os,shutil,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-upper-body-b100';scene=bpy.context.scene;base=Path(bpy.data.filepath)
before=json.loads((out/'before.json').read_text());cfg=json.loads((out/'controls.json').read_text());catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
assert base.name=='salvador_lacerda_r30b99_subsolos_corpo_cidade_alta.blend' and os.getpid()==before['pid'] and not before['session_geometry_delta']
with base.open('rb') as f:basehash=hashlib.file_digest(f,'sha256').hexdigest()
assert basehash==cat['authoring_source']['sha256']
dest=root/'blender/salvador_lacerda_r30b100_corpo_superior_cobertura.blend';assert not dest.exists() and shutil.disk_usage(root).free>base.stat().st_size*2
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
rows={r['object']:r for r in before['rows']};archive=cfg['archive'];groups=cfg['facade_transforms'];window_names={n for v in groups.values() for n in v['objects']};roofname='SUPERIOR | cobertura corpo elevado';changed_names=window_names|{roofname}
assert not (set(archive)&changed_names)
assert all(sig(scene.objects[n])==s for n,s in before['preserved_signatures'].items())
staging_orphans=[m for m in bpy.data.meshes if m.name=='B100 | cidade alta | corpo superior contínuo' and m.users==0]
if bpy.data.is_dirty:
 assert len(staging_orphans)==1 and not any(o.name.startswith('B100 |') for o in scene.objects) and not (out/'application.json').exists(),'Preservar edição pendente não identificada'
 (out/'staging-retry.json').write_text(json.dumps({'reason':'QA recusou faces internas das junções antes de aplicar qualquer objeto','all_616_original_signatures_intact':True,'discarded_unlinked_meshes':[m.name for m in staging_orphans]},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for m in staging_orphans:bpy.data.meshes.remove(m)
protected={o.name:(o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in changed_names|set(archive)}
preserved={n:s for n,s in before['preserved_signatures'].items() if n not in changed_names}
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects};terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==cfg['ssot_sha256']
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def polygon(p):
 q=[Vector(v) for v in p]
 if (q[0]-q[-1]).length<1e-7:q.pop()
 if area(q)<0:q.reverse()
 return q
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def inset(poly,t):
 q=[]
 for i,b in enumerate(poly):
  u=(b-poly[i-1]).normalized();v=(poly[(i+1)%len(poly)]-b).normalized();nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));p=b+nu*t;r=b+nv*t;cross=u.x*v.y-u.y*v.x
  q.append(b+(nu+nv)*(.5*t) if abs(cross)<1e-7 else p+u*(((r-p).x*v.y-(r-p).y*v.x)/cross))
 assert area(q)>0 and all(inside(p,poly) for p in q)
 return q
def triangulate(outer,holes=()):
 points=[];edges=[];loops=[]
 for loop in [outer]+list(holes):
  start=len(points);points.extend(loop);ix=list(range(start,len(points)));loops.append(ix);edges.extend((v,ix[(j+1)%len(ix)]) for j,v in enumerate(ix))
 result=delaunay_2d_cdt(points,edges,[loops[0]],1,1e-7);p=list(result[0]);tri=[]
 for f in result[2]:
  center=sum((p[i] for i in f),Vector((0,0)))/len(f)
  if any(inside(center,v) for v in holes):continue
  tri.append(tuple(f) if area([p[i] for i in f])>0 else tuple(reversed(f)))
 expected=area(outer)-sum(abs(area(v)) for v in holes);actual=sum(area([p[i] for i in f]) for f in tri)
 assert abs(expected-actual)<.002,(expected,actual)
 counts={};directed={}
 for f in tri:
  for a,b in zip(f,f[1:]+f[:1]):key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1;directed[key]=(a,b)
 return p,tri,[directed[k] for k,c in counts.items() if c==1]
def extrude(poly,z0,z1):
 p,tri,border=triangulate(poly);n=len(p);verts=[(v.x,v.y,z) for z in (z0,z1) for v in p];faces=[]
 for f in tri:faces.extend([tuple(reversed(f)),tuple(i+n for i in f)])
 faces.extend((a,b,b+n,a+n) for a,b in border)
 return verts,faces
def quality(mesh,fuse=False):
 bm=bmesh.new();bm.from_mesh(mesh);removed=0
 if fuse:
  # Retirar ambos os tampões ANTES de soldar. Remove Doubles coalesce
  # faces duplicadas, deixando uma divisória interna se a ordem for invertida.
  pairs={}
  for f in bm.faces:pairs.setdefault(tuple(sorted(tuple(round(float(c),6) for c in v.co) for v in f.verts)),[]).append(f)
  delete=[]
  for fs in pairs.values():
   if len(fs)>1:assert len(fs)==2;delete.extend(fs)
  removed=len(delete);assert removed==16,('JOINT_CAPS',removed);bmesh.ops.delete(bm,geom=delete,context='FACES_ONLY')
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);mesh.update()
 q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True),'internal_joint_faces_removed':removed};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0 and q['volume']>0,q
 return q
material=scene.objects['SUPERIOR | lateral corpo elevado'].data.materials[0];roofmat=scene.objects[roofname].data.materials[0]
buffers=[]
def stage(name,verts,faces,mat,function,fuse=False):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);q=quality(mesh,fuse);buffers.append((name,mesh,q,function))
outer=polygon(cfg['body_contour_local']);inner=inset(outer,cfg['wall_thickness_candidate']);corners={k:Vector(v) for k,v in cfg['corners'].items()};openings=[]
z0=cfg['levels']['body_bottom'];z1=cfg['levels']['roof_bottom'];verts=[];faces=[]
for i,a in enumerate(outer):
 b=outer[(i+1)%len(outer)];ai=inner[i];bi=inner[(i+1)%len(inner)];u=(b-a).normalized();length=(b-a).length
 facade=next((key for key,start,end in [('FRONT','SE','NE'),('SOUTH','SW','SE'),('NORTH','NE','NW')] if (a-corners[start]).length<1e-5 and (b-corners[end]).length<1e-5),None)
 holes=[]
 for window in cfg['windows']:
  if window['facade']!=facade:continue
  p=[Vector(v) for v in window['vertices_local_after']];positions=[(Vector((v.x,v.y))-a).dot(u)/length for v in p];margin=window['opening_margin_candidate'];lo=min(positions)-margin/length;hi=max(positions)+margin/length;bottom=min(v.z for v in p)-margin;top=max(v.z for v in p)+margin
  assert 0<lo<hi<1 and z0<bottom<top<z1,(window['object'],lo,hi,bottom,top)
  holes.append([Vector((lo,bottom)),Vector((hi,bottom)),Vector((hi,top)),Vector((lo,top))]);openings.append({'window':window['object'],'edge':i,'u':[lo,hi],'z':[bottom,top],'margin_candidate':margin})
 flat,tri,border=triangulate([Vector((0,z0)),Vector((1,z0)),Vector((1,z1)),Vector((0,z1))],holes);n=len(flat);offset=len(verts)
 for aa,bb in ((a,b),(ai,bi)):
  for p in flat:
   xy=aa if p.x==0 else bb if p.x==1 else aa.lerp(bb,p.x);verts.append((xy.x,xy.y,p.y))
 for f in tri:faces.extend([tuple(offset+j for j in reversed(f)),tuple(offset+n+j for j in f)])
 faces.extend((offset+a0,offset+b0,offset+n+b0,offset+n+a0) for a0,b0 in border)
assert len(openings)==18
stage('B100 | cidade alta | corpo superior contínuo',verts,faces,material,'UPPER_BODY_WITH_CANDIDATE_EXISTING_WINDOW_APERTURES',True)
rp=polygon(cfg['roof_contour_local']);roofverts,rooffaces=extrude(rp,cfg['levels']['roof_bottom'],cfg['levels']['roof_top'])
roofmesh=bpy.data.meshes.new('B100 | cobertura corpo elevado');roof_local=wm(scene.objects[roofname]).inverted()@M
roofmesh.from_pydata([tuple(roof_local@Vector(p)) for p in roofverts],[],rooffaces)
for m in scene.objects[roofname].data.materials:roofmesh.materials.append(m)
roofquality=quality(roofmesh)
pi=polygon(cfg['parapet_inner_local']);n=len(rp);vertices=[(p.x,p.y,z) for z in (cfg['levels']['roof_top'],cfg['levels']['parapet_top']) for loop in (rp,pi) for p in loop];faces=[]
for i in range(n):
 j=(i+1)%n;faces.extend([(i,j,j+2*n,i+2*n),(i+n,i+3*n,j+3*n,j+n),(i,i+n,j+n,j),(i+2*n,j+2*n,j+3*n,i+3*n)])
stage('B100 | cidade alta | platibanda contorno completo',vertices,faces,material,'DOCUMENT_ROOF_PERIMETER')
boundary=[Vector(p) for p in cfg['floor_admin_boundary']];a,b=boundary;v=(b-a).normalized();normal=Vector((-v.y,v.x))
if normal.x<0:normal=-normal
floor=[]
for start,end in zip(inner,inner[1:]+inner[:1]):
 ds=(start-a).dot(normal);de=(end-a).dot(normal)
 if ds>=0:floor.append(start)
 if (ds>=0)!=(de>=0):floor.append(start.lerp(end,ds/(ds-de)))
assert area(floor)>40 and all(p.x>min(x[0] for x in cfg['floor_admin_boundary'])-.05 for p in floor)
for label,key in [('01','floor1'),('02','floor2')]:
 level=cfg['levels'][key];v,f=extrude(floor,level-cfg['levels']['slab_thickness_candidate'],level);stage('B100 | cidade alta | laje administrativa '+label,v,f,roofmat,'DOCUMENT_FLOOR_LEVEL_ADMIN_AREA_CANDIDATE_CONTOUR')
# Reconciliação rígida das esquadrias: sem alteração de dimensão/topologia.
window_meshes={};window_stats={}
for group,control in groups.items():
 R=control['rotation'];t=control['translation']
 for name in control['objects']:
  o=scene.objects[name];assert not o.constraints and not o.animation_data
  row=rows[name];shift=cfg['second_window_row_shift'] if sum(row['bounds'][2])/2>70.12300872802734+8 else 0.
  trans=wm(o).inverted()@M;mesh=o.data.copy();mesh.name='B100 | '+name
  for v,p in zip(mesh.vertices,row['vertices_local']):v.co=trans@Vector((R[0][0]*p[0]+R[0][1]*p[1]+t[0],R[1][0]*p[0]+R[1][1]*p[1]+t[1],p[2]+shift))
  q=quality(mesh);window_meshes[name]=mesh;window_stats[name]={'mesh':q,'facade':group,'rigid_z_shift':shift}
journal={'file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':basehash,'pid':os.getpid(),'scene':scene.name,'ssot_sha256':ssot,'controls_file':(out/'controls.json').relative_to(root).as_posix(),'preserved_signatures':preserved,'terrain_signature':terrain,'proxy_signatures':proxy,'protected_object_count':len(protected),'planned_archive':archive,'planned_changes':sorted(changed_names),'window_openings':openings,'floor_outline_local':[list(p) for p in floor]}
(out/'mutation-journal.json').write_text(json.dumps(journal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
changes=[]
for name,mesh in {**window_meshes,roofname:roofmesh}.items():
 o=scene.objects[name];old=sig(o);o.data.use_fake_user=True;o.data=mesh;o['boas_generated_revision']='R30B.100';o['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-body-b100']);o['accuracy']='DOCUMENT_RELATIVE_CONTOUR_LEGACY_WINDOW_LAYOUT_CANDIDATE_SECTION';o['replacement_required']=True;o['boas_production_ready']=False
 changes.append({'object':name,'before':{'signature':old,'bounds':rows[name]['bounds']},'after':{'signature':sig(o)},**window_stats.get(name,{'mesh':roofquality,'function':'DOCUMENT_ROOF_CONTOUR'})})
collection=scene.objects[roofname].users_collection[0];added=[]
for name,mesh,q,function in buffers:
 assert name not in bpy.data.objects
 o=bpy.data.objects.new(name,mesh);collection.objects.link(o);o.matrix_world=M
 for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_generated_revision':'R30B.100','boas_provenance_ids':json.dumps(['derived:lacerda-upper-body-b100']),'boas_function':function,'boas_source_control':journal['controls_file'],'accuracy':'DOCUMENT_RELATIVE_MAJOR_CONTOUR_LEGACY_WINDOW_LAYOUT_CANDIDATE_SECTION','replacement_required':True,'boas_production_ready':False,'boas_collision_enabled':False}.items():o[k]=v
 added.append({'object':name,'after':{'signature':sig(o)},'mesh':q,'function':function})
archived=[]
for name in archive:
 o=scene.objects[name];o.hide_set(True);o.hide_render=True;o['boas_active_authoring']=False;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_archive_revision']='R30B.100';o['boas_replaced_by']=journal['controls_file'];assert sig(o)==before['preserved_signatures'][name]
 archived.append({'object':name,'before':before['preserved_signatures'][name],'after_signature':sig(o),'reason':'Envelope/coroamento retangular legado ou janelas na antiga divisão interna; preservação integral'})
for name,state in protected.items():
 o=scene.objects[name];assert (o.data.as_pointer() if o.data else None,[list(v) for v in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,name
assert all(sig(scene.objects[n])==s for n,s in preserved.items()) and all(sig(bpy.data.objects[n])==s for n,s in proxy.items()) and sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json';profile=json.loads(profilepath.read_text());invalidated=[]
for binding in profile['collision_bindings']:
 if binding.get('source_object',binding.get('source')) in set(archive)|changed_names:
  binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_UPPER_BODY_B100';invalidated.append(binding['object'])
scene['lacerda_revision']='R30B.100 | corpo superior, cobertura e pavimentos documentais';scene['boas_historic_movement_enabled']=False
r={**journal,'revision':'R30B.100','changes':changes,'added':added,'archived':archived,'invalidated_bindings':invalidated,'reopened':False,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'production_ready':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.100','scope':'Corpo superior/cobertura/reconciliação rígida das esquadrias; pisos+4,94/+9,42; instalação histórica bloqueada','movement_enabled':False,'evidence':(out/'application.json').relative_to(root).as_posix()});profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':r['file'],'revision':r['revision'],'parent_file':r['parent_file'],'sha256':r['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':(out/'application.json').relative_to(root).as_posix(),'notes':'Contornos18/19/20 e níveis23; alas técnicas e cobertura reconciliadas, janelas rígidas/candidatas, instalação intacta.'};cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'sha256':r['sha256'],'changed':len(changes),'added':len(added),'archived':len(archived),'preserved':len(preserved)},ensure_ascii=False))
