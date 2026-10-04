"""Diagnóstico visual das bordas, read-only na geometria."""
import bpy, json, collections
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
membership=collections.defaultdict(set)
for v in o.data.vertices:
    for a in v.groups: membership[a.group].add(v.index)
rows=[]
for g in o.vertex_groups:
    ids=membership[g.index]
    if not ids:continue
    pts=[o.data.vertices[i].co for i in ids]
    faces=[p for p in o.data.polygons if all(i in ids for i in p.vertices)]
    rows.append({'name':g.name,'vertices':len(ids),'faces':len(faces),'lo':[min(p[k] for p in pts) for k in range(3)],'hi':[max(p[k] for p in pts) for k in range(3)]})
(r/'artifacts/vehicles/rondesp/v13-finish-components.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
thick=next(m for m in o.modifiers if m.type=='SOLIDIFY');state=thick.show_render;thick.show_render=False
exec(compile((r/'automation/blender/review_hilux_body_v13.py').read_text(encoding='utf-8'),str(r/'automation/blender/review_hilux_body_v13.py'),'exec'))
for name in ['cacamba','encontro-cabine','frente']:
    p=r/f'artifacts/vehicles/rondesp/v13-carroceria-{name}.png';p.replace(p.with_name(p.stem+'-sem-espessura.png'))
thick.show_render=state
