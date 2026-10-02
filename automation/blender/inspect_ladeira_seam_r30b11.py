"""Amostra as duas bordas da Ladeira no Blender aberto, sem mutação."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
tree=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
inv=terrain.matrix_world.inverted()
def sample(x,y):
    o=inv @ (rot @ Vector((x,y,110)))
    d=(inv.to_3x3() @ Vector((0,0,-1))).normalized()
    p,n,face,dist=tree.ray_cast(o,d,180)
    if p is None:return None
    return [round((terrain.matrix_world @ p).z,3),terrain.data.materials[terrain.data.polygons[face].material_index].name]
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
out=[]
for row in rows[::3]:
    y=row['y']; left,right=row['road_run_x']
    out.append({'y':y,'road':[left,right,row['road_z']],
        'left':[[round(left-d,2),sample(left-d,y)] for d in (0,.25,.5,1,2,3,5)],
        'right':[[round(right+d,2),sample(right+d,y)] for d in (0,.25,.5,1,2,3,5)]})
(root/'artifacts/lacerda/r30b11_seam_samples.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
