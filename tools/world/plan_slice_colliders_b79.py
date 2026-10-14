"""Patches próximos do corredor real; evita copiar o edifício/cidade inteiro."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];d=json.loads((ROOT/'artifacts/lacerda-controller/geometry_b77b.json').read_text(encoding='utf8'))
routes=[np.asarray(r['points']) for r in d['qa']['routes'].values()];patches=[];omitted=[]
for row in d['objects']:
    if row['walkable'] or 'terrain' in row['name'].lower() or 'terreno' in row['name'].lower():continue
    g=row['geometry'];v=np.asarray(g['vertices']);faces=np.asarray(g['triangles']);tri=v[faces]
    selected=np.ones(len(faces),dtype=bool) if row['dynamic'] else np.zeros(len(faces),dtype=bool)
    if not row['dynamic']:
        lo=tri.min(axis=1);hi=tri.max(axis=1)
        for route in routes:
            for a,b in zip(route,route[1:]):
                low=np.minimum(a,b)-[.55,.55,.1];high=np.maximum(a,b)+[.55,.55,2.1]
                selected|=np.all(hi>=low,axis=1)&np.all(lo<=high,axis=1)
        # Interferências do movimento não podem desaparecer do collider do poço.
        sl=np.array(d['shaft_roi']['min']);sh=np.array(d['shaft_roi']['max'])
        selected|=np.all(hi>=sl,axis=1)&np.all(lo<=sh,axis=1)
    f=faces[selected]
    if not len(f):continue
    if len(f)>3000:
        omitted.append({'source':row['name'],'triangles':len(f),'reason':'requires dedicated simplification; no whole visual duplicate'});continue
    used=np.unique(f);lookup={int(old):i for i,old in enumerate(used)}
    patches.append({'source':row['name'],'vertices':v[used].tolist(),'triangles':[[lookup[int(i)] for i in face] for face in f],
                    'dynamic':row['dynamic'],'door':row['elevator_role'] in ('cabin_door','landing_door')})
out={'source':d['source'],'patches':patches,'omitted':omitted,'metric_unit_status':'candidate'}
(ROOT/'artifacts/lacerda-controller/collider_plan_b79.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
print(json.dumps({'patches':len(patches),'triangles':sum(len(p['triangles']) for p in patches),'omitted':len(omitted)}))
