"""Aquisição explícita OSM/Mapzen; não substitui a captura histórica Aleph."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, urllib.request, urllib.parse, math, io, sys
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
AREA = 'centro-lapa-tororo-fontenova'
BBOX = (-12.995, -38.519, -12.966, -38.492)
ZOOM = 14

def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Bay-of-All-Saints/structural-acquisition (+OSM mapping; noncommercial development)'})
    with urllib.request.urlopen(req, timeout=100) as response:
        return response.read(), dict(response.headers)

def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    capture_id = 'osm-mapzen-' + stamp
    folder = ROOT/'world-reference'/AREA/'source'/capture_id
    folder.mkdir(parents=True, exist_ok=False)
    report_dir = ROOT/'docs/reports/world'/AREA
    report_dir.mkdir(parents=True, exist_ok=True)
    south, west, north, east = BBOX
    query = '[out:xml][timeout:90];(way(%s);relation["type"="multipolygon"](%s););(._;>;);out meta;' % (','.join(map(str,BBOX)),','.join(map(str,BBOX)))
    failures = []
    endpoints = [] if '--map-api-only' in sys.argv else ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']
    for endpoint in endpoints:
        try:
            data, headers = fetch(endpoint, urllib.parse.urlencode({'data': query}).encode())
            xml = ET.fromstring(data)
            if xml.find('remark') is not None: raise RuntimeError(xml.find('remark').text)
            assert xml.tag == 'osm' and len(xml.findall('way')) > 0
            break
        except Exception as exc:
            failures.append({'endpoint': endpoint, 'error': str(exc)})
    else:
        # Map API entrega ways completas, mas relações podem ser parciais;
        # preservar todos os recortes e deixar essa condição no QA topológico.
        endpoint='https://api.openstreetmap.org/api/0.6/map'
        query='Quatro janelas Map API; relações de fora da área podem ser parciais'
        midlat=(south+north)/2;midlon=(west+east)/2
        windows=[(w,s,e,north_) for w,e in [(west,midlon),(midlon,east)] for s,north_ in [(south,midlat),(midlat,north)]]
        elements={};parts=[]
        for index,window in enumerate(windows):
            url=endpoint+'?bbox='+','.join(map(str,window))
            raw,h=fetch(url);part=ET.fromstring(raw);assert part.tag=='osm'
            (folder/f'map-part-{index}.osm').write_bytes(raw)
            parts.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'file':f'map-part-{index}.osm'})
            for el in part:
                if el.tag not in ('node','way','relation'):continue
                key=(el.tag,el.attrib['id'])
                if key in elements:
                    assert elements[key].attrib.get('version')==el.attrib.get('version'), 'Versões divergentes entre recortes; requer nova captura'
                elements[key]=el
        xml=ET.Element('osm',version='0.6',generator='Bay of All Saints / explicit Map API composition')
        for key in sorted(elements,key=lambda k:(k[0],int(k[1]))):xml.append(elements[key])
        data=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
    (folder/'map.osm').write_bytes(data)
    osm_meta = {'provider': 'OpenStreetMap contributors / Overpass', 'endpoint': endpoint, 'query': query, 'license': 'ODbL-1.0', 'license_url': 'https://www.openstreetmap.org/copyright', 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'nodes':len(xml.findall('node')), 'ways':len(xml.findall('way')), 'relations':len(xml.findall('relation')), 'fallback_failures': failures}
    if endpoint.endswith('/map'):osm_meta.update(provider='OpenStreetMap contributors / Map API',composition_parts=parts,relations_may_be_partial=True)
    landmarks=[]
    for element in list(xml.findall('way'))+list(xml.findall('relation')):
        tags={t.attrib['k']:t.attrib['v'] for t in element.findall('tag')}
        name=tags.get('name','')
        if any(t in name.lower() for t in ['tororó','tororo','fonte nova','center lapa','shopping lapa']):
            landmarks.append({'osm_type':element.tag,'osm_id':int(element.attrib['id']),'tags':tags})
    n=2**ZOOM
    def tile(lon,lat): return ((lon+180)/360*n, (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
    x0,y0=tile(west,north);x1,y1=tile(east,south)
    ix0,iy0,ix1,iy1=math.floor(x0),math.floor(y0),math.floor(x1),math.floor(y1)
    mosaic=np.empty(((iy1-iy0+1)*256,(ix1-ix0+1)*256),np.float32)
    tiles=[]
    for y in range(iy0,iy1+1):
        for x in range(ix0,ix1+1):
            url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{ZOOM}/{x}/{y}.png'
            blob,h=fetch(url);file=folder/f'terrain-{ZOOM}-{x}-{y}.png';file.write_bytes(blob)
            rgb=np.asarray(Image.open(io.BytesIO(blob)).convert('RGB'),dtype=np.float32)
            elevation=rgb[:,:,0]*256+rgb[:,:,1]+rgb[:,:,2]/256-32768
            mosaic[(y-iy0)*256:(y-iy0+1)*256,(x-ix0)*256:(x-ix0+1)*256]=elevation
            tiles.append({'x':x,'y':y,'z':ZOOM,'url':url,'file':file.name,'sha256':hashlib.sha256(blob).hexdigest(),'imagery_sources':h.get('x-imagery-sources') or h.get('X-Imagery-Sources')})
    radius=6378137.;span=2*math.pi*radius;pixel=span/(n*256)
    left=ix0/n*span-span/2;top=span/2-iy0/n*span
    np.savez_compressed(folder/'terrain.npz',elevation=mosaic,left=np.array(left),top=np.array(top),pixel_size=np.array(pixel),epsg=np.array(3857))
    manifest={'schema':'boas/explicit-osm-mapzen-capture-v1','area_id':AREA,'capture_id':capture_id,'acquired_at_utc':datetime.now(timezone.utc).isoformat(),'requested_bounds_wgs84':{'south':south,'west':west,'north':north,'east':east},'osm':osm_meta,'terrain':{'provider':'Mapzen Terrain Tiles / AWS Open Data','source_registry':'https://registry.opendata.aws/terrain-tiles/','attribution':'https://github.com/tilezen/joerd/blob/master/docs/attribution.md','encoding':'Terrarium PNG','zoom':ZOOM,'crs':'EPSG:3857','pixel_size_projected_m':pixel,'vertical_datum_verified':False,'native_source_resolution_verified':False,'minimum_m':float(mosaic.min()),'maximum_m':float(mosaic.max()),'tiles':tiles},'landmarks':landmarks,'scene_merged':False,'aleph_original_capture_replaced':False}
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    summary={**manifest,'capture_folder':folder.relative_to(ROOT).as_posix(),'source_files_ignored_root':'world-reference/'}
    (report_dir/'source_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'capture_folder':summary['capture_folder'],'osm':osm_meta,'landmarks':landmarks,'dem_shape':list(mosaic.shape)},ensure_ascii=True))

if __name__=='__main__':main()
