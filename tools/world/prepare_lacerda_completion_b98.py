"""Controles da frente superior: contornos CAD17 e níveis23, sem novo SSOT."""
import json,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-completion-b98'
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
items=json.loads((root/'artifacts/lacerda-proportions/sheet17-vectors.json').read_text())['items'];curves={x['index']:x for x in items if x['kind']=='curve'}
anchor=cfg['drawing_to_architecture']['origin_pdf'];scale=cfg['pdf_units_per_m']
def local(p):return [5.5+(p[0]-anchor[0])/scale,-(p[1]-anchor[1])/scale]
pillars=[]
for i,k in enumerate((1751,1758,1738,1743),1):
 c=curves[k];assert c['stroke']==[0.,0.,0.] and c['linewidth']==.84
 assert len(c['points'])==6
 # Quatro quinas do contorno estrutural; pequenos rebaixos/capas nas pontas
 # ficam explicitamente simplificados, sem assumir ferragem/seção as-built.
 p=[c['points'][j] for j in (1,2,3,4)]
 pillars.append({'id':f'upper_front_pillar_{i}','drawing_id':'sucop-2023-17','cad_curve_id':k,'trace_pdf':c['points'],'points_pdf':p,'points_local':[local(v) for v in p],'simplification':'SMALL_END_REBATES_OMITTED','accuracy':'DOCUMENT_RELATIVE_CONTOUR_NOT_AS_BUILT'})
spans=[]
for i,(a,b) in enumerate(zip(pillars,pillars[1:])):
 pa=a['points_local'];pb=b['points_local'];polygon=[pa[3],pa[2],pb[1],pb[0]]
 spans.append({'id':f'upper_front_span_{i+1}','points_local':polygon,'function':('ROLLER_CANDIDATE','MAIN_OPEN_ACCESS','ROLLER_CANDIDATE')[i],'source_note':'PORTA DE ROLO na planta17' if i!=1 else 'Vão entre apoios do salão na planta17','clear_width_control':'DOCUMENT_VECTOR_ENDS_NOT_PRINTED_OPENING_COTA'})
z=cfg['levels']['upper_walkable']
d={'schema':'boas/lacerda-upper-completion-v1','parent_ssot':'world/geographic-reference.json','ssot_sha256':cfg['ssot_sha256'],'source_ids':['source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],'source_sha256':{str(k):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{k}.pdf').read_bytes()).hexdigest() for k in (17,23)},'drawing_to_architecture':cfg['drawing_to_architecture'],'pdf_units_per_m':scale,'pillars':pillars,'spans':spans,'levels':{'floor':z,'ceiling':z+3.75,'roof':z+4.,'opening_height_candidate':2.69,'opening_height_status':'INHERITED_APPROXIMATE_FROM_EXISTING_LEAF_NOT_DOCUMENTED'},'canopy_decision':'PRESERVE_SUPERSEDED_REFERENCE: marquise legada flutua 0,957m acima da cobertura atual e excede contorno; não inventar projeção substituta sem controle','absolute_registration_accepted':False,'production_ready':False}
(out/'controls.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pillars':4,'spans':3,'source':'CAD17 / níveis23','absolute_registration_accepted':False}))
