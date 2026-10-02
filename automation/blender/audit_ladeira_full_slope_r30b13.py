"""Perfis do talude fora do trecho já corrigido."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv=obj.matrix_world.inverted();tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
direction=(inv.to_3x3() @ Vector((0,0,-1))).normalized()
def h(x,y):
    p,n,face,d=tree.ray_cast(inv @ (rot @ Vector((x,y,110))),direction,180)
    return round((obj.matrix_world @ p).z,2) if p else None
rows=json.loads((root/'artifacts/lacerda/r30b13_road_extent.json').read_text(encoding='utf8'))
out=[]
for r in rows:
    if r['y'] not in (-140,-120,-100,-80,-60,80,100,120,140,160):continue
    x=r['outer_x'];y=r['y']
    out.append({'y':y,'road_z':r['road_z'],'outer_x':x,
        'slope':[[d,h(x+d,y)] for d in (0,1,2,4,6,8,10,12,15,20,25,30,35,40,50,60,70)]})
(root/'artifacts/lacerda/r30b13_full_slope.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
