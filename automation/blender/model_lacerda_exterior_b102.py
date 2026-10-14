"""Corrige resíduos e completa corpo exterior; quatro cabines em camada proxy."""
import bpy,bmesh,json,runpy,os,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
before=json.loads((out/'before.json').read_text());cfg=json.loads((out/'controls.json').read_text());scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b101_pavimentos_estruturais.blend'
assert not bpy.data.is_dirty and os.getpid()==before['pid'] and not before['session_geometry_delta']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
assert all(sig(scene.objects[n])==s for n,s in before['preserved_signatures'].items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==cfg['ssot_sha256']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
archive=[r['object'] for r in cfg['archive']]
protected={o.name:sig(o) for o in scene.objects if o.type=='MESH'}
terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
proxy={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
col=bpy.data.collections.new('HERO | Lacerda | corpo exterior B102');scene.collection.children.link(col)
gcol=bpy.data.collections.new('GAMEPLAY_PROXY | Lacerda | quatro equipamentos B102');scene.collection.children.link(gcol)
gcol['status']='GAMEPLAY_PROXY';gcol['accuracy']='APPROXIMATE';gcol['replacement_required']=True
material=scene.objects['CASCA | parede lateral'].data.materials[0]
door_mat=bpy.data.materials.new('B102 | portas dos equipamentos proxy');door_mat.diffuse_color=(.20,.28,.30,1.)
staged=[];added=[]
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def poly(raw):
 p=[Vector(v) for v in raw]
 if area(p)<0:p.reverse()
 return p
def offset(p,t):
 result=[]
 for i,b in enumerate(p):
  u=(b-p[i-1]).normalized();v=(p[(i+1)%len(p)]-b).normalized();nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));cross=u.x*v.y-u.y*v.x
  if abs(cross)<1e-7:r=b+(nu+nv)*(.5*t)
  else:
   d=(nv-nu)*t;r=b+nu*t+u*((d.x*v.y-d.y*v.x)/cross)
  result.append(r)
 return result
def stage(name,verts,faces,role,source,collection=col,mat=material):
 assert name not in bpy.data.objects
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh)
 q={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),
    'inconsistent_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_edges']==0 and q['volume']>1e-8,(name,q)
 mesh.update();staged.append((name,mesh,q,role,source,collection));return name
def ring(name,outer,inner,z0,z1,role,source):
 n=len(outer);vs=[(p.x,p.y,z) for z in (z0,z1) for loop in (outer,inner) for p in loop];fs=[]
 for i in range(n):
  j=(i+1)%n;fs.extend([(i,j,j+2*n,i+2*n),(i+n,i+3*n,j+3*n,j+n),(i,i+n,j+n,j),(i+2*n,j+2*n,j+3*n,i+3*n)])
 return stage(name,vs,fs,role,source)
def wall_path(name,points,z0,z1,t,source):
 # Miter único, sem caixas/faces internas sobrepostas em cada quina.
 p=[Vector(v) for v in points];left=[];right=[]
 for i,b in enumerate(p):
  u=(p[1]-b).normalized() if i==0 else (b-p[i-1]).normalized()
  v=u if i==len(p)-1 else (p[i+1]-b).normalized();nu=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));direction=(nu+nv).normalized()
  distance=t*.5/max(.15,direction.dot(nu));left.append(b+direction*distance);right.append(b-direction*distance)
 outline=left+list(reversed(right));n=len(outline)
 from mathutils.geometry import tessellate_polygon
 ids={tuple(v):i for i,v in enumerate(outline)};fs=[]
 for tri in tessellate_polygon([[Vector((v.x,v.y,0.)) for v in outline]]):
  ix=[v if isinstance(v,int) else ids[(v.x,v.y)] for v in tri];fs.extend([tuple(reversed(ix)),tuple(i+n for i in ix)])
 fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 return stage(name,[(v.x,v.y,z) for z in (z0,z1) for v in outline],fs,'ARCHITECTURAL_RETAINING_INTERFACE_CANDIDATE',source)
for r in cfg['rooms']:
 inner=poly(r['inner_floor_outline']);outer=offset(inner,-r['wall_thickness_candidate'])
 ring('B102 | cidade alta | corpo sala técnica '+r['id'],outer,inner,r['bottom_z'],r['top_z'],'ARCHITECTURAL_MODEL_CANDIDATE',r['source'])
 # A cobertura é o prolongamento da laje do nível documental superior.
 n=len(outer);verts=[(v.x,v.y,z) for z in (r['top_z'],r['top_z']+.25) for v in outer]
 stage('B102 | cidade alta | cobertura sala técnica '+r['id'],verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ARCHITECTURAL_MODEL_CANDIDATE',r['source'])
for r in cfg['retaining_paths']:
 wall_path('B102 | cidade alta | contenção '+r['id'],r['points_local'],r['bottom_z'],r['top_z'],r['wall_thickness_candidate'],'SUCOP14 curvas'+str(r['curve_ids'])+'; seção23; extensão vertical candidata')

# Dois equipamentos por torre; dimensões de gameplay, não levantamento Otis.
fc=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
zupper=fc['levels']['upper_walkable'];zlower=zupper-59.01;specs=[]
for number,y in ((1,-1.25),(2,2.05)):
 specs.append({'id':f'lacerda-{number:02}','number':number,'tower':'CIDADE_ALTA','center_local':[-14.4,y], 'angle_local':0.,'size':[2.,2.35,2.5],'upper_side':-1,'lower_side':-1})
a=fc['new_tower_basis']['angle'];c=fc['new_tower_basis']['center_local']
for number,y in ((3,-1.85),(4,1.85)):
 specs.append({'id':f'lacerda-{number:02}','number':number,'tower':'CIDADE_BAIXA','center_local':[c[0]-math.sin(a)*y,c[1]+math.cos(a)*y],
 'angle_local':a,'size':[2.,2.35,2.5],'upper_side':1,'lower_side':-1})
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,center,size,spec,tag,landing=None,leaf=None):
 ca,sa=math.cos(spec['angle_local']),math.sin(spec['angle_local']);cx,cy=spec['center_local'];vs=[]
 for z in (-size[2]/2,size[2]/2):
  for x,y in ((-size[0]/2,-size[1]/2),(size[0]/2,-size[1]/2),(size[0]/2,size[1]/2),(-size[0]/2,size[1]/2)):
   x+=center[0];y+=center[1];vs.append((cx+ca*x-sa*y,cy+sa*x+ca*y,z+center[2]+(zupper if tag.startswith('cabin') else 0.)))
 stage(name,vs,faces,'DYNAMIC_CABIN' if tag.startswith('cabin') else 'DYNAMIC_DOOR',spec['id'],gcol,door_mat)
 spec.setdefault('parts',[]).append({'object':name,'tag':tag,'center':center,'size':size,'landing':landing,'leaf':leaf})
for s in specs:
 s.update(upper=zupper,lower=zlower,status='GAMEPLAY_PROXY',accuracy='APPROXIMATE',replacement_required=True,production_ready=False,
          clearance_status='NOT_YET_TESTED',movement_enabled=False,door_width=1.3)
 prefix='B102 | '+s['id']+' | '
 box(prefix+'piso',[0,0,-.06],[2.12,2.47,.12],s,'cabin_floor')
 box(prefix+'teto',[0,0,2.56],[2.12,2.47,.12],s,'cabin_roof')
 for side in (-1,1):box(prefix+'lateral '+str(side),[0,side*1.205,1.25],[2.12,.06,2.5],s,'cabin_wall')
 for side in (-1,1):
  if side not in (s['upper_side'],s['lower_side']):box(prefix+'fundo',[side*1.03,0,1.25],[.06,2.47,2.5],s,'cabin_wall')
  else:
   for sy in (-1,1):box(prefix+'jamba '+str(side)+' '+str(sy),[side*1.03,sy*.925,1.25],[.06,.55,2.5],s,'cabin_wall')
   for leaf in (-1,1):box(prefix+'porta cabine '+str(side)+' '+str(leaf),[side,leaf*.325,1.25],[.05,.65,2.5],s,'cabin_door',str(side),leaf)
 for landing,z in (('upper',zupper),('lower',zlower)):
  side=s[landing+'_side']
  for leaf in (-1,1):box(prefix+'porta estação '+landing+' '+str(leaf),[side*1.12,leaf*.325,z+1.25],[.06,.65,2.5],s,'landing_door',landing,leaf)
for name,mesh,q,role,source,collection in staged:
 o=bpy.data.objects.new(name,mesh);collection.objects.link(o);o.matrix_world=M
 for k,v in {'boas_location_id':'elevador-lacerda','boas_role':role,'boas_generated_revision':'R30B.102','boas_provenance_ids':json.dumps(['derived:lacerda-exterior-four-lifts-b102']),
    'accuracy':'APPROXIMATE' if collection==gcol else 'DOCUMENT_XY_CANDIDATE_VERTICAL_ENVELOPE','replacement_required':True,'boas_production_ready':False,
    'boas_source_control':'docs/reports/blender/lacerda-exterior-b102/controls.json','boas_source_component':source,
    'boas_vertical_gate':'BLOCKED_EXTERNAL_EVIDENCE','boas_historic_movement_enabled':False}.items():o[k]=v
 if collection==gcol:o['status']='GAMEPLAY_PROXY';o['boas_equipment_id']=source
 added.append({'object':name,'after':{'signature':sig(o)},'mesh':q,'role':role,'source':source})
for r in cfg['archive']:
 o=scene.objects[r['object']];assert sig(o)==r['signature'];o.hide_set(True);o.hide_render=True
 o['boas_role']='SUPERSEDED_REFERENCE';o['boas_active_authoring']=False;o['boas_archive_revision']='R30B.102';o['boas_archive_reason']=r['reason']
for n,s in protected.items():assert sig(scene.objects[n])==s,n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain
assert all(sig(bpy.data.objects[n])==s for n,s in proxy.items())
r={'revision':'R30B.102','parent_file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':scene.name,'pid':os.getpid(),
 'ssot_sha256':cfg['ssot_sha256'],'preserved_signatures':protected,'terrain_signature':terrain,'proxy_b82_signatures':proxy,
 'changes':[],'added':added,'archived':cfg['archive'],'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,
 'production_ready':False,'saved':False,'reopened':False}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
contract={'schema':'boas/four-lifts-gameplay-v1','scene':scene.name,'status':'GAMEPLAY_PROXY','historical_gate':'docs/LACERDA_CORRIDOR_B80.md',
 'ssot':'world/geographic-reference.json','accuracy':'APPROXIMATE','replacement_required':True,'production_ready':False,
 'pedestrian_route_status':'NOT_INTEGRATED_WITH_FOUR_LIFTS','equipment':specs}
(root/'world/areas/mvp-centro-lacerda/lacerda-four-lifts.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'added':len(added),'archived':archive,'four_lifts':'STAGED_NOT_YET_CCD_APPROVED','saved':False},ensure_ascii=False))
