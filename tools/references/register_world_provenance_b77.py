"""Índice de fontes existentes; catálogos de mídia e capturas continuam canônicos."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def raw(p):
    path=ROOT/p
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    return {'path':p,'sha256':sha}
def main():
    osm=read('docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json')
    dem=read('docs/reports/blender/geographic-foundation/aleph_dem_candidate.json')
    bounds=osm['requested_bounds_wgs84']
    resources=[
      {'resource_id':'source:terrarium-centro-20261005','provider':osm['terrain']['provider'],'dataset':'Terrarium PNG zoom 14; composição nativa/datum pendentes','capture_id':osm['capture_id'],'capture_date':'2026-10-05','bounds':bounds,'raw_files':[raw(osm['capture_folder']+'/'+t['file']) for t in osm['terrain']['tiles']],'usage_class':'PENDENTE_VERIFICACAO','purpose':'Fonte efetiva do terreno greybox B74/B75; não confundir com GeoTIFF candidato','dependencies':[],'evidence':'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json','kind':'survey'},
      {'resource_id':'source:osm-centro-20261005','provider':'OpenStreetMap contributors / Map API','dataset':'OSM XML','capture_id':osm['capture_id'],'capture_date':'2026-10-05','bounds':osm.get('bounds_wgs84',osm.get('bounds')),'raw_files':[raw(osm['capture_folder']+'/map.osm')],'usage_class':'PRODUCAO_COM_ATRIBUICAO','attribution':'© OpenStreetMap contributors — https://www.openstreetmap.org/copyright','purpose':'Geografia de referência, footprints, vias e metadados','dependencies':[],'evidence':'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json','kind':'survey'},
      {'resource_id':'source:aleph-geotiff-20261005','provider':'AWS elevation-tiles-prod via Aleph','dataset':'GeoTIFF Float32; composição nativa/datum ainda desconhecidos','capture_id':dem['capture_id'],'capture_date':'2026-10-05','bounds':osm.get('bounds_wgs84',osm.get('bounds')),'raw_files':[raw(dem['dem_file'])],'usage_class':'PENDENTE_VERIFICACAO','purpose':'Auditoria vertical, sem aplicação global','dependencies':[],'evidence':'docs/reports/aleph/centro-lapa-tororo-fontenova/source_summary.json','kind':'survey'},
      {'resource_id':'source:legacy-dem-mvp','provider':'AWS elevation via Aleph histórico, segundo registro existente','dataset':'DEM histórico do MVP; arquivo original ausente','capture_id':'aleph-20260924T205631Z-aqqo7pkx','capture_date':None,'bounds':None,'raw_files':[],'usage_class':'PENDENTE_VERIFICACAO','purpose':'Proveniência herdada do terreno do núcleo; revisão necessária antes de release','dependencies':[],'evidence':'docs/reports/aleph/mvp-centro-lacerda/source_summary.json','kind':'survey'},
      {'resource_id':'source:legacy-lacerda-authoring','provider':'Bay of All Saints — autoria histórica do núcleo','dataset':'Cena Blender B76; referências por asset ainda parciais','capture_date':None,'bounds':None,'raw_files':[],'usage_class':'PENDENTE_VERIFICACAO','purpose':'Identificar legado sem presumir licença final dos assets','dependencies':[],'evidence':'docs/GEOGRAPHIC_FOUNDATION_B76.md','kind':'authoring'},
      {'resource_id':'derived:lacerda-corridor-b77','provider':'Bay of All Saints — derivação determinística','dataset':'Colisões e percurso medidos na geometria B76','capture_date':'2026-10-05','bounds':None,'raw_files':[],'usage_class':'PENDENTE_VERIFICACAO','purpose':'Primeira vertical slice candidata; não certifica release nem levantamento','dependencies':['source:legacy-dem-mvp','source:legacy-lacerda-authoring'],'kind':'derived','derived_objects':[],'evidence':'docs/reports/blender/lacerda-corridor/'}]
    for resource in resources:
        if resource['resource_id'] in ('source:osm-centro-20261005','source:aleph-geotiff-20261005'):resource['bounds']=bounds
    path=ROOT/'world/data-provenance.json'
    if path.exists():
        existing=json.loads(path.read_text(encoding='utf8'))['resources'];known={r['resource_id'] for r in resources}
        resources.extend(r for r in existing if r['resource_id'] not in known)
    data={'schema':'boas/data-provenance-v1','policy':'world/provenance-policy.json','geographic_ssot':'world/geographic-reference.json','media_catalogs':'world/**/media-manifest.json','resources':resources,'note':'Índice de proveniência; catálogos e resumos referenciados não são substituídos. IDs não conhecidos continuam bloqueando release.'}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'registered_resources':len(resources),'existing_catalogs_reused':True}))
if __name__=='__main__':main()
