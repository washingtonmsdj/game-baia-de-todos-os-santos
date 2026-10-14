"""Reconcilia máscaras de piso vetoriais com áreas documentais; não altera Blender."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[2];out=root/'artifacts/lacerda-proportions'
data=json.loads((out/'sheet17-vectors.json').read_text())
colors={};polygons=[];indices=[]
for r in data['items']:
    if r['kind']!='curve' or len(r['points'])<4:continue
    b=r['bbox'];c=r['fill_color']
    if not (700<b[0] and b[2]<2990 and b[1]>690 and b[3]<1470):continue
    if not r['fill']:continue
    colors[str(c)]=colors.get(str(c),0)+1
    if not isinstance(c,list) or min(c)<.70:continue
    pts=r['points'];area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))/2)
    if area>10:polygons.append(pts);indices.append(r['index'])
record={'candidate_only':True,'pdf_frame':True,'colors':colors,'source_indices':indices,'polygons':polygons,'note':'Sobreposições não unidas; não é malha de piso aprovada'}
(out/'sheet17-floor-mask.json').write_text(json.dumps(record),encoding='utf8')
fig,ax=plt.subplots(figsize=(14,5))
for pts,i in zip(polygons,indices):
    x,y=zip(*pts);ax.fill(x,y,color='#afc6da',alpha=.5);ax.plot(x,y,color='#1c435e',linewidth=.5)
    if i in (160,193,197,205,77,79,104):ax.text(sum(x)/len(x),sum(y)/len(y),str(i),fontsize=8,color='red')
ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Máscara vetorial candidata de piso — prancha 17');fig.tight_layout();fig.savefig(out/'sheet17-floor-mask.png',dpi=160)
print(json.dumps({'colors':colors,'polygons':len(polygons)}))
