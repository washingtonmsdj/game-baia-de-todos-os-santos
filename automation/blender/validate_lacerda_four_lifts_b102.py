"""CCD exato de translação vertical por caixa varrida; não certifica instalação."""
import bpy,bmesh,json,math,runpy,sys
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
sys.path.insert(0,str(root/'tools/world'));from lacerda_four_lifts import verify_lift
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
r=json.loads((out/'application.json').read_text());contractpath=root/'world/areas/mvp-centro-lacerda/lacerda-four-lifts.json';cfg=json.loads(contractpath.read_text());scene=bpy.context.scene
for n,s in r['preserved_signatures'].items():assert sig(scene.objects[n])==s,n
assert all(sig(bpy.data.objects[n])==s for n,s in r['proxy_b82_signatures'].items())
checks=[]
for row in r['added']:
 o=scene.objects[row['object']];bm=bmesh.new();bm.from_mesh(o.data)
 q={'object':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),
    'inconsistent_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_edges']==0,q;checks.append(q)

def intersection(tri,half):
 # SAT triângulo × AABB. Retorna penetração mínima nos eixos normalizados.
 edges=[tri[1]-tri[0],tri[2]-tri[1],tri[0]-tri[2]];units=[Vector((1.,0.,0.)),Vector((0.,1.,0.)),Vector((0.,0.,1.))]
 axes=units+[edges[0].cross(edges[1])]+[e.cross(u) for e in edges for u in units];penetration=1e9
 for axis in axes:
  if axis.length_squared<1e-14:continue
  axis.normalize();values=[v.dot(axis) for v in tri];extent=sum(abs(axis[i])*half[i] for i in range(3))
  gap=min(max(values),extent)-max(min(values),-extent)
  if gap< -1e-5:return None
  # Espessura zero do triângulo pede distância à face da caixa, e não largura
  # do intervalo do triângulo (sempre zero no seu próprio eixo normal).
  overlap=min(extent-min(values),max(values)+extent);penetration=min(penetration,overlap)
 return penetration

static=[]
for o in scene.objects:
 if o.type!='MESH' or not o.visible_get() or o.get('status')=='GAMEPLAY_PROXY':continue
 if o.get('boas_role') in ('SUPERSEDED_REFERENCE','HISTORICAL_INSTALLATION_REFERENCE','RENDER_ONLY'):continue
 if any('COLLISION' in c.name for c in o.users_collection) and o.get('boas_physical_enabled') is False:continue
 trans=inv@wm(o);p=[trans@v.co for v in o.data.vertices]
 if not p:continue
 b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 if b[0][1]<-55 or b[0][0]>-10 or b[1][1]<-10 or b[1][0]>12 or b[2][1]<10 or b[2][0]>74:continue
 o.data.calc_loop_triangles();static.append((o.name,p,[tuple(t.vertices) for t in o.data.loop_triangles],b))
results=[]
for s in cfg['equipment']:
 a=s['angle_local'];ca,sa=math.cos(a),math.sin(a);cx,cy=s['center_local']
 centerz=(s['lower']-.12+s['upper']+2.62)/2;enclosure=s.get('enclosure_size',[2.12,2.47,2.74]);half=Vector((enclosure[0]/2,enclosure[1]/2,(s['upper']+2.62-s['lower']+.12)/2))
 hits={};contacts={};tested=0
 for name,points,faces,bounds in static:
  p=[Vector((ca*(v.x-cx)+sa*(v.y-cy),-sa*(v.x-cx)+ca*(v.y-cy),v.z-centerz)) for v in points]
  b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
  if any(b[i][1]<-half[i]-1e-5 or b[i][0]>half[i]+1e-5 for i in range(3)):continue
  for face in faces:
   tri=[p[i] for i in face]
   if any(max(v[i] for v in tri)<-half[i]-1e-5 or min(v[i] for v in tri)>half[i]+1e-5 for i in range(3)):continue
   tested+=1;depth=intersection(tri,half)
   if depth is None:continue
   target=hits if depth>1e-4 else contacts
   target.setdefault(name,[]).append({'triangle':list(face),'min_penetration_m':depth,'z_range':[min(v.z for v in tri)+centerz,max(v.z for v in tri)+centerz]})
  if name in hits:hits[name]=sorted(hits[name],key=lambda h:-h['min_penetration_m'])[:3]
  if name in contacts:contacts[name]=contacts[name][:3]
 s['clearance_status']='SOLID_INTERSECTION' if hits else ('CONTACT_NEEDS_REVIEW' if contacts else 'CABIN_VOLUME_CCD_CLEAR')
 s['movement_enabled']=not hits and not contacts
 state=verify_lift(s) if s['movement_enabled'] else {'status':'DISABLED_BY_GEOMETRY_GATE'}
 results.append({'id':s['id'],'tower':s['tower'],'status':s['clearance_status'],'movement_enabled':s['movement_enabled'],
   'triangles_narrow_phase':tested,'solid_hits':hits,'contacts':contacts,'controller':state,
   'method':'SAT triangle vs exact swept cabin OBB; fixed orientation, monotonic vertical segment, full enclosure rather than center rays',
   'not_proven':['soleiras/portal pedonal','rota completa de personagem','dimensões instaladas','folgas regulamentares']})
cfg['validation_report']='docs/reports/blender/lacerda-exterior-b102/validation.json'
contractpath.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
v={'revision':'R30B.102','file':bpy.data.filepath,'mesh_checks':checks,'preserved_components':len(r['preserved_signatures']),
 'equipment':results,'historical_movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','production_ready':False,
 'scene_is_visible_session':True,'reopened':False,'pedestrian_route':'NOT_VALIDATED_FOR_FOUR_LIFTS'}
(out/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'meshes':len(checks),'equipment':[{'id':v['id'],'status':v['status'],'solid_objects':list(v['solid_hits']),'contacts':list(v['contacts'])} for v in results]},ensure_ascii=False))
