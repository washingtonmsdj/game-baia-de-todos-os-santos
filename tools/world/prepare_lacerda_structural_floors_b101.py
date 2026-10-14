"""Pavimentos faltantes a partir dos vetores já catalogados; sem novo levantamento."""
import json, hashlib, math
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[2]
out = root / 'docs/reports/blender/lacerda-floors-b101'
out.mkdir(parents=True, exist_ok=True)
baseline = json.loads((root / 'docs/reports/blender/lacerda-structure-b99/controls.json').read_text())
frame = json.loads((root / 'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
pages = {n: {(v['kind'], v['index']): v for v in json.loads((root / f'artifacts/lacerda-proportions/sheet{n}-vectors.json').read_text())['items']} for n in (14, 15)}
anchor, scale = frame['drawing_to_architecture']['origin_pdf'], frame['pdf_units_per_m']

def convert(n, p):
    T = np.array(baseline['registration'][str(n)]['matrix_to_sheet17'])
    q = (T @ np.r_[p, 1.])[:2]
    return [5.5 + (q[0] - anchor[0]) / scale, -(q[1] - anchor[1]) / scale]

def pt(n, i, j):
    return pages[n][('line' if i > 700 else 'curve', i)]['points'][j]

# Faces internas e quinas permanentes da subestação. A reentrância ocidental
# preserva os dois lances projetados da escada; não vem de uma cápsula.
p15 = [pt(15,376,1), pt(15,376,2), pt(15,370,0), pt(15,375,0),
       pt(15,375,1), pt(15,375,2), pt(15,372,0), pt(15,372,1), pt(15,372,2),
       [pt(15,551,2)[0],pt(15,373,0)[1]], pt(15,373,1),pt(15,373,2),
       pt(15,374,0),pt(15,374,1),pt(15,374,2),pt(15,374,3),
       [pt(15,404,2)[0],pt(15,401,0)[1]],
       [pt(15,404,2)[0],pt(15,1772,0)[1]],
       [pt(15,1772,1)[0],pt(15,1772,0)[1]],
       [pt(15,1772,1)[0],pt(15,376,1)[1]]]
# Somente as áreas de piso das salas desativadas da14, não plataformas sobre
# poços. Contorno principal; rebaixos de peitoril/jamba não viram piso inferido.
north = [pt(14,525,3),pt(14,525,8),pt(14,3209,0),pt(14,2210,0)]
south = [pt(14,2848,1),pt(14,2850,1),pt(14,2850,0),pt(14,2853,1)]
z = frame['levels']['upper_walkable']
specs = [('B101 | cidade alta | laje subsolo 02 subestação',15,p15,-9.74,'SUBSTATION_FLOOR_WITH_DOCUMENT_STAIR_NOTCH'),
         ('B101 | cidade alta | piso sala técnica norte subsolo 03',14,north,-19.85,'DISUSED_MACHINE_ROOM_FLOOR_NORTH'),
         ('B101 | cidade alta | piso sala técnica sul subsolo 03',14,south,-19.85,'DISUSED_MACHINE_ROOM_FLOOR_SOUTH')]
floors=[]
for name,n,p,offset,role in specs:
    local=[convert(n,v) for v in p]
    signed=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(local,local[1:]+local[:1]))/2
    if signed<0:local.reverse()
    assert abs(signed)>10 and min(math.dist(a,b) for a,b in zip(local,local[1:]+local[:1]))>.01
    floors.append({'object':name,'drawing_id':f'sucop-2023-{n}','source_points_pdf':p,
                   'outline_local':local,'top_z':z+offset,'printed_level_offset_m':offset,
                   'area_m2':abs(signed),'function':role})
cfg={'schema':'boas/lacerda-structural-floors-v1','parent_ssot':'world/geographic-reference.json',
     'ssot_sha256':baseline['ssot_sha256'],'registration_reused_from':'docs/reports/blender/lacerda-structure-b99/controls.json',
     'floors':floors,'thickness_candidate_m':.25,'source_ids':['source:lacerda-issue22-sucop-14','source:lacerda-issue22-sucop-15','source:lacerda-issue22-sucop-23'],
     'source_sha256':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (14,15,23)},
     'control_features':{'floor02':'Faces15/370,372–376,373–374,401,404,551; canto de escada15/1772 e projeções colineares de parede',
                         'north03':'Face interna14/525 e limites14/2210,3209',
                         'south03':'Faces internas14/2848,2850,2853'},
     'stair_notch_pdf15':[[pt(15,404,2)[0],pt(15,376,1)[1]],[pt(15,1772,1)[0],pt(15,376,1)[1]],pt(15,1772,1),[pt(15,404,2)[0],pt(15,1772,0)[1]]],
     'accuracy':'DOCUMENT_RELATIVE_LEVELS_AND_MAJOR_FLOOR_CONTOURS_APPROXIMATE_SECTION',
     'not_proven':['espessura estrutural as-built','pequenos rebaixos das salas técnicas','altura/teto das salas antigas','instalação dos quatro ascensores','datum/implantação absoluta','escada executada e circulação completa'],
     'production_ready':False}
(out/'controls.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'floors':[{'object':r['object'],'top_z':r['top_z'],'area_m2':r['area_m2']} for r in floors],'no_new_registration':True},ensure_ascii=False))
