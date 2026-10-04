"""Dry-run da máscara de preservação da Ladeira na B42."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"));wm=runpy.run_path(str(root/"automation/blender/component_fingerprint.py"))["world_matrix"]
g=s.objects[c["export"]["road_object"]];lad=s.objects["R30A7 | ROAD | 103595139"];poly=[wm(lad)@Vector(p.co[:3]) for sp in lad.data.splines for p in sp.points]
before_o=set(bpy.data.objects);before_m=set(bpy.data.meshes);before_mat=set(bpy.data.materials)
with bpy.data.libraries.load(str(root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend"),link=False) as (src,dst):dst.objects=[c["export"]["road_object"]]
old=dst.objects[0]
assert len(old.data.vertices)==len(g.data.vertices)
def distance(p):
 best=1e9
 for a,b in zip(poly,poly[1:]):
  d=(b-a).to_2d();L2=d.length_squared
  if L2<1e-9:continue
  t=max(0,min(1,(p.to_2d()-a.to_2d()).dot(d)/L2));q=a.to_2d()+d*t;best=min(best,(p.to_2d()-q).length)
 return best
core=1.9;outer=2.5;changed=full=blend=0;maxdelta=0
for i,(v,n) in enumerate(zip(g.data.vertices,old.data.vertices)):
 a=wm(g)@v.co;b=wm(old)@n.co;dz=a.z-b.z
 if abs(dz)<1e-5:continue
 changed+=1;dist=distance(a)
 if dist<=core:full+=1;maxdelta=max(maxdelta,abs(dz))
 elif dist<outer:blend+=1;maxdelta=max(maxdelta,abs(dz))
for ob in list(set(bpy.data.objects)-before_o):
 if ob.name!=g.name:bpy.data.objects.remove(ob,do_unlink=True)
for me in list(set(bpy.data.meshes)-before_m):
 if me.users==0:bpy.data.meshes.remove(me)
for mat in list(set(bpy.data.materials)-before_mat):
 if mat.users==0:bpy.data.materials.remove(mat)
print(json.dumps({"b42_changed_ground_vertices":changed,"full_restore_candidates":full,"blend_candidates":blend,"unchanged_by_mask":changed-full-blend,"core_m":core,"outer_m":outer,"max_existing_delta_in_mask_m":maxdelta},ensure_ascii=False))
