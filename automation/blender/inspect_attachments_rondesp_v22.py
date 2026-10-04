"""Inspeção read-only dos encaixes e luzes sobre V21."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v21_montada.blend'
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();body=s.objects['HILUX | CARROCERIA PRINCIPAL'];ev=body.evaluated_get(dg);me=ev.to_mesh();bt=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
items=[]
for o in s.objects:
 if not o.visible_get() or o.type not in ['MESH','CURVE']:continue
 if not (any(t in o.name for t in ['lanterna','sinalizador','LED lateral','Lente externa','Extremidade','Asa para-choque','Piso antiderrapante','placa traseira','Placa sem','Engate','Esfera engate','Suporte','Terceira luz','Núcleo óptico','Guia óptica','Puxador tampa']) or o==body):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 if not pts:continue
 bbox=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]];center=sum(pts,Vector((0,0,0)))/len(pts)
 samples=[]
 if 'lanterna' in o.name:
  for p in pts[::max(1,len(pts)//8)]:
   side=1 if p.x>0 else -1
   hit,*_=bt.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),3)
   nearest=bt.find_nearest(p)
   samples.append({'p':list(p),'side_hit':list(hit) if hit is not None else None,'side_gap':side*(p.x-hit.x) if hit is not None else None,'nearest_body':list(nearest[0]) if nearest[0] is not None else None,'nearest_distance':nearest[3]})
 items.append({'name':o.name,'bbox':bbox,'center':list(center),'materials':[m.name for m in o.data.materials if m],'mods':[{'type':m.type,'offset':getattr(m,'offset',None),'thickness':getattr(m,'thickness',None)} for m in o.modifiers],'samples':samples})
body_samples=[]
for z in [.535,.65,.77,.943,1.095,1.24,1.29]:
 row={'z':z,'rear':[],'side':[]}
 for x in [.60,.72,.80,.82,.84,.86,.88,.90,.92]:
  hit,*_=bt.ray_cast(Vector((x,3.4,z)),Vector((0,-1,0)),4);row['rear'].append([x,list(hit) if hit is not None else None])
 for y in [2.50,2.60,2.70,2.73,2.74,2.75,2.77]:
  hit,*_=bt.ray_cast(Vector((2,y,z)),Vector((-1,0,0)),3);row['side'].append([y,list(hit) if hit is not None else None])
 body_samples.append(row)
data={'file':bpy.data.filepath,'items':items,'body_samples':body_samples,'body_panels':json.loads(body['boas_panel_id_map']),'root_properties':{k:s.objects['RDP01_ROOT | viatura'][k] for k in s.objects['RDP01_ROOT | viatura'].keys()}}
(r/'artifacts/vehicles/rondesp/v22-before-attachments.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_inspected':len(items),'file':'artifacts/vehicles/rondesp/v22-before-attachments.json'}))
