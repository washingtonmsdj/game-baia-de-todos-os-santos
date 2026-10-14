"""Localiza frestas B68 por teste XY independente dos raios."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,geometry
r=Path(__file__).resolve().parents[2]
v=json.loads((r/'docs/reports/blender/pier_land_contacts_r30b68_validation.json').read_text(encoding='utf8'));reg=json.loads((r/'artifacts/waterfront/pier_land_region_b67.json').read_text(encoding='utf8'))
out=[]
for row in v['contacts']:
 me=bpy.context.scene.objects[f"B68 | WALKABLE CANDIDATE | encontro terrestre | {row['osm_id']}"].data;me.calc_loop_triangles()
 for xy in row['missing_examples'][:6]:
  q=Vector((*xy,0));hits=[];near=[]
  for t in me.loop_triangles:
   pts=[Vector((me.vertices[i].co.x,me.vertices[i].co.y,0)) for i in t.vertices]
   inside=geometry.intersect_point_tri_2d(q,pts[0],pts[1],pts[2])
   if inside:hits.append(list(t.vertices))
   ds=[]
   for a,b in zip(pts,pts[1:]+pts[:1]):
    d=b-a;tau=max(0,min(1,(q-a).dot(d)/max(d.length_squared,1e-20)));ds.append((q-a-tau*d).length)
   near.append((min(ds),[list(me.vertices[i].co) for i in t.vertices]))
  out.append({'osm_id':row['osm_id'],'q':xy,'inside_xy_triangles':hits,'nearest':sorted(near,key=lambda x:x[0])[:2]})
(r/'docs/reports/blender/pier_gap_diagnosis_b69.json').write_text(json.dumps(out,indent=2),encoding='utf8')
