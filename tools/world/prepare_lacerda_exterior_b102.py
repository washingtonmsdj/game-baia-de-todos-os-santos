"""Controles do corpo exterior, separados do perfil do núcleo dos elevadores."""
import json,math,hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
base=json.loads((root/'docs/reports/blender/lacerda-structure-b99/controls.json').read_text())
frame=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
page=json.loads((root/'artifacts/lacerda-proportions/sheet14-vectors.json').read_text())
c={v['index']:v for v in page['items'] if v['kind']=='curve'}
T=np.array(base['registration']['14']['matrix_to_sheet17']);anchor=frame['drawing_to_architecture']['origin_pdf'];scale=frame['pdf_units_per_m']
def convert(p):
 q=(T@np.r_[p,1])[:2];return [5.5+(q[0]-anchor[0])/scale,-(q[1]-anchor[1])/scale]
z=frame['levels']['upper_walkable']
# As duas salas laterais NÃO são o núcleo estreito hachurado da planta17.
# Envoltórias principais: retornos de janelas/portas não são detalhados aqui.
rooms=[]
floorcfg=json.loads((root/'docs/reports/blender/lacerda-floors-b101/controls.json').read_text())
for item in floorcfg['floors'][1:]:
 poly=item['outline_local'];rooms.append({'id':'norte' if 'norte' in item['object'] else 'sul',
 'inner_floor_outline':poly,'floor_object':item['object'],'bottom_z':z-19.85,
 'top_z':z-9.74-.25,'vertical_connection':'CANDIDATE_BETWEEN_DOCUMENT_LEVELS_NOT_AS_BUILT',
 'source':'SUCOP14 salas antigas; SUCOP15 projeções da cobertura; níveis23',
 'wall_thickness_candidate':.25})
# Faces de contenção desenhadas, que ligam a traseira do edifício à encosta.
# Manter o hachurado de rocha como rocha: NÃO gerar piso/sala dentro dele.
paths=[{'id':'face posterior','curve_ids':[518], 'points_pdf':c[518]['points']},
 {'id':'ala norte encosta','curve_ids':[523],'points_pdf':list(reversed(c[523]['points']))},
 {'id':'ala sul encosta','curve_ids':[521],'points_pdf':c[521]['points']}]
for v in paths:
 v['points_local']=[convert(p) for p in v['points_pdf']]
 v['bottom_z']=z-53.17;v['top_z']=z-19.85
 v['vertical_profile_status']='CANDIDATE_SECTION23_CONTINUITY_NOT_SURVEYED'
 v['wall_thickness_candidate']=.25
raw=json.loads((out/'before.json').read_text())
names=['PASSARELA R10 | rodapé','PASSARELA R10 | rodapé.001','PASSARELA R10 | corrimão','PASSARELA R10 | corrimão.001']
archive=[]
for name in names:
 r=next(r for r in raw['rows'] if r['object']==name and r['scene']==raw['scene'])
 assert r['visible'] and r['bounds'][0][1]-r['bounds'][0][0]>50
 archive.append({'object':name,'signature':r['signature'],'reason':'Acabamento R10 com eixo/alcance antigo, fora do contorno documental da ponte B88 e duplicando seus limites atuais','classification':'ERROR'})
config={'schema':'boas/lacerda-exterior-v1','ssot_sha256':base['ssot_sha256'],
 'frame':'docs/reports/blender/lacerda-corridor/scene_b78.json','registration_reused':'docs/reports/blender/lacerda-structure-b99/controls.json',
 'source_ids':['source:lacerda-issue22-sucop-14','source:lacerda-issue22-sucop-15','source:lacerda-issue22-sucop-23'],
 'source_hashes':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (14,15,23)},
 'rooms':rooms,'retaining_paths':paths,'archive':archive,
 'inner_core_preserved':'LAC R30B08 | apoio oposto | corpo estrutural afunilado',
 'not_proven':['espessuras executadas','perfil vertical exato das alas técnicas','encontro absoluto DEM/arquitetura','dimensões/instalação as-built dos quatro equipamentos'],
 'production_ready':False}
(out/'controls.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'archive':len(archive),'rooms':len(rooms),'retaining_walls':len(paths),'no_ssot_change':True}))
