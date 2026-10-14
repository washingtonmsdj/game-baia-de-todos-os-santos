"""Vista de trabalho dos vetores arquitetônicos, coordenadas nativas da prancha."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[2]
for sheet in (17,12):
    d=json.loads((root/f'artifacts/lacerda-proportions/sheet{sheet}-vectors.json').read_text())
    fig,ax=plt.subplots(figsize=(18,8));ax.set_aspect('equal')
    for r in d['items']:
        b=r['bbox'];pts=r['points']
        if b[0]<300 or b[2]>2400 or b[1]<480 or b[3]>1320:continue
        if r['stroke'] not in ([0.,0.,0.],[.59608,.59608,.59608]) or r['linewidth'] not in (.24,.48,.84):continue
        ax.plot([p[0] for p in pts],[p[1] for p in pts],color='black',lw=.5 if r['linewidth']<.7 else 1.3)
    ax.set_xlim(300,2400);ax.set_ylim(1320,480);ax.set_xticks(range(300,2401,100));ax.set_yticks(range(500,1321,50));ax.grid(alpha=.3)
    fig.tight_layout();fig.savefig(root/f'artifacts/lacerda-proportions/sheet{sheet}-geometry.png',dpi=150);plt.close(fig)
