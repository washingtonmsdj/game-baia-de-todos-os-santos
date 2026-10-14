import bpy,json
from mathutils import Vector
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.visible_get():continue
 bb=[o.matrix_world@Vector(c) for c in o.bound_box]
 mn=[min(p[q] for p in bb) for q in range(3)];mx=[max(p[q] for p in bb) for q in range(3)]
 if mn[0]<-260 and mx[0]>-552 and mn[1]<10 and mx[1]>-510:
  if len(o.data.vertices)>500 or o.name.startswith(('B5','EXPANSAO')):rows.append({'name':o.name,'verts':len(o.data.vertices),'bbox':[mn,mx],'render':not o.hide_render})
print(json.dumps(rows,ensure_ascii=False))
