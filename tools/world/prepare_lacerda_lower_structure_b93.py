"""Controles relativos da frente inferior; não constitui registro geográfico."""
import json, math, hashlib
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'docs/reports/blender/lacerda-lower-structure-b93'
cfg = json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
items = json.loads((root/'artifacts/lacerda-proportions/sheet12-vectors.json').read_text())['items']
curves = {x['index']: x for x in items if x['kind'] == 'curve'}

def boundary(ids):
    # O hatch PDF é um conjunto de triângulos com T-junctions. Dividir as
    # arestas nos vértices existentes e cancelar interiores recupera o contorno
    # exato da união; não usar convex hull nem completar o canto por aproximação.
    polys = []
    for i in ids:
        c = curves[i]
        assert c['fill'] and c['fill_color'] == [0.,0.,0.]
        p = []
        for v in c['points']:
            q = tuple(round(x, 2) for x in v)
            if not p or q != p[-1]: p.append(q)
        if p[-1] == p[0]: p.pop()
        assert len(p) == 3, (i, p)
        polys.append(p)
    points = sorted({p for poly in polys for p in poly})
    edges = Counter()
    for poly in polys:
        for a,b in zip(poly,poly[1:]+poly[:1]):
            dx,dy = b[0]-a[0],b[1]-a[1]; ll = dx*dx+dy*dy
            on = []
            for p in points:
                t = ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/ll
                cross = (p[0]-a[0])*dy-(p[1]-a[1])*dx
                if -1e-8 <= t <= 1+1e-8 and abs(cross) < 1e-6: on.append((t,p))
            on.sort()
            for (_,u),(_,v) in zip(on,on[1:]): edges[tuple(sorted((u,v)))] += 1
    assert max(edges.values()) == 2
    adjacent = defaultdict(list)
    for (a,b),n in edges.items():
        if n == 1: adjacent[a].append(b); adjacent[b].append(a)
    assert all(len(v)==2 for v in adjacent.values())
    first=min(adjacent); loop=[first]; prev=None; current=first
    while True:
        nxt=next(v for v in adjacent[current] if v != prev)
        if nxt == first: break
        assert nxt not in loop
        loop.append(nxt); prev,current=current,nxt
    assert len(loop)==len(adjacent)
    area=lambda p: abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1])))/2
    assert abs(area(loop)-sum(area(p) for p in polys)) < 1e-5
    return loop

scale=cfg['pdf_units_per_m']; anchor=cfg['drawing_to_architecture']['origin_pdf']
local=lambda p:[5.5+(p[0]-anchor[0])/scale,-(p[1]-anchor[1])/scale]
groups=[list(range(230,238)),list(range(238,242)),[313,346,347,353,354,355],list(range(421,428))]
pillars=[]
for i,ids in enumerate(groups):
    p=boundary(ids)
    pillars.append({'id':f'lower_front_pillar_{i+1}','drawing_id':'sucop-2023-12','cad_curve_ids':ids,'points_pdf':p,'points_local':[local(v) for v in p], 'confidence':'PROJECT_VECTOR_DERIVED', 'not_proven':['implantação geográfica absoluta','execução as-built','fundação/armadura']})

upper=cfg['levels']['upper_walkable']; floor_offset=-59.01; roof_offset=-53.17
data={'schema':'boas/lacerda-lower-structure-v1','parent_ssot':'world/geographic-reference.json','ssot_sha256':cfg['ssot_sha256'],'drawing_to_architecture':cfg['drawing_to_architecture'],'pdf_units_per_m':scale,
      'source_sha256':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (12,23)},
      'source_ids':['source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-23'], 'pillars':pillars,
      'levels':{'upper_datum_preserved':upper,'hall_floor_offset_printed':floor_offset,'roof_offset_printed':roof_offset,'hall_floor_world':upper+floor_offset,'roof_world':upper+roof_offset,'roof_above_hall_floor':roof_offset-floor_offset,'previous_roof_above_floor':5.76,'architectural_roof_delta':.08,'roof_thickness_inherited_candidate':.25,'shaft_landing_offset_NOT_USED':-58.93},
      'evidence':{'floor':'Prancha12: SAGUÃO 265,56m² / -59,01','roof':'Prancha23: -53,17 COBERTURA CIDADE BAIXA; diferença piso/cobertura 5,84m','pillars':'Quatro massas pretas na linha frontal da planta12; contornos recuperados da união exata de hatchs PDF','roof_thickness':'Espessura herdada candidata, sem cota confirmada nesta rodada'},
      'scope':'Arquitetura relativa; não altera datum do poço, terreno ou GAMEPLAY_PROXY','production_ready':False,'ssot_registration_accepted':False}
out.mkdir(parents=True,exist_ok=True)
(out/'controls.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pillars':len(pillars),'boundary_vertex_counts':[len(p['points_pdf']) for p in pillars],'roof_above_floor':data['levels']['roof_above_hall_floor'],'absolute_placement':'NEEDS_REVIEW'}))
