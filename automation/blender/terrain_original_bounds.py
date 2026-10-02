"""Inspeciona os limites autorais da pista; não modifica a cena salva."""
import bpy,json
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
name=c['export']['road_object']
with bpy.data.libraries.load(str(root/'blender/salvador_lacerda_mvp_r30c2_urban_slice.blend'),link=False) as (src,dst):dst.objects=[name]
o=dst.objects[0]
if o.parent:raise RuntimeError('Transform com ancestral requer dependências')
bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update()
o.data.calc_loop_triangles()
ps=[o.matrix_world@v.co for v in o.data.vertices]
def material_name(m):return m.name.rsplit('.',1)[0] if m.name[-4:-3]=='.' and m.name[-3:].isdigit() else m.name
slots={i:material_name(m) for i,m in enumerate(o.data.materials) if m}
road_ids={i for i,n in slots.items() if n in c['export']['road_materials']}
ts=[t for t in o.data.loop_triangles if t.material_index in road_ids]
tree=BVHTree.FromPolygons(ps,[list(t.vertices) for t in ts],all_triangles=True)
cfg=json.loads((root/'prototypes/threejs-water-lab/public/data/urban_slice.json').read_text())
nodes={}
for r in cfg['routes']:
    for id,p in zip(r['node_ids'],r['points']):
        hit=tree.ray_cast(Vector((p[0],-p[2],150)),Vector((0,0,-1)),300)[0]
        nodes[id]={'xy':[p[0],-p[2]],'pavement_height':hit.z if hit else None}
report={'source':'blender/salvador_lacerda_mvp_r30c2_urban_slice.blend','matrix': [list(row) for row in o.matrix_world],'vertices':len(ps),'triangles':len(o.data.loop_triangles),'material_triangles':dict(Counter(slots.get(t.material_index,'none') for t in o.data.loop_triangles)),'road_triangles':len(ts),'route_nodes':nodes}
bpy.data.objects.remove(o,do_unlink=True)
(root/'artifacts/urban-slice/original-road-bounds.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
