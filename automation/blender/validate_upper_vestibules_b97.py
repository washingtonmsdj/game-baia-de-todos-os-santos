"""Persistência, malha, apoios e limites locais; não aprova controller."""
import bpy,bmesh,json,runpy,hashlib,os,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-vestibules-b97';r=json.loads((out/'application.json').read_text());scene=bpy.context.scene
assert Path(bpy.data.filepath).name==Path(r['file']).name and os.getpid()==r['pid']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text());assert proof['file']==r['file'] and proof['sha256']==r['sha256'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
assert all(sig(scene.objects[n])==s for n,s in r['preserved_signatures'].items())
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_signature']
assert all(sig(bpy.data.objects[n])==s for n,s in r['proxy_signatures'].items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
checks=[];guardtrees={}
for row in r['added']:
 o=scene.objects[row['object']];assert sig(o)==row['after']['signature'];bm=bmesh.new();bm.from_mesh(o.data)
 q={'object':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free()
 assert q['nonmanifold_edges']==q['degenerate_faces']==q['inconsistent_winding_edges']==0 and q['volume']>0
 assert o['status']=='GAMEPLAY_PROXY' and o['accuracy']=='APPROXIMATE' and o['replacement_required'] and not o['boas_collision_enabled']
 T=inv@wm(o);guardtrees[o.name]=BVHTree.FromPolygons([T@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]);checks.append(q)
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());z=cfg['levels']['upper_walkable']
o=scene.objects['SUPERIOR | piso saguão'];T=inv@wm(o);o.data.calc_loop_triangles();v=[T@vert.co for vert in o.data.vertices];triangles=[[v[i] for i in tri.vertices] for tri in o.data.loop_triangles]
def support(x,y):
 hits=[]
 for a,b,c in triangles:
  den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
  if abs(den)<1e-12:continue
  u=((b.y-c.y)*(x-c.x)+(c.x-b.x)*(y-c.y))/den;w=((c.y-a.y)*(x-c.x)+(a.x-c.x)*(y-c.y))/den
  if min(u,w,1-u-w)>=-1e-7:hits.append(u*a.z+w*b.z+(1-u-w)*c.z)
 return max(hits) if hits else None
supportchecks=[];limits=[];opening=[];rejected=[]
for side,y,x0,x1 in [('saída',8.65,1.60,5.70),('entrada',-8.90,1.55,4.10)]:
 name=f'B97 | acesso superior | guarda {side}'
 previous_x=1.40 if side=='saída' else 1.35
 distance=guardtrees[name].find_nearest(Vector((previous_x,y,z+.55)))[3]
 rejected.append({'side':side,'xy':[previous_x,y],'guard_clearance_m':distance,'required_m':.315,'classification':'REJECTED_SAMPLE_TOO_CLOSE_TO_GUARD','action':'Interior sample moved laterally; guard unchanged. Not a production route.'})
 for j in range(6):
  x=x0+(x1-x0)*j/5
  for angle in [None]+[2*math.pi*k/8 for k in range(8)]:
   px=x if angle is None else x+.315*math.cos(angle);py=y if angle is None else y+.315*math.sin(angle);height=support(px,py)
   assert height is not None and abs(height-z)<1e-4,(side,px,py,height)
   supportchecks.append({'side':side,'xy':[px,py],'support_z':height})
  nearest=guardtrees[name].find_nearest(Vector((x,y,z+.55)));assert nearest[3]>.315
  limits.append({'side':side,'xy':[x,y],'guard_clearance_m':nearest[3]})
 # Caminho leste não pode receber uma tampa de guarda; apenas verifica as novas peças.
 hit=guardtrees[name].ray_cast(Vector((x1,y,z+.55)),Vector((1.,0.,0.)),2.)
 assert hit[0] is None;opening.append({'side':side,'east_path_clear_of_added_guard':True,'scope':'ONLY_NEW_GUARD_NOT_FULL_SCENE_CONTROLLER'})
assert scene['boas_historic_movement_enabled'] is False
q={'file':r['file'],'sha256':r['sha256'],'reopened':True,'preserved_architecture_components':len(r['preserved_signatures']),'mesh_checks':checks,'support_checks':supportchecks,'local_guard_clearance':limits,'rejected_initial_samples':rejected,'openings':opening,'ssot_preserved':True,'terrain_preserved':True,'proxy_b82_preserved':True,'movement_enabled':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','production_ready':False,'scope':'Apoio local do disco 0,30+skin0,015 e malha das guardas. Não é sweep3D/controller/CCD nem valida acesso à praça ou elevador.'}
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True;(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'meshes':len(checks),'support_samples':len(supportchecks),'preserved':len(r['preserved_signatures'])}))
