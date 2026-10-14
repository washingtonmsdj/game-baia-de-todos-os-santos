import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2];me=bpy.data.meshes['B68_LAND_CONTACT_609043799'];me.calc_loop_triangles()
out=[{'property_center':list(t.center),'computed_center':[sum(me.vertices[i].co[k] for i in t.vertices)/3 for k in range(3)],'vertices':[list(me.vertices[i].co) for i in t.vertices]} for t in list(me.loop_triangles)[:5]]
(r/'docs/reports/blender/pier_center_b69.json').write_text(json.dumps(out,indent=2),encoding='utf8')
