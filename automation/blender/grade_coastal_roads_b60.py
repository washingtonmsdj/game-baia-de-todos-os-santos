"""B60: plataformas viárias locais, mantendo eixo e largura candidatos explícitos."""
import bpy,json,math,hashlib,runpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
cat_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cat_path.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.59' and Path(bpy.data.filepath).resolve()==(root/src['file']).resolve()
out=root/'blender/salvador_lacerda_r30b60_plataformas_costeiras.blend';assert not out.exists()
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
ground=scene.objects['MVP | terreno corrigido | colisão estática'];old=scene.objects['B59 | GAMEPLAY TERRAIN HQ | encosta contínua']
protected_names=[ground.name,'BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro','CAIS | contenção costeira alinhada à linha de costa']+[o.name for o in scene.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]
protected={n:sig(scene.objects[n]) for n in protected_names}
def tree(ob):
 ob.data.calc_loop_triangles();return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(t.vertices) for t in ob.data.loop_triangles],all_triangles=True)
ot,gt=tree(old),tree(ground)
def hit(t,x,y):return t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)[0]
def floor(x,y):
 a=hit(ot,x,y);b=hit(gt,x,y)
 if a is None:return b
 if b is None:return a
 return a if a.z>=b.z else b
contract=json.loads((root/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'))
xyz=np.array([list(v.co) for v in old.data.vertices],dtype=float);weight_sum=np.zeros(len(xyz));target_sum=np.zeros(len(xyz));profiles=[]
for r in contract['roads']:
 if r['role']!='road_driveable':continue
 runs=[];run=[]
 for si,(a,b) in enumerate(zip(r['blender_xy'],r['blender_xy'][1:])):
  a=np.array(a,dtype=float);b=np.array(b,dtype=float);L=float(np.linalg.norm(b-a));count=max(1,math.ceil(L/.75))
  for q in range(count+1):
   if si and q==0:continue
   p=a+(b-a)*q/count;z=floor(*p)
   if z is None or hit(ot,*p) is None:
    if len(run)>1:runs.append(run)
    run=[];continue
   run.append([float(p[0]),float(p[1]),float(z.z)])
 if len(run)>1:runs.append(run)
 for pts in runs:
  pts=np.array(pts);z=pts[:,2].copy();distance=np.linalg.norm(np.diff(pts[:,:2],axis=0),axis=1)
  feasible=abs(z[-1]-z[0])<=.20*float(distance.sum())
  # Preserva endpoints existentes; suaviza perfil intermediário sem Z global.
  for _ in range(18):
   z[1:-1]=.5*z[1:-1]+.25*(z[:-2]+z[2:])
   if feasible:
    for k in range(1,len(z)-1):z[k]=np.clip(z[k],z[k-1]-.20*distance[k-1],z[k-1]+.20*distance[k-1])
    for k in range(len(z)-2,0,-1):z[k]=np.clip(z[k],z[k+1]-.20*distance[k],z[k+1]+.20*distance[k])
  half=float(r['gameplay_width_m'])/2;reach=half+3.
  best=np.full(len(xyz),np.inf);targets=np.zeros(len(xyz))
  for k,(a,b) in enumerate(zip(pts[:-1,:2],pts[1:,:2])):
   d=b-a;ll=float(d@d)
   if ll<1e-10:continue
   sel=np.where((xyz[:,0]>=min(a[0],b[0])-reach)&(xyz[:,0]<=max(a[0],b[0])+reach)&(xyz[:,1]>=min(a[1],b[1])-reach)&(xyz[:,1]<=max(a[1],b[1])+reach))[0]
   t=np.clip(((xyz[sel,:2]-a)@d)/ll,0,1);dist=np.linalg.norm(xyz[sel,:2]-(a+t[:,None]*d),axis=1)
   better=dist<best[sel];ids=sel[better];best[ids]=dist[better];targets[ids]=z[k]+t[better]*(z[k+1]-z[k])-.015*np.minimum(dist[better]/half,1)**2
  choose=np.isfinite(best)&(best<reach);u=np.clip((best[choose]-half)/3,0,1);weights=1-3*u*u+2*u*u*u
  weight_sum[choose]+=weights;target_sum[choose]+=weights*targets[choose]
  profiles.append({'osm_way_id':r['osm_way_id'],'width_m':float(r['gameplay_width_m']),'width_status':r['gameplay_width_status'],'samples':len(z),'profile_grade_feasible':bool(feasible),'endpoints_preserved':True})
seam=json.loads((root/'docs/reports/blender/coastal_seam_r30b58.json').read_text(encoding='utf8'))['physical_boundary_xy']
locked=((abs(xyz[:,0]-seam['x'])<.0001)&(xyz[:,1]>=seam['y']-.0001))|((abs(xyz[:,1]-seam['y'])<.0001)&(xyz[:,0]>=seam['x']-.0001))
change=(weight_sum>0)&(~locked);blend=np.minimum(weight_sum[change],1)
newz=xyz[:,2].copy();newz[change]=(1-blend)*newz[change]+blend*target_sum[change]/weight_sum[change]
col=bpy.data.collections.new('39.3 GAMEPLAY | B60 VIAS COSTEIRAS');scene.collection.children.link(col)
terrain=old.copy();terrain.data=old.data.copy();terrain.name='B60 | GAMEPLAY TERRAIN HQ | plataformas costeiras';col.objects.link(terrain)
for v,z in zip(terrain.data.vertices,newz):v.co.z=float(z)
terrain.data.update()
for p in terrain.data.polygons:
 slope=math.degrees(math.acos(min(1,max(-1,p.normal.z))));p.material_index=2 if slope>=35 else (1 if slope>=18 or p.center.z<.3 else 0)
terrain['boas_revision']='R30B.60';terrain['boas_gameplay_approved']=False
collision=bpy.data.objects.new('B60 | COLLISION | plataformas costeiras',terrain.data.copy());col.objects.link(collision);collision.hide_viewport=True;collision.hide_render=True
collision['boas_source_surface']=terrain.name;collision['boas_runtime_role']='terrain_collision';collision['boas_geometry_identical_to_visual']=True;collision['boas_gameplay_approved']=False;terrain['boas_collision_partner']=collision.name
old.hide_render=True;old.hide_viewport=True;old['boas_superseded_by']=terrain.name;scene.objects['B59 | COLLISION | terreno encosta contínua']['boas_superseded_by']=collision.name
nt=tree(terrain);roads=[]
for oldroad in list(scene.objects):
 if not oldroad.name.startswith('B59 | ROAD VISUAL |'):continue
 ob=oldroad.copy();ob.data=oldroad.data.copy();ob.name=oldroad.name.replace('B59 |','B60 |',1);col.objects.link(ob)
 for v in ob.data.vertices:
  p=hit(nt,v.co.x,v.co.y)
  if p is None:p=hit(gt,v.co.x,v.co.y)
  assert p is not None
  v.co.z=p.z+.015
 ob.data.update();ob['boas_revision']='R30B.60';ob['boas_collision_source']=collision.name;ob['boas_navigation_status']='needs_drape_on_current_surface'
 oldroad.hide_render=True;oldroad.hide_viewport=True;oldroad['boas_superseded_by']=ob.name;roads.append(ob.name)
assert not [n for n,s in protected.items() if sig(scene.objects[n])!=s]
scene['boas_validation_revision']='R30B.60'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'schema':'boas/coastal-roads-b60-v1','source_before':src,'source_after':{'file':out.relative_to(root).as_posix(),'revision':'R30B.60','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'classification':'ADAPT_LOCAL','profiles':profiles,'road_surfaces':roads,'changed_vertices':int(np.count_nonzero(abs(newz-xyz[:,2])>1e-5)),'max_z_change_m':float(np.max(abs(newz-xyz[:,2]))),'visual_collision_identical':True,'xy_width_core_unchanged':True,'protected_changes':[],'approved':False,'pending':['Conferência após reabertura','Navegação atualizada e travessia na engine','Lacuna histórica até o cais']}
rp=root/'docs/reports/blender/coastal_roads_r30b60.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(root).as_posix(),'notes':'Plataformas locais de vias costeiras candidatas; conserva XY/larguras/núcleo; visual=colisão; circulação não aprovada.'}
for r in cat['revisions']:
 if r['file']==src['file']:r['status']='superseded_validation'
cat['revisions'].append(e);cat['validation_source']=e.copy();cat_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'R30B.60','changed_vertices':report['changed_vertices'],'max_z_change_m':report['max_z_change_m'],'roads':len(roads),'protected_changes':[]}))
