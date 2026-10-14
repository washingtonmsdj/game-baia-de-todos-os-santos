"""B61: pavimento integrado ao piso, sem chapas sobrepostas."""
import bpy,bmesh,json,math,hashlib,runpy,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
cp=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.60' and Path(bpy.data.filepath).resolve()==(root/src['file']).resolve()
out=root/'blender/salvador_lacerda_r30b61_pavimento_integrado.blend';assert not out.exists()
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
names=['MVP | terreno corrigido | colisão estática','BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']+[o.name for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]
protected={n:sig(scene.objects[n]) for n in names}
roads=json.loads((root/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'))['roads'];segments=[]
for rec in roads:
 for a,b in zip(rec['blender_xy'],rec['blender_xy'][1:]):
  a=np.array(a);d=np.array(b)-a;ll=float(d@d)
  if ll>1e-8:segments.append((a,d,ll,float(rec['gameplay_width_m'])/2,rec))
def classify(points,margin=0):
 best=np.full(len(points),np.inf);which=np.full(len(points),-1,dtype=int)
 for k,(a,d,ll,half,r) in enumerate(segments):
  t=np.clip(((points-a)@d)/ll,0,1);dist=np.linalg.norm(points-a-t[:,None]*d,axis=1);good=(dist<=half+margin)&(dist/half<best)
  best[good]=dist[good]/half;which[good]=k
 return which
old=scene.objects['B60 | GAMEPLAY TERRAIN HQ | plataformas costeiras'];me=old.data.copy()
bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();centers=np.array([[f.calc_center_median().x,f.calc_center_median().y] for f in bm.faces]);near=classify(centers,1.);edges=set()
for f,k in zip(bm.faces,near):
 if k>=0:edges.update(f.edges)
bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
for name in ('MVP | asfalto da ladeira','VIAS | pavimento de pedra Rua Chile','MVP | percurso pedonal'):me.materials.append(bpy.data.materials[name])
roles=me.attributes.new(name='boas_surface_role',type='INT',domain='FACE');ids=me.attributes.new(name='boas_osm_way_id',type='INT',domain='FACE')
which=classify(np.array([[p.center.x,p.center.y] for p in me.polygons]));counts={}
for face,k in zip(me.polygons,which):
 if k<0:continue
 rec=segments[int(k)][4];walk=rec['role']=='walkable';sett=(rec.get('surface') or '').lower()=='sett'
 face.material_index=5 if walk else (4 if sett else 3);face.use_smooth=True;roles.data[face.index].value=2 if walk else 1;ids.data[face.index].value=int(rec['osm_way_id']);wid=str(rec['osm_way_id']);counts[wid]=counts.get(wid,0)+1
col=bpy.data.collections.new('39.4 GAMEPLAY | B61 PAVIMENTO INTEGRADO');scene.collection.children.link(col)
terrain=bpy.data.objects.new('B61 | GAMEPLAY TERRAIN HQ | pavimento integrado',me);col.objects.link(terrain)
for k in old.keys():terrain[k]=old[k]
terrain['boas_revision']='R30B.61';terrain['boas_runtime_role']='gameplay_terrain_integrated_candidate';terrain['boas_gameplay_approved']=False
terrain['boas_pavement_status']='Na geometria do piso; largura candidata de gameplay; limites discretizados em até 0.375m.'
collision=bpy.data.objects.new('B61 | COLLISION | terreno e pavimento integrado',me.copy());col.objects.link(collision);collision.hide_viewport=True;collision.hide_render=True
collision['boas_source_surface']=terrain.name;collision['boas_runtime_role']='terrain_collision';collision['boas_geometry_identical_to_visual']=True;collision['boas_gameplay_approved']=False;terrain['boas_collision_partner']=collision.name
old.hide_render=True;old.hide_viewport=True;old['boas_superseded_by']=terrain.name;scene.objects['B60 | COLLISION | plataformas costeiras']['boas_superseded_by']=collision.name
hidden=[]
for ob in scene.objects:
 if ob.name.startswith('B60 | ROAD VISUAL |'):
  ob.hide_viewport=True;ob.hide_render=True;ob['boas_superseded_by']=terrain.name;hidden.append(ob.name)
assert not [n for n,s in protected.items() if sig(scene.objects[n])!=s]
scene['boas_validation_revision']='R30B.61';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'schema':'boas/coastal-pavement-b61-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.61','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'classification':'ERROR','reason':'Pavimento integrado à malha física para eliminar interpenetração de chapas.','terrain':terrain.name,'collision':collision.name,'vertices':len(me.vertices),'faces':len(me.polygons),'pavement_osm_face_counts':counts,'superseded_road_skins':hidden,'protected_changes':[],'visual_collision_identical':True,'runtime_exported':False,'approved':False,'pending':['Lacuna até o cais','Reabertura, apoios e aparência','Navegação e travessia na engine']}
rp=root/'docs/reports/blender/coastal_pavement_r30b61.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Pavimento integrado à malha física; refino local 0.375m; núcleo, água e cais preservados.'}
for r in cat['revisions']:
 if r['file']==src['file']:r['status']='superseded_validation'
cat['revisions'].append(e);cat['validation_source']=e.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.61','vertices':len(me.vertices),'pavement_faces':sum(counts.values()),'protected_changes':[]}))
