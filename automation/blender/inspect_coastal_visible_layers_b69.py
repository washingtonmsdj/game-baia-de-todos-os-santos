import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.visible_get():continue
 bb=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[k] for p in bb) for k in range(3)];hi=[max(p[k] for p in bb) for k in range(3)]
 if not(lo[0]<60 and hi[0]>-560 and lo[1]<620 and hi[1]>-110):continue
 if len(o.data.polygons)>1000 or (hi[0]-lo[0]>120 and hi[1]-lo[1]>120):
  rows.append({'name':o.name,'faces':len(o.data.polygons),'bounds':[lo,hi],'collections':[c.name for c in o.users_collection],'properties':{k:o[k] for k in o.keys() if isinstance(o[k],(str,int,float,bool))}})
(r/'docs/reports/blender/coastal_visible_layers_b69.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
