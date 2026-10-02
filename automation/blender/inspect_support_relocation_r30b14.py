"""Verifica implantação candidata do apoio oposto sem editar a cena."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();out=[]
for y in (-2,2,5,9,12):
    for x in (-57,-54,-51,-48,-45,-42,-39):
        o=rot @ Vector((x,y,110))
        hit,p,n,face,obj,mat=scene.ray_cast(deps,o,Vector((0,0,-1)),distance=180)
        out.append([x,y,round(p.z,2) if hit else None,obj.name if hit else None])
(root/'artifacts/lacerda/r30b14_support_footprint.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
