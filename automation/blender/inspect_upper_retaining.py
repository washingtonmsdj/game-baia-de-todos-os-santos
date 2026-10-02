import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.context.view_layer.update();rows=[]
for o in bpy.context.scene.objects:
    if o.type in ('MESH','CURVE') and any(s in o.name.lower() for s in ('conten','balaustr','guarda','encosta','mirante','muralha','barranc')):
        p=[o.matrix_world@Vector(v) for v in o.bound_box]
        b=[[round(min(v[i] for v in p),2),round(max(v[i] for v in p),2)] for i in range(3)]
        if b[0][1]<-180 or b[0][0]>140 or b[1][1]<-140 or b[1][0]>210:continue
        rows.append({'name':o.name,'bounds':b,'hidden':o.hide_get() or o.hide_render,'collections':[c.name for c in o.users_collection],'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices] if o.type=='MESH' and len(o.data.vertices)<65 else None})
root=Path(__file__).resolve().parents[2];(root/'artifacts/palacio-rio-branco/retaining_before.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([(r['name'],r['bounds'],r['hidden']) for r in rows if not r['hidden']],ensure_ascii=True))
