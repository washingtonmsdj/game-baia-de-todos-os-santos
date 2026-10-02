"""Inspeção do DEM-fonte nas duas vias, sem modificar geografia/Blender."""
import argparse,json,math,hashlib
from pathlib import Path
from PIL import Image
parser=argparse.ArgumentParser();parser.add_argument('--capture',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[2];g=json.loads((root/'prototypes/threejs-water-lab/public/data/road_graph.json').read_text());nodes={n['id']:n for n in g['nodes']}
st=json.loads((root/'artifacts/structural-pipeline/mvp-centro-lacerda/osm_structure.json').read_text());tags={f['osm_id']:f['tags'] for f in st['features'] if f['osm_id'] in (421206045,48846625)}
im=Image.open(args.capture/'terrain.tif');scale=im.tag_v2[33550];tie=im.tag_v2[33922];keys=im.tag_v2[34735];entries={keys[4+i*4]:list(keys[5+i*4:8+i*4]) for i in range(keys[3])}
if entries.get(3072)!=[0,1,3857]:raise RuntimeError('DEM precisa de EPSG3857; não presumir CRS')
kind=entries.get(1025)
if kind not in ([0,1,1],[0,1,2]):raise RuntimeError('Sem convenção raster Area/Point')
pixel_is_point=kind==[0,1,2];shift=.5 if pixel_is_point else 0
nodata=float(im.tag_v2[42113]) if 42113 in im.tag_v2 else None
if im.mode!='F':raise RuntimeError('DEM float esperado')
pixel=im.load();out=[]
for w in g['ways']:
    if w['osm_way_id'] not in tags:continue
    points=[]
    for ref in w['node_refs']:
        x,y=nodes[ref]['epsg3857'];col=math.floor((x-tie[3])/scale[0]+tie[0]+shift);row=math.floor((tie[4]-y)/scale[1]+tie[1]+shift);z=pixel[col,row] if 0<=col<im.width and 0<=row<im.height else None
        if z is not None and (not math.isfinite(z) or z==nodata):z=None
        points.append({'node_id':ref,'blender_xy':nodes[ref]['blender_xy'],'dem_m':z})
    out.append({'osm_way_id':w['osm_way_id'],'tags':tags[w['osm_way_id']],'width_verified_m':None,'points':points})
r={'capture_id':args.capture.name,'source_files':['map.osm','terrain.tif'],'dem_sha256':hashlib.file_digest((args.capture/'terrain.tif').open('rb'),'sha256').hexdigest(),'dem_crs':'EPSG:3857','dem_resolution_projected_m':list(scale[:2]),'sampling_method':'nearest pixel via GeoTIFF tiepoint/scale; '+('PixelIsPoint' if pixel_is_point else 'PixelIsArea'),'ways':out,'vertical_fit_quality':'insufficient; source sampling only, not a road grade/width survey','scene_changed':False}
(root/'docs/reports/blender/terrain_conceicao_source_check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False))
usage={'capture_id':args.capture.name,'report':'docs/reports/blender/terrain_conceicao_source_check.json','dem_sha256':r['dem_sha256'],'purpose':'revisão dos níveis das vias Montanha/Conceição; sem aplicação automática do DEM','source_modified':False,'road_widths_verified':False}
for name in ('source_summary.json','dem_audit.json'):
    p=root/'docs/reports/aleph/mvp-centro-lacerda'/name
    if not p.exists():raise RuntimeError('Relatório de proveniência ausente: '+name)
    data=json.loads(p.read_text())
    if name=='source_summary.json' and data.get('capture_id')!=args.capture.name:raise RuntimeError('Captura diverge do registro')
    data['latest_terrain_inspection']=usage
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
