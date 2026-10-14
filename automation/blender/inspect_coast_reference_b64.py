"""Inspeção da B64 reaberta, superfícies e percursos fonte; nenhuma mudança geométrica."""
import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from collections import Counter
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b64_costa_volumes_corrigidos.blend'
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais']
def tree(ob,regional=False):
 ob.data.calc_loop_triangles()
 a=np.empty((len(ob.data.vertices),3),dtype=np.float32);ob.data.vertices.foreach_get('co',a.ravel());mw=np.array(ob.matrix_world,dtype=np.float64);a=a@mw[:3,:3].T+mw[:3,3]
 t=np.empty((len(ob.data.loop_triangles),3),dtype=np.int32);ob.data.loop_triangles.foreach_get('vertices',t.ravel())
 if regional:
  xyz=a[t];lo=xyz.min(axis=1);hi=xyz.max(axis=1);t=t[(hi[:,0]>-360)&(lo[:,0]<-235)&(hi[:,1]>285)&(lo[:,1]<360)]
 if len(t)==0:return None
 ids=np.unique(t);mapping=np.full(len(a),-1,dtype=np.int32);mapping[ids]=np.arange(len(ids))
 return BVHTree.FromPolygons(a[ids].tolist(),mapping[t].tolist(),all_triangles=True)
wa=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];wt=tree(wa)
def wet(x,y):
 h=wt.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0]
 return h is not None and abs(h.z-.35)<.001
wetrows=[];geomrows=[]
for name in names:
 ob=sc.objects[name];counts=Counter()
 for f in ob.data.polygons:
  p=ob.matrix_world@f.center
  if p.x>50:continue
  if wet(p.x,p.y):counts[f.material_index]+=1
 wetrows.append({'name':name,'faces_over_water_by_material':dict(counts)})
for ob in sc.objects:
 if ob.type!='MESH' or not (ob.name.startswith('B63 | VISUAL |') or ob.name=='CAIS | contenção costeira alinhada à linha de costa'):continue
 ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);nm=sum(not e.is_manifold for e in bm.edges);bm.free()
 partner=sc.objects.get(ob.get('boas_collision_partner',''));same=partner is not None and len(partner.data.vertices)==len(ob.data.vertices) and len(partner.data.polygons)==len(ob.data.polygons) and all((partner.matrix_world@b.co-ob.matrix_world@a.co).length<1e-6 for a,b in zip(ob.data.vertices,partner.data.vertices))
 geomrows.append({'name':ob.name,'visible':not ob.hide_viewport,'degenerate':sum(t.area<1e-9 for t in ob.data.loop_triangles),'nonmanifold_edges':nm,'collision_matches_vertices_and_faces_count':same})
surfaces=[(sc.objects[n],tree(sc.objects[n],True)) for n in names]+[(o,tree(o,True)) for o in sc.objects if o.name.startswith('B56 | COLLISION | PIER |')]
ref=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf8'));routes=[]
for feat in ref['features']:
 if feat['osm_id'] not in (1426173138,1426173325,1426173326,1426173327):continue
 points=feat['blender_xy'];sampled=[]
 for a,b in zip(points,points[1:]):
  parts=max(1,math.ceil(math.dist(a,b)))
  for i in range(parts):
   x=a[0]+(b[0]-a[0])*i/parts;y=a[1]+(b[1]-a[1])*i/parts;hits=[]
   for o,tr in surfaces:
    if tr is None:continue
    h=tr.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300)[0]
    if h is not None:hits.append((h.z,o.name))
   sampled.append({'xy':[x,y],'support':max(hits) if hits else None,'over_water':wet(x,y)})
 missing=[s['xy'] for s in sampled if s['support'] is None];supported=[s for s in sampled if s['support'] is not None]
 routes.append({'osm_id':feat['osm_id'],'tags':feat['tags'],'samples':len(sampled),'missing_support':len(missing),'missing_examples':missing[:8],'z_range':[min(s['support'][0] for s in supported),max(s['support'][0] for s in supported)] if supported else None,'details':sampled})
props=[]
for o in sc.objects:
 if any(t in o.name.upper() for t in ('CAIS','CAIRU','TERMINAL','MARCELO')) and o.type=='MESH':
  bb=[o.matrix_world@Vector(v) for v in o.bound_box];props.append({'name':o.name,'visible':o.visible_get(),'bbox':[[min(v[k] for v in bb) for k in range(3)],[max(v[k] for v in bb) for k in range(3)]],'properties':{k:str(v) for k,v in o.items()}})
rep={'schema':'boas/coast-reference-b64-inspection-v1','file':Path(bpy.data.filepath).relative_to(r).as_posix(),'reopened':True,'wet_surfaces':wetrows,'generated_geometry':geomrows,'pier_approaches':routes,'coast_objects':props,'real_fidelity_approved':False}
path=r/'docs/reports/blender/coast_reference_b64_inspection.json';tmp=path.with_suffix('.tmp')
try:
 tmp.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(path)
except OSError as err:
 print('REPORT_WRITE_PENDING',str(err))
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_extras=False;sp.region_3d.view_location=Vector((-155,190,15));sp.region_3d.view_distance=360;sp.region_3d.view_rotation=Euler((math.radians(50),0,math.radians(-38)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
print(json.dumps({'wet':wetrows,'geometry':geomrows,'approaches':[{k:v for k,v in x.items() if k!='details'} for x in routes]},ensure_ascii=False))
