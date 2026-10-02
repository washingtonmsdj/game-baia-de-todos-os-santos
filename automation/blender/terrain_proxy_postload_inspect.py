import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text());bpy.context.view_layer.update();out={}
for name in (c['export']['road_object'],c['export']['terrain_proxy']):
    o=bpy.context.scene.objects[name];out[name]={'world':[list(r) for r in o.matrix_world],'basis':[list(r) for r in o.matrix_basis],'parent':o.parent.name if o.parent else None,'modifiers':[m.type for m in o.modifiers],'constraints':[q.type for q in o.constraints],'first_vertex':list(o.matrix_world@o.data.vertices[0].co)}
print(json.dumps(out))
