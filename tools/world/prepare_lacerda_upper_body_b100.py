"""Contornos superiores já extraídos: nenhuma busca ou novo registro."""
import json,hashlib,math
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-upper-body-b100'
base=json.loads((root/'docs/reports/blender/lacerda-structure-b99/controls.json').read_text())
frame=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
pages={n:{p['index']:p for p in json.loads((root/f'artifacts/lacerda-proportions/sheet{n}-vectors.json').read_text())['items'] if p['kind']=='curve'} for n in (18,19,20)}
anchor=frame['drawing_to_architecture']['origin_pdf'];scale=frame['pdf_units_per_m']
def convert(n,p):
 T=np.array(base['registration'][str(n)]['matrix_to_sheet17']);q=(T@np.r_[p,1])[:2]
 return [5.5+(q[0]-anchor[0])/scale,-(q[1]-anchor[1])/scale]
def area(p):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2
def ccw(p):return p if area(p)>0 else list(reversed(p))
# Envelope estrutural da19: rebaixos pequenos de pilares/jambas são
# simplificados nas quinas principais; não é desenho de instalação.
nw=[pages[19][594]['points'][10][0],pages[19][594]['points'][4][1]]
ne=[pages[19][573]['bbox'][2],pages[19][573]['bbox'][1]]
se=[pages[19][570]['bbox'][2],pages[19][570]['bbox'][3]]
sw=[pages[19][566]['points'][10][0],pages[19][566]['points'][6][1]]
raw=[nw,ne,se,sw,pages[19][566]['points'][15],pages[19][566]['points'][16],pages[19][595]['points'][2],pages[19][595]['points'][1]]
body=ccw([convert(19,p) for p in raw]);roof=ccw([convert(20,p) for p in pages[20][321]['points'][:-1]])
parapet_inner=ccw([convert(20,p) for p in pages[20][326]['points'][:-1]])
# Reordenar inner pelos cantos correspondentes, com a mesma orientação.
assert len(roof)==len(parapet_inner)==8
before=json.loads((out/'before.json').read_text());rows={r['object']:r for r in before['rows']}
body_names=['FACHADA SUPERIOR | corpo elevado','SUPERIOR | lateral corpo elevado','SUPERIOR | lateral corpo elevado.001','EDIFICIO | parede posterior alta']
archive=body_names+[n for n in rows if n.startswith('EDIFICIO | janela posterior') or any(x in n for x in ('cornija lateral','platibanda lateral','degrau central do coroamento','degrau intermediario'))]
# Coroamento frontal legado também é substituído pelo contorno completo.
archive+= [n for n in rows if n.startswith('FACHADA SUPERIOR |') and any(x in n for x in ('cornija','platibanda','coroamento'))]
archive=list(dict.fromkeys(archive));changes=[];groups={'FRONT':[],'NORTH':[],'SOUTH':[]}
for n,r in rows.items():
 if n in archive or n=='SUPERIOR | cobertura corpo elevado':continue
 if n.startswith('FACHADA SUPERIOR |'):groups['FRONT'].append(n)
 elif n.startswith('EDIFICIO |') and any(x in n for x in ('janela lateral','ombreira lateral','verga peitoril','montante lateral','travessa lateral')):
  groups['NORTH' if sum(r['bounds'][1])>0 else 'SOUTH'].append(n)
assert all(groups.values())
corners={'NW':convert(19,nw),'NE':convert(19,ne),'SE':convert(19,se),'SW':convert(19,sw)}
# Migração rígida por fachada; não esticar caixilhos para preencher o volume.
front=rows['FACHADA SUPERIOR | corpo elevado']['bounds'];south=rows['SUPERIOR | lateral corpo elevado']['bounds'];north=rows['SUPERIOR | lateral corpo elevado.001']['bounds']
old_s=(front[0][1],(front[1][0]+front[1][1])/2)
front_points=np.array([p[:2] for n in groups['FRONT'] if n.startswith('FACHADA SUPERIOR | janela') for p in rows[n]['vertices_local']])
_,vectors=np.linalg.eigh(np.cov(front_points.T));old_front_u=vectors[:,-1]
if old_front_u[1]<0:old_front_u=-old_front_u
# O corpo legado afunila para sul: direção NE do eixo da face é +Y,+X.
new_front_u=np.array(corners['NE'])-np.array(corners['SE']);new_front_u/=np.linalg.norm(new_front_u)
new_s=(np.array(corners['NE'])+np.array(corners['SE']))/2
faces={}
for k,old_anchor,old_u,new_anchor,new_u in [
 ('FRONT',old_s,old_front_u,new_s,new_front_u),
 ('NORTH',[north[0][1],north[1][1]],[1.,0.],corners['NE'],np.array(corners['NE'])-np.array(corners['NW'])),
 ('SOUTH',[south[0][1],south[1][0]],[1.,0.],corners['SE'],np.array(corners['SE'])-np.array(corners['SW']))]:
 old_u=np.array(old_u,float);old_u/=np.linalg.norm(old_u);new_u=np.array(new_u,float);new_u/=np.linalg.norm(new_u)
 angle=math.atan2(new_u[1],new_u[0])-math.atan2(old_u[1],old_u[0]);R=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);t=np.array(new_anchor)-R@np.array(old_anchor)
 faces[k]={'rotation':R.tolist(),'translation':t.tolist(),'old_anchor':list(old_anchor),'new_anchor':list(new_anchor),'rotation_deg':math.degrees(angle),'objects':groups[k]}
z=frame['levels']['upper_walkable'];old_step=3.5833333333333335;new_step=9.42-4.94
windows=[]
for k,g in groups.items():
 for n in g:
  if not (n.startswith('FACHADA SUPERIOR | janela') or n.startswith('EDIFICIO | janela lateral')):continue
  r=rows[n];shift=new_step-old_step if sum(r['bounds'][2])/2>z+8 else 0.
  R=np.array(faces[k]['rotation']);t=np.array(faces[k]['translation']);verts=[]
  for p in r['vertices_local']:
   xy=R@np.array(p[:2])+t;verts.append([*xy,p[2]+shift])
  windows.append({'object':n,'facade':k,'vertices_local_after':verts,'z_shift':shift,'opening_margin_candidate':.025})
assert len(windows)==18,len(windows)
controls={'schema':'boas/lacerda-upper-body-v1','parent_ssot':'world/geographic-reference.json','ssot_sha256':base['ssot_sha256'],'registration_reused_from':'docs/reports/blender/lacerda-structure-b99/controls.json','absolute_ssot_registration_accepted':False,'body_contour_local':body,'body_contour_pdf19':raw,'body_corner_sources':['594/10.x+594/4.y','573 NE pier envelope','570 SE pier envelope','566/10.x+566/6.y','566/15','566/16','595/2','595/1'],'roof_contour_local':roof,'roof_control':'20/321','parapet_inner_local':parapet_inner,'parapet_control':'20/326','corners':corners,'archive':archive,'facade_transforms':faces,'windows':windows,'levels':{'body_bottom':z+4.,'floor1':z+4.94,'floor2':z+9.42,'roof_bottom':z+14.-.25,'roof_top':z+14.,'parapet_top':z+15.4,'slab_thickness_candidate':.25},'second_window_row_shift':new_step-old_step,'wall_thickness_candidate':.30,'floor_admin_boundary':[convert(18,pages[18][563]['points'][0]),convert(18,pages[18][563]['points'][23])],'source_ids':[f'source:lacerda-issue22-sucop-{n}' for n in (18,19,20,23)],'source_sha256':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (18,19,20,23)},'accuracy':'DOCUMENT_RELATIVE_MAJOR_CONTOUR_LEGACY_WINDOW_LAYOUT_CANDIDATE_SECTION','simplifications':['Pequenos rebaixos dos pilares/jambas omitidos no envelope massing','Janelas legadas conservam forma e largura, com migração rígida de fachada; layout/cotas de peitoril candidatos','Segunda fileira acompanha diferença documental de níveis4,48m, sem esticar caixilhos','Lajes somente nas salas administrativas, excluindo ala técnica, caixa de elevadores e escada','Espessura de parede0,30 e laje0,25 herdada/candidata; não seção certificada'],'production_ready':False}
(out/'controls.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'body_points':len(body),'roof_points':len(roof),'archive':len(archive),'facade_components':{k:len(v) for k,v in groups.items()},'windows':len(windows),'floor_levels':controls['levels'],'no_new_registration':True},ensure_ascii=False))
