"""Reprojeta somente os pés da rota superior nas superfícies visuais existentes.

Não modifica arquitetura e não acrescenta apoio. A cápsula completa continua
auditada contra todos os obstáculos; o resultado é candidato, não controller.
"""
import json
from pathlib import Path
import numpy as np
from slice_geometry import capsule_distances,support_hits
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller-b80';OUT.mkdir(parents=True,exist_ok=True)
path=ROOT/'artifacts/lacerda-controller/geometry_b79.json';assert path.exists()
d=json.loads(path.read_text(encoding='utf8'));qa=d['qa'];r=qa['character_design']['radius'];h=qa['character_design']['height']
allowed={'SUPERIOR | piso saguão','LAC R30B | Passarela | piso paginado visual','FUNCIONAL | 3 soleira superior',
         'CALIBRADO | piso superior torre','TORRE | cornija galeria','FUNCIONAL | 3 piso'}
allowed|={row['name'] for row in d['objects'] if row['walkable'] and not row['name'].startswith('NAV |')}
floor_tri=[];names=[]
for row in d['objects']:
    if row['name'] not in allowed:continue
    g=d['states']['open_upper']['objects'].get(row['name'],row['geometry']);t=np.asarray(g['vertices'])[np.asarray(g['triangles'])]
    # Contato arredondado também precisa dos espelhos/bordas do piso.
    floor_tri.append(t);names.extend([row['name']]*len(t))
tri=np.concatenate(floor_tri);names=np.asarray(names);lo=tri.min(axis=1);hi=tri.max(axis=1)
old=qa['routes']['upper']['points'];new=[];samples=[];pending=[]
# Adensamento de XY preserva o eixo e revela descontinuidades; não cria rampas.
points=[]
for a,b in zip(old,old[1:]):
    a=np.asarray(a);b=np.asarray(b);count=max(1,int(np.ceil(np.linalg.norm(b-a)/.1)))
    points.extend((a+(b-a)*j/count).tolist() for j in range(count))
points.append(old[-1])
for index,p in enumerate(points):
    p=np.asarray(p,dtype=float);sel=np.flatnonzero(np.all(hi[:,:2]>=p[:2]-r,axis=1)&np.all(lo[:,:2]<=p[:2]+r,axis=1)&(hi[:,2]>=p[2]-.25)&(lo[:,2]<=p[2]+.25))
    local=tri[sel];ids,zs=support_hits(p[0],p[1],local,p[2]-.25,p[2]+.25)
    if not len(ids):
        pending.append({'point':index,'reason':'no_real_center_support','xy':p[:2].tolist()})
        if not len(local):new.append(p.tolist());continue
        # Bordas reais podem tocar a semiesfera do pé; isso permanece pendente
        # de apoio na engine, nunca vira um novo piso na abertura.
        best=int(np.argmin(capsule_distances(p,local,r,h)));ground=float(p[2]);source_name=str(names[sel[best]])
    else:
        best=int(np.argmax(zs));ground=float(zs[best]);source_name=str(names[sel[ids[best]]])
    base=p.copy();base[2]=ground
    # Ajuste vertical de contato com superfície inclinada sob a esfera do pé.
    lower=ground;upper=ground+.25
    for _ in range(25):
        mid=(lower+upper)/2;base[2]=mid
        if capsule_distances(base,local,r,h).min()<r+qa['character_design']['contact_tolerance']:lower=mid
        else:upper=mid
    base[2]=upper
    if upper-ground>.03:pending.append({'point':index,'reason':'rounded_foot_support_requires_engine','foot_lift':upper-ground})
    new.append(base.tolist());samples.append({'point':index,'z_before':float(p[2]),'z_after':upper,'ground_z':ground,'source':source_name})
qa['routes']['upper']['points']=new;qa['routes']['upper']['status']='ground_following_candidate'
qa['source']=d['source'];qa['ground_following']={'method':'real visual faces and capsule contact; XY unchanged','contact_skin':qa['character_design']['contact_tolerance'],'architecture_changed':False,'pending':pending}
(OUT/'walkability_candidate_b80.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d['qa']=qa;(ROOT/'artifacts/lacerda-controller/geometry_b79_ground_b80.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
report={'source':d['source'],'upper_samples':len(new),'changed_foot_heights':sum(abs(x['z_before']-x['z_after'])>1e-5 for x in samples),
        'max_z_change':max(abs(x['z_before']-x['z_after']) for x in samples),'support_sources':sorted(set(x['source'] for x in samples)),
        'missing_or_uncertain_support':pending,'samples':samples,'architecture_changed':False,'engine_verified':False}
(OUT/'ground_following_b80.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('samples','missing_or_uncertain_support')}))
