"""Registro entre pranchas e contorno exterior de subsolo, subordinado ao SSOT."""
import json,hashlib,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-structure-b99'
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
pages={n:json.loads((root/f'artifacts/lacerda-proportions/sheet{n}-vectors.json').read_text()) for n in (14,15,16,17,18,19,20)}
curves={n:{p['index']:p for p in v['items'] if p['kind']=='curve'} for n,v in pages.items()}
# Três quinas físicas internas à folha, não cantos recortados no limite do PDF:
# SW/SE/NE do mesmo imóvel vizinho no levantamento-base das pranchas.
# Registro desenho→desenho; NÃO equivale a controles físicos aceitos na cena.
indices={14:6,15:7,16:2,17:7,18:7,19:7,20:7};target=np.array(curves[17][7]['points'][1:4],float)
registration={};matrices={};scale=cfg['pdf_units_per_m'];anchor=cfg['drawing_to_architecture']['origin_pdf']
for n in indices:
 if n==17:continue
 points=np.array(curves[n][indices[n]]['points'],float);source=points[1:4]
 # Similaridade 2D limitada: algumas exportações CAD diferem em rotação/escala
 # por arredondamento. Nunca ajustar o SSOT ou permitir deformação afim livre.
 A=[];b=[]
 for (x,y),(u,v) in zip(source,target):A.extend([[x,-y,1,0],[y,x,0,1]]);b.extend([u,v])
 a,s,tx,ty=np.linalg.lstsq(np.array(A),np.array(b),rcond=None)[0];T=np.array([[a,-s,tx],[s,a,ty],[0,0,1.]])
 factor=math.hypot(a,s);assert abs(factor-1)<.0003
 residuals=np.linalg.norm((T@np.column_stack((source,np.ones(3))).T).T[:,:2]-target,axis=1)/scale
 checkpoint=(T@np.r_[points[4],1])[:2];reference=np.array(curves[17][7]['points'][4]);check=float(np.linalg.norm(checkpoint-reference)/scale)
 assert max(max(residuals),check)<.008,(n,residuals,check)
 matrices[n]=T
 registration[str(n)]={'drawing_id':f'sucop-2023-{n}','matrix_to_sheet17':T.tolist(),'scale':factor,'rotation_deg':math.degrees(math.atan2(s,a)),'controls':[{'drawing_point':p.tolist(),'reference_sheet17_point':q.tolist(),'feature':f'neighbor_permanent_roof_corner_{i+1}','source':f'source:lacerda-issue22-sucop-{n}','confidence':'DOCUMENT_CROSS_REFERENCE','residual_m':float(e),'scene_registration_accepted':False} for i,(p,q,e) in enumerate(zip(source,target,residuals))],'independent_check_point':points[4].tolist(),'independent_check_residual_m':check,'reason':'Mesmo contorno permanente do imóvel vizinho visível nas folhas; sem cabine/obra/mobiliário/nomes de mesh','status':'DRAWING_TO_DRAWING_ACCEPTED_NOT_ABSOLUTE_SSOT'}
def convert(n,p):
 q=(matrices[n]@np.r_[p,1])[:2];return [5.5+(q[0]-anchor[0])/scale,-(q[1]-anchor[1])/scale]
d=curves[16];northwest=d[90]['points'];southwest=d[78]['points'];east=d[81]['points']
# Silhueta estrutural exterior. Jambas/rebaixos pequenos de janelas e grelhas
# são omitidos nesta massing, não interpretados como paredes as-built.
south_y=southwest[9][1];e0=np.array(east[10]);e1=np.array(east[5]);south_east=(e0+(e1-e0)*(south_y-e0[1])/(e1[1]-e0[1])).tolist()
refs=[(90,15),(81,14),('DERIVED_EAST_SOUTH',None),(78,9),(78,8),(78,7),(78,6),(78,4),(78,3),(78,2),(90,23),(90,22),(90,21),(90,20),(90,19),(90,18),(90,17),(90,16)]
raw=[south_east if isinstance(i,str) else curves[16][i]['points'][j] for i,j in refs]
outline=[convert(16,p) for p in raw]
# Verificação independente das mesmas quinas na15. Busca limitada à linework
# estrutural já identificada na planta; não cria associação objeto/OSM/mesh.
candidate=[]
for c in curves[15].values():
 b=c['bbox']
 if c['linewidth']<.7 or not (1980<b[0]<2700 and b[2]<2900 and 760<b[1]<1300):continue
 for j,p in enumerate(c['points']):candidate.append((c['index'],j,convert(15,p)))
crosschecks=[]
for i,p in enumerate(outline):
 if i==2:continue
 ci,cj,q=min(candidate,key=lambda c:math.dist(p,c[2]));distance=math.dist(p,q)
 crosschecks.append({'contour_point_index':i,'reference16':refs[i],'reference15_curve':ci,'reference15_vertex':cj,'sheet15_point_local':q,'residual_m':distance,'status':'MATCHED_DOCUMENT_CORNER' if distance<.06 else 'NEEDS_REVIEW'})
match=sum(c['status']=='MATCHED_DOCUMENT_CORNER' for c in crosschecks)
assert match>=14,(match,crosschecks)
z=cfg['levels']['upper_walkable'];floor16=[convert(16,p) for p in curves[16][335]['points']]
if math.dist(floor16[0],floor16[-1])<.001:floor16.pop()
controls={'schema':'boas/lacerda-basement-contours-v1','parent_ssot':'world/geographic-reference.json','ssot_sha256':cfg['ssot_sha256'],'registration':registration,'source_ids':[f'source:lacerda-issue22-sucop-{n}' for n in (15,16,17,23)],'source_sha256':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (15,16,17,23)},'contour_pdf16':raw,'contour_references':refs,'contour_local':outline,'floor16_pdf':curves[16][335]['points'],'floor16_local':floor16,'crosscheck15':crosschecks,'crosscheck_matched':match,'levels':{'floor_subsolo02':z-9.74,'floor_subsolo01':z-4.97,'upper_floor_underside':z-.33,'upper_floor':z,'printed_offsets':[-9.74,-4.97,0.],'wall_height':9.41,'slab_thickness_candidate':.25},'wall_thickness_candidate':.15,'accuracy':'DOCUMENT_CONTOUR_SIMPLIFIED_UNIFORM_THICKNESS','simplifications':['omitir rebaixos pequenos de janelas/grelhas no envelope','espessura uniforme0,15m candidata, baseada em um par de faces da16, não espessura levantada de todas as paredes','corpo vertical usa envelope16 comparado à15; pontos NEEDS_REVIEW não autorizam detalhe métrico','extensões do muro para a encosta excluídas; não altera terreno/retaining world','piso apenas na superfície cinza documentada da16; núcleo hachurado não recebe piso nem preenchimento'],'room14_offset_NOT_MODELED':-19.85,'absolute_ssot_registration_accepted':False,'installed_shaft_dimensions_known':False,'production_ready':False}
(out/'controls.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'matched15':match,'crosscheck_residuals_m':[round(c['residual_m'],4) for c in crosschecks],'contour_bounds':[[min(p[i] for p in outline),max(p[i] for p in outline)] for i in range(2)],'ssot_unchanged':True}))
