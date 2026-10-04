"""Identifica faces residuais nas junções depois da solda de vértices."""
import bpy, json, collections
from pathlib import Path
r=Path(__file__).resolve().parents[2];o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
gn={g.index:g.name for g in o.vertex_groups};vgs=[{a.group for a in v.groups if a.weight>.001} for v in o.data.vertices]
result=[];summary=collections.Counter()
for p in o.data.polygons:
    votes=collections.Counter(g for i in p.vertices for g in vgs[i]);name=gn[votes.most_common(1)[0][0]] if votes else 'NONE'
    if not any(n==len(p.vertices) for n in votes.values()):
        summary[name]+=1
        result.append({'face':p.index,'owner':name,'votes':[(gn[g],n) for g,n in votes.most_common()], 'coordinates':[list(o.data.vertices[i].co) for i in p.vertices]})
(r/'artifacts/vehicles/rondesp/v13-residual-faces.json').write_text(json.dumps({'summary':summary,'faces':result},ensure_ascii=False),encoding='utf-8')
