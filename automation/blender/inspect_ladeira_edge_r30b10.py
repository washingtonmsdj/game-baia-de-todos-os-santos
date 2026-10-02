"""Localiza a borda interna da Ladeira na malha existente, sem edição."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
tree=BVHTree.FromObject(terrain,bpy.context.evaluated_depsgraph_get())
def hit(x,y):
    origin=rot @ Vector((x,y,100))
    local=terrain.matrix_world.inverted() @ origin
    direction=(terrain.matrix_world.inverted().to_3x3() @ Vector((0,0,-1))).normalized()
    p,n,face,d=tree.ray_cast(local,direction,150)
    if p is None:return None
    mat=terrain.data.materials[terrain.data.polygons[face].material_index].name
    return round((terrain.matrix_world @ p).z,3),mat
rows=[]
for y in range(-90,91,5):
    samples=[]
    for n in range(81):
        x=-55+n*.5
        h=hit(x,y)
        if h:samples.append((x,h[0],h[1]))
    run=[];runs=[]
    for i,s in enumerate(samples):
        road='asfalto da ladeira' in s[2] or 'passeio mineral claro' in s[2]
        if road:run.append(i)
        elif run:runs.append(run);run=[]
    if run:runs.append(run)
    runs=[r for r in runs if any('asfalto da ladeira' in samples[i][2] for i in r)]
    if not runs:continue
    r=max(runs,key=len)
    edge=samples[r[-1]]
    row={'y':y,'edge_x':edge[0],'road_z':edge[1],'road_run_x':[samples[r[0]][0],edge[0]],'slope':[]}
    for dx in (.5,1,2,3,4,6):
        h=hit(edge[0]+dx,y)
        if h:row['slope'].append({'dx':dx,'z':h[0],'material':h[1]})
    rows.append(row)
(root/'artifacts/lacerda/r30b10_ladeira_edge.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'cross_sections':len(rows)},ensure_ascii=False))
