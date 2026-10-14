"""Inventário completo delimitado do Lacerda, incluindo coleção 08 omitida."""
import bpy,json,os,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
names=set()
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.get('boas_location_id')=='elevador-lacerda' or any(c.name.startswith(('08 ELEVADOR','11 ELEVADOR','12 LACERDA','13 LACERDA','30 LACERDA','31 LACERDA','HERO | Lacerda')) for c in o.users_collection)):names.add(o.name)
rows=[]
for name in sorted(names):
 o=bpy.context.scene.objects[name]
 if o.constraints:continue
 p=[inv@wm(o)@v.co for v in o.data.vertices]
 rows.append({'object':name,'visible':o.visible_get(),'collections':[c.name for c in o.users_collection],'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'materials':[m.name if m else None for m in o.data.materials],'signature':sig(o)})
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());controls={}
for key in ('upper_floor','lower_floor','new_core','old_core'):
 points=cfg['polygons'][key]['points_local']
 controls[key]=[[sum(p[i] for p in points)/len(points) for i in (0,1)]]
 if key=='lower_floor':controls[key]+=[points[0],points[-1],[(points[0][i]+points[-1][i])/2 for i in (0,1)]]
terrain=bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'];bvh=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get());to_world=wm(terrain);back=to_world.inverted();samples=[]
for key,points in controls.items():
 for xy in points:
  world=M@Vector((xy[0],xy[1],120.));origin=back@world;direction=(back.to_3x3()@Vector((0,0,-1))).normalized();hit,normal,index,distance=bvh.ray_cast(origin,direction,200.)
  samples.append({'control_group':key,'local_xy':xy,'terrain_world_z':(to_world@hit).z if hit else None,'terrain_triangle':index,'terrain_normal_world':list(to_world.to_3x3()@normal) if normal else None})
data={'file':bpy.data.filepath,'scene':bpy.context.scene.name,'pid':os.getpid(),'rows':rows,'terrain_samples':samples,'ssot_registration_accepted':False,'scope':'Inventário para triagem; nomes não comprovam equivalência física ou dimensão.'}
out=root/'docs/reports/blender/lacerda-lower-structure-b93';out.mkdir(parents=True,exist_ok=True);(out/'before.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(rows),'visible':sum(r['visible'] for r in rows),'terrain_samples':samples,'legacy_08':[{'object':r['object'],'bounds':r['bounds']} for r in rows if r['visible'] and any(c.startswith('08 ELEVADOR') for c in r['collections'])]},ensure_ascii=False))
