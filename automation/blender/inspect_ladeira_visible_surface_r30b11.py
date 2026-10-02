"""Identifica objeto que aparece entre contenção e passeio."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
out=[]
for row in rows:
    if row['y'] not in (-50,-25,0,25,50,75):continue
    y=row['y'];x0=row['edge_x'];cross=[]
    for dx in (-.5,0,.25,.5,1,2,3,4,6,8,12,16,20,24,28,32,36,40):
        x=x0+dx;o=rot @ Vector((x,y,110))
        hit,p,n,face,obj,mat=scene.ray_cast(deps,o,Vector((0,0,-1)),distance=180)
        material=None;center=None
        if hit and obj.type=='MESH' and 0<=face<len(obj.data.polygons):
            poly=obj.data.polygons[face]
            if poly.material_index<len(obj.data.materials):material=obj.data.materials[poly.material_index].name
            center=rot.inverted() @ obj.matrix_world @ poly.center
        cross.append([dx,round(p.z,2) if hit else None,material,face,[round(v,2) for v in center] if center else None])
    out.append({'y':y,'edge':x0,'hits':cross})
(root/'artifacts/lacerda/r30b11_visible_surfaces.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
