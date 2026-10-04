"""Conferência geométrica das folhas e amostragem de abertura, sem alterar a fonte salva."""
import bpy,bmesh,collections,hashlib,json,math,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
before=json.loads((r/'artifacts/vehicles/rondesp/v18-doors-before.json').read_text(encoding='utf8'))
body=s.objects['HILUX | CARROCERIA PRINCIPAL']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
def mesh_review(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
 result={'vertices':len(bm.verts),'faces':len(bm.faces),
  'multi_edges':sum(len(e.link_faces)>2 for e in bm.edges),
  'wire_edges':sum(not e.link_faces for e in bm.edges),
  'tiny_faces':sum(f.calc_area()<1e-10 for f in bm.faces),
  'inconsistent_winding':sum(len(e.link_faces)==2 and not e.is_contiguous for e in bm.edges),
  'boundary_edges':sum(e.is_boundary for e in bm.edges)}
 bm.free();return result
def triangles(ob,evaluated=False):
 eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else ob
 mesh=eo.to_mesh() if evaluated else eo.data
 mesh.calc_loop_triangles();vs=[eo.matrix_world@v.co for v in mesh.vertices]
 ts=[tuple(t.vertices) for t in mesh.loop_triangles];ids=[t.polygon_index for t in mesh.loop_triangles]
 if evaluated:eo.to_mesh_clear()
 return vs,ts,ids,BVHTree.FromPolygons(vs,ts,all_triangles=True,epsilon=0.)
def intersections(aa,bb,same=False):
 va,ta,fa,treea=aa;vb,tb,fb,treeb=bb
 hits=[];pairs=set()
 for ia,ib in treea.overlap(treeb):
  if same and (ia>=ib or fa[ia]==fb[ib] or set(ta[ia]).intersection(tb[ib])):continue
  pa=[va[i] for i in ta[ia]];pb=[vb[i] for i in tb[ib]]
  na=(pa[1]-pa[0]).cross(pa[2]-pa[0]).normalized();nb=(pb[1]-pb[0]).cross(pb[2]-pb[0]).normalized()
  da=[(p-pb[0]).dot(nb) for p in pa];db=[(p-pa[0]).dot(na) for p in pb]
  if min(da)>1e-7 or max(da)<-1e-7 or min(db)>1e-7 or max(db)<-1e-7:continue
  hit=None
  for tri,other in [(pa,pb),(pb,pa)]:
   for p,q in zip(tri,tri[1:]+tri[:1]):
    edge=q-p;point=intersect_ray_tri(*other,edge,p,True)
    if point is None or edge.length_squared<1e-14:continue
    t=(point-p).dot(edge)/edge.length_squared
    a,b,c=other;v0=b-a;v1=c-a;v2=point-a
    d00,d01,d11=v0.dot(v0),v0.dot(v1),v1.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-20:continue
    u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
    if 1e-6<t<1-1e-6 and min(u,v,1-u-v)>1e-6:hit=point;break
   if hit is not None:break
  if hit is None:continue
  pair=(fa[ia],fb[ib])
  if pair in pairs:continue
  pairs.add(pair);hits.append({'faces':list(pair),'point':list(hit)})
 return hits
shells=[s.objects[d['shell']] for d in report['door_assemblies']]
pivots=[s.objects[d['pivot']] for d in report['door_assemblies']]
angles=[p['abertura_graus'] for p in pivots]
reviews={o.name:mesh_review(o) for o in shells}
self_cross={o.name:intersections(triangles(o),triangles(o),True) for o in shells}
unchanged={name:fingerprint(s.objects[name])==sha for name,sha in before['protected_objects'].items()
 if name not in report['migrated_objects'] and name!=body.name}
audit={'body_unchanged':fingerprint(body)==before['body_hash'],'body_matches_authorized_change':fingerprint(body)==report['body_hash_after'],'protected_meshes_unchanged':all(unchanged.values()),
 'changed_unrelated_meshes':[n for n,v in unchanged.items() if not v],
 'mesh_reviews':reviews,'body_mesh_review':mesh_review(body),'self_intersections':self_cross,'movement_samples':[],
 'scope':'Malhas de portas; penetracao estrita de triangulos contra carroceria avaliada com Mirror e espessura. Ferragens de contato intencional excluidas. Amostragem angular, sem certificacao de varredura continua.'}
try:
 states=[('todas_'+str(a),[a]*4) for a in [0,2,5,10,20,35,50,65,70]]
 states+=[('dianteiras_abertas',[65,65,0,0]),('traseiras_inicio',[0,0,5,5]),('traseiras_abertas',[0,0,65,65]),('dianteiras_meia',[35,35,70,70])]
 for name,values in states:
  for p,angle in zip(pivots,values):p['abertura_graus']=float(angle);p.update_tag(refresh={'OBJECT'})
  s.frame_set(s.frame_current);bpy.context.view_layer.update()
  bt=triangles(body,True);dts=[triangles(o) for o in shells]
  sample={'pose':name,'angle_degrees':values,'doors':{},'door_pair_intersections':[]}
  for d,o,p,dt in zip(report['door_assemblies'],shells,pivots,dts):
   sample['doors'][o.name]={'rotation_z_degrees':math.degrees(p.rotation_euler.z),'body_intersections':intersections(dt,bt)}
  for i in range(len(shells)):
   for j in range(i+1,len(shells)):
    hit=intersections(dts[i],dts[j])
    if hit:sample['door_pair_intersections'].append({'objects':[shells[i].name,shells[j].name],'hits':hit})
  audit['movement_samples'].append(sample)
finally:
 for p,angle in zip(pivots,angles):p['abertura_graus']=angle;p.update_tag(refresh={'OBJECT'})
 s.frame_set(s.frame_current);bpy.context.view_layer.update()
audit['door_body_intersection_count']=sum(len(d['body_intersections']) for v in audit['movement_samples'] for d in v['doors'].values())
audit['door_pair_intersection_count']=sum(len(p['hits']) for v in audit['movement_samples'] for p in v['door_pair_intersections'])
sym={}
for label in ['dianteira','traseira']:
 a=s.objects[f'RDP01 | HILUX06 | Porta {label} -1'];b=s.objects[f'RDP01 | HILUX06 | Porta {label} 1']
 av=[a.matrix_world@v.co for v in a.data.vertices];bv=[b.matrix_world@v.co for v in b.data.vertices]
 sym[label]=max((Vector((-p.x,p.y,p.z))-q).length for p,q in zip(av,bv)) if len(av)==len(bv) else None
audit['mirror_vertex_difference_m']=sym
out=r/'artifacts/vehicles/rondesp/v18-doors-audit.json';out.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report['geometry_review']=audit;report['geometry_audit_file']=out.relative_to(r).as_posix()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'body_unchanged':audit['body_unchanged'],'protected_meshes_unchanged':audit['protected_meshes_unchanged'],
 'door_body_intersections':audit['door_body_intersection_count'],'door_pair_intersections':audit['door_pair_intersection_count'],
 'mesh_reviews':reviews,'self_intersections':{k:len(v) for k,v in self_cross.items()}}))
