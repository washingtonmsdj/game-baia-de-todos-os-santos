"""Contorno superior derivado de cotas/vetores SUCOP; implantação ainda candidata."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'docs/reports/blender/lacerda-layout-b86';out.mkdir(parents=True,exist_ok=True)
controls=[{'cota_m':5.20,'pdf_span':[1986.24,2182.68]}, {'cota_m':1.99,'pdf_span':[2182.56,2257.80]}, {'cota_m':2.20,'pdf_span':[2257.80,2341.08]}]
scale=sum(c['cota_m']*(c['pdf_span'][1]-c['pdf_span'][0]) for c in controls)/sum(c['cota_m']**2 for c in controls)
for c in controls:c['residual_m']=(c['pdf_span'][1]-c['pdf_span'][0])/scale-c['cota_m']
assert max(abs(c['residual_m']) for c in controls)<.006
anchor_pdf=[2932.68,1085.08];anchor_local=[5.5,0.]
def convert(p):return [anchor_local[0]+(p[0]-anchor_pdf[0])/scale,anchor_local[1]-(p[1]-anchor_pdf[1])/scale]
# Quinas de limites de piso/circulação da 17; não incluem certificação do poço.
outline=[[1976.16,785.08],[2761.8,785.08],[2761.8,713.20],[2968.92,713.20],
         [2953.92,880.84],[2902.68,1443.64],[2902.68,1456.96],[2758.08,1456.96],
         [2758.08,1389.28],[1977.96,1389.28]]
config={'schema':'boas/lacerda-upper-layout-derived-v1','source':'source:lacerda-issue22-sucop-17',
        'drawing_sha256':hashlib.sha256((root/'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-17.pdf').read_bytes()).hexdigest(),
        'scale_pdf_units_per_m':scale,'scale_controls':controls,'outline_pdf':outline,'outline_local':[convert(p) for p in outline],
        'main_station_x':[convert([1976.16,1085.08])[0],5.5],
        'main_station_y':[convert([2932.68,1389.28])[1],convert([2932.68,785.08])[1]],
        'bridge_opening_y':[convert([1976.16,1195.60])[1],convert([1976.16,962.68])[1]],
        'upper_building_x':[convert([2339.40,1085.08])[0],5.5],
        'upper_building_y':[convert([2932.68,1293.04])[1],convert([2932.68,878.92])[1]],
        'old_tower_envelope_center':convert([2183.46,1079.14]),
        'old_tower_envelope_center_status':'CANDIDATE_PROJECT_REGION_CENTER_NOT_INSTALLED_SHAFT_SECTION',
        'placement':{'status':'CANDIDATE_EXISTING_UPPER_ACCESS_ANCHOR','drawing_anchor':anchor_pdf,'scene_anchor_local':anchor_local,'physical_scene_control_count':0,'ssot_registration_accepted':False,'reason':'Forma arquitetônica derivada; implantação das torres e distância do mapa ainda não reconciliadas.'},
        'z_status':'EXISTING_CANDIDATE_PRESERVED','installed_elevator_dimensions_known':False,'production_ready':False}
(out/'layout_source.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:config[k] for k in ('scale_controls','main_station_x','main_station_y','upper_building_x','upper_building_y')},ensure_ascii=False))
