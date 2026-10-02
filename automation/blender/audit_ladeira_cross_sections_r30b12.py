"""Mede faixa asfaltada, passeios e afastamento da encosta no Blender aberto."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv=obj.matrix_world.inverted();tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
def hit(x,y):
    p,n,face,d=tree.ray_cast(inv @ (rot @ Vector((x,y,110))),(inv.to_3x3() @ Vector((0,0,-1))).normalized(),180)
    if p is None:return None
    return ((obj.matrix_world @ p).z,obj.data.materials[obj.data.polygons[face].material_index].name)
rows=[]
for y in range(-60,81,10):
    samples=[(round(-65+i*.1,2),hit(-65+i*.1,y)) for i in range(601)]
    asphalt=[x for x,h in samples if h and 'asfalto da ladeira' in h[1]]
    walk=[x for x,h in samples if h and 'passeio mineral claro' in h[1]]
    if not asphalt or not walk:continue
    a=min(asphalt);b=max(asphalt);outer=max(walk);rz=hit(outer,y)[0]
    low=[];rise=[]
    for d in range(1,351):
        x=outer+d*.1;h=hit(x,y)
        if h and h[0]<rz-1:low.append(x)
        if h and h[0]>=rz+4:rise.append(x)
    rows.append({'y':y,'asphalt_width_m':round(b-a,2),'asphalt_x':[a,b],
        'right_walk_width_m':round(outer-b,2),'right_outer_x':outer,'road_z':round(rz,2),
        'depression_width_m':round(max(low)-min(low),2) if low else 0,
        'first_high_wall_x':round(min(rise),2) if rise else None,
        'distance_outer_walk_to_high_wall_m':round(min(rise)-outer,2) if rise else None})
path=root/'artifacts/lacerda/r30b12_cross_sections.json'
path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
