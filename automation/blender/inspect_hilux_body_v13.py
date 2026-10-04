"""Inventário das chapas fixas V12 antes do passe de continuidade."""
import bpy,json,collections
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
rows=[]
membership=collections.defaultdict(set)
for v in o.data.vertices:
    for a in v.groups:membership[a.group].add(v.index)
for g in o.vertex_groups:
    ids=membership[g.index]
    if not ids:continue
    pts=[o.data.vertices[i].co for i in ids]
    edges=collections.Counter()
    for p in o.data.polygons:
        if all(i in ids for i in p.vertices):
            vs=list(p.vertices)
            for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
    boundary=[i for pair,n in edges.items() if n==1 for i in pair]
    rows.append({'name':g.name,'vertices':len(ids),'lo':[min(p[k] for p in pts) for k in range(3)],'hi':[max(p[k] for p in pts) for k in range(3)],'boundary':[list(o.data.vertices[i].co) for i in sorted(set(boundary))]})
(r/'artifacts/vehicles/rondesp/v13-components-before.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
