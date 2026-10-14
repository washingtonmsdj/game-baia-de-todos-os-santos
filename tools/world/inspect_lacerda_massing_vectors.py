"""Seleciona contornos CAD por região; não usa hachura como limite físico."""
import json,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for sheet in (17,12):
    items=json.loads((root/f'artifacts/lacerda-proportions/sheet{sheet}-vectors.json').read_text())['items']
    print('SHEET',sheet)
    for r in items:
        b=r['bbox'];p=r['points']
        if r['stroke']!=[0.,0.,0.]:continue
        if not (300<b[0]<2300 and 550<b[1]<1450):continue
        if r['kind']=='curve' and len(p)>8 and (r.get('linewidth',0)>.3 or r['index'] in range(1682,1688)):
            print('OUTLINE',r['index'],'bbox',b,'width',r['linewidth'],'points',p)
        elif len(p)==2 and math.dist(*p)>200 and b[2]<2000:
            print('EDGE',r['kind'],r['index'],'width',r['linewidth'],'points',p)
