"""Levanta toda a extensão viária do talude para correção contínua."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv=obj.matrix_world.inverted();tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
direction=(inv.to_3x3() @ Vector((0,0,-1))).normalized()
def hit(x,y):
    p,n,face,d=tree.ray_cast(inv @ (rot @ Vector((x,y,110))),direction,180)
    if p is None:return None
    return round((obj.matrix_world @ p).z,2),obj.data.materials[obj.data.polygons[face].material_index].name
rows=[]
for y in range(-220,221,10):
    s=[(x*.5,hit(x*.5,y)) for x in range(-240,81)]
    asphalt=[(x,h) for x,h in s if h and 'asfalto da ladeira' in h[1]]
    if not asphalt:continue
    groups=[];g=[]
    for x,h in asphalt:
        if g and x-g[-1][0]>.75:groups.append(g);g=[]
        g.append((x,h))
    if g:groups.append(g)
    prediction=-37-.13*y
    groups=[g for g in groups if 5<=g[-1][0]-g[0][0]<=10 and 15<=g[-1][1][0]<=50 and abs((g[0][0]+g[-1][0])/2-prediction)<30]
    if not groups:continue
    road=min(groups,key=lambda g:abs((g[0][0]+g[-1][0])/2-prediction))
    right=road[-1][0]
    walk=[x for x,h in s if h and 'passeio mineral claro' in h[1] and right<=x<=right+5]
    outer=max(walk) if walk else right
    rows.append({'y':y,'road_x':[road[0][0],right],'asphalt_m':round(right-road[0][0],2),'outer_x':outer,'road_z':road[-1][1][0]})
path=root/'artifacts/lacerda/r30b13_road_extent.json'
path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'rows':len(rows),'range_y':[rows[0]['y'],rows[-1]['y']] if rows else None},ensure_ascii=False))
