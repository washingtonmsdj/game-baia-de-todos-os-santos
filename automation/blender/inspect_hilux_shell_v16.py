"""Leitura dos contornos da armação V15 na instância visível."""
import bpy,json,collections
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v16.blend'
attr=o.data.attributes['boas_panel_id'];labels=json.loads(o['boas_panel_id_map'])
by_panel=collections.defaultdict(list)
for p in o.data.polygons:by_panel[attr.data[p.index].value].append(p)
rows=[]
for panel,faces in by_panel.items():
    count=collections.Counter();vi=set()
    for f in faces:
        vs=list(f.vertices);vi.update(vs)
        for a,b in zip(vs,vs[1:]+vs[:1]):count[tuple(sorted((a,b)))]+=1
    pts=[o.data.vertices[i].co for i in vi]
    rows.append({'id':panel,'name':labels.get(str(panel),'sem identificação'),'faces':len(faces),
        'boundary_edges':[[list(o.data.vertices[a].co),list(o.data.vertices[b].co)] for (a,b),n in count.items() if n==1],
        'vertices':[[i,*list(o.data.vertices[i].co)] for i in sorted(vi)] if labels.get(str(panel),'').startswith('HILUX15') else []})
(r/'artifacts/vehicles/rondesp/v16-contours-live.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
