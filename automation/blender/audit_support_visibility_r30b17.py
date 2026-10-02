"""Identifica a geometria que oculta a base do apoio na vista inferior."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv=rot.inverted();scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
eye=rot @ Vector((-115,70,12))
out=[]
for z in (21,25,30,35,40,45,50,60):
    target=rot @ Vector((-23,4,z))
    direction=(target-eye).normalized()
    hit,p,n,face,obj,mat=scene.ray_cast(deps,eye,direction,distance=(target-eye).length)
    out.append({'target_z':z,'hit':obj.name if hit else None,'hit_local':[round(v,2) for v in (inv@p)] if hit else None})
(root/'artifacts/lacerda/r30b17_visibility_rays.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
