"""Listagem limitada de controles vetoriais das plantas, sem alterar a cena."""
import json,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for sheet,ids in [(17,(1682,)),(12,(437,))]:
    data=json.loads((root/f'artifacts/lacerda-proportions/sheet{sheet}-vectors.json').read_text())
    items=data['items']
    print('SHEET',sheet)
    for r in items:
        b=r['bbox'];color=r['stroke']
        if sheet==17 and color==[0.0,0.0,0.0]:
            for a,z in zip(r['points'],r['points'][1:]):
                if 700<math.dist(a,z)<1100 and min(a[0],z[0])>1000 and max(a[0],z[0])<2000 and 800<min(a[1],z[1])<1200:print('BRIDGE_SEGMENT',r['kind'],r['index'],a,z)
        if r['kind']=='curve' and r['index'] in ids:print('SHAFT',json.dumps(r))
        if sheet==17 and 840<b[1]<870 and b[0]>1960 and b[2]<2350 and b[2]-b[0]>35 and b[3]-b[1]<1:print('DIM',json.dumps(r))
        if sheet==17 and color==[0.72157,0.0,0.0] and 1960<b[0]<2350 and b[2]-b[0]<1 and b[1]<860 and b[3]>850 and b[3]-b[1]>20:print('DIM_EXTENSION',json.dumps(r))
        if sheet==17 and color==[0.0,0.0,0.0] and 1100<b[0]<1200 and 1850<b[2]<1990 and 830<b[1]<1150 and b[3]-b[1]<200 and len(r['points'])==2:print('BRIDGE_EDGE',json.dumps(r))
        if sheet==17 and r['kind']=='curve' and 6<len(r['points'])<65 and 2090<b[0]<2250 and 920<b[1]<1080 and b[2]<2300 and b[3]>1180:print('UPPER_SHAFT_CANDIDATE',json.dumps(r))
