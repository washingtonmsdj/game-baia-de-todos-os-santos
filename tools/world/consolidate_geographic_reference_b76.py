"""Registrar referencial compartilhado e derivar Campo da Pólvora da fonte OSM."""
import json, sys, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.georef.world_reference import read_reference, require_shared_transform
from tools.world.build_blender_structure_reference import transform_point
from tools.georef.solve_osm_blender_fit import mercator

def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def write(p,d):
    p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    evidence='artifacts/structural-pipeline/centro-lapa-tororo-fontenova/georef_fit.json'
    fit=read(evidence)['robust_fit']
    keys=('scale_blender_units_per_meter','meters_per_blender_unit','rotation_epsg3857_to_blender_deg','translation_blender','blender_origin_epsg3857','blender_origin_wgs84','true_north_blender_vector','true_north_angle_from_blender_x_deg')
    transform={k:fit[k] for k in keys if k in fit}
    vertical=read('docs/reports/blender/geographic-foundation/vertical_fit_aleph.json')['vertical_fit']
    contract={'schema':'boas/geographic-reference-v1','ssot_id':'salvador-geographic-reference-v1','status':'relative_consistent_absolute_candidate',
      'horizontal':{'source_crs':'EPSG:3857','wgs84_origin_order':'latitude_longitude','transform':transform,'confidence':'candidate','fit_evidence':evidence,'note':'Uma transformação para núcleo e expansão. Escala EPSG:3857 não equivale diretamente a distância no solo; unidade nominal da cena é um metro.'},
      'vertical':{'reference':'existing_scene_local_z','absolute_datum':None,'absolute_datum_verified':False,'candidate_dem_to_scene':vertical,'candidate_evidence':'docs/reports/blender/geographic-foundation/vertical_fit_aleph.json','candidate_applied_to_scene':False,'existing_expansion_recipe':'tools/world/build_centro_expansion_candidate.py','note':'Preservar Z do núcleo. B74/B75 continuam na derivação Terrarium registrada; GeoTIFF Aleph é candidato de auditoria, não substituição silenciosa.'},
      'units':{'blender_unit_nominal_meters':1,'physical_scale_survey_verified':False},
      'sources':{'osm':'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json','aleph_candidate':'docs/reports/aleph/centro-lapa-tororo-fontenova/source_summary.json','historical_aleph_recovered':False},
      'gates':{'independent_regional_fit_allowed':False,'automatic_global_z_adjustment_allowed':False,'missing_height_or_width':None,'runtime_promotion':False,'next_priority':'Validar continuidade vertical do núcleo Tomé de Souza/Lacerda/Cairu; resolver perfil de margem do Dique antes de aprovar expansão.'}}
    path=ROOT/'world/geographic-reference.json'
    if path.exists():
        require_shared_transform(fit,read_reference(path))
    write('world/geographic-reference.json',contract)
    for area in ('mvp-centro-lacerda','centro-lapa-tororo-fontenova'):
        require_shared_transform(read(f'artifacts/structural-pipeline/{area}/georef_fit.json')['robust_fit'],contract)
        p=f'world/areas/{area}/area.json';d=read(p)
        d['coordinate_system']['shared_transform_reference']='world/geographic-reference.json#/horizontal'
        d['coordinate_system']['vertical_reference']='world/geographic-reference.json#/vertical'
        d['coordinate_system']['world_anchor_status']='candidate'
        write(p,d)
    source=read('docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json')
    capture=ROOT/source['capture_folder'];osm=ET.parse(capture/'map.osm').getroot()
    nodes={int(n.attrib['id']):(float(n.attrib['lat']),float(n.attrib['lon'])) for n in osm.findall('node')}
    way=next(w for w in osm.findall('way') if w.attrib['id']=='257336400')
    tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
    ring=[nodes[int(n.attrib['ref'])] for n in way.findall('nd')]
    assert ring[0]==ring[-1] and tags['leisure']=='park'
    xy=[transform_point(mercator(lat,lon),fit) for lat,lon in ring]
    write('artifacts/geographic-foundation/campo-da-polvora.json',{'osm_type':'way','osm_id':257336400,'tags':tags,'wgs84_lat_lon':ring,'blender_xy':xy,'ssot_id':contract['ssot_id'],'capture_id':source['capture_id'],'height':None})
    p='world/areas/centro-lapa-tororo-fontenova/locations.json';d=read(p)
    if not any(l['location_id']=='campo-da-polvora' for l in d['locations']):
        d['locations'].append({'location_id':'campo-da-polvora','name':tags['name'],'category':'square','fidelity_class':'A','priority':5,'model_status':'proxy','reference_status':'partial','osm':{'type':'way','id':257336400,'verified':True,'source_capture_id':source['capture_id']},'position_wgs84':None,'blender_binding':{'custom_property':'boas_location_id','value':'campo-da-polvora','status':'candidate','object':'B76 | Campo da Polvora | footprint OSM'},'required_views':['map'],'production_rules':{'geometry_must_be_realigned':False,'manual_review_required':True,'notes':['Contorno real; Z candidato amostrado da superfície existente. Sem detalhe arquitetônico.']}})
    write(p,d)
    print(json.dumps({'ssot':contract['ssot_id'],'both_fits_identical':True,'campo_vertices':len(xy),'geometry_replaced':False}))

if __name__=='__main__':main()
