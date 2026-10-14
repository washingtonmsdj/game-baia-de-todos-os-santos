"""Comparar GeoTIFFs Float32 do Aleph pinado sem substituir a fonte da cena."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, sys, types, urllib.request
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'artifacts/geospatial-python'))
import numpy as np
import rasterio
PIN='d24c61507481a91a0dd6afac4f97626a4e5ea780'


def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Bay-of-All-Saints-source-audit'})
    with urllib.request.urlopen(request,timeout=30) as response:
        data=response.read(12_000_001)
    assert len(data)<=12_000_000
    return data


def main():
    folder=ROOT/'docs/reports/blender/geographic-foundation';folder.mkdir(parents=True,exist_ok=True)
    summary_path=folder/'aleph_dem_candidate.json'
    if summary_path.exists():
        saved=json.loads(summary_path.read_text(encoding='utf8'))
        if saved.get('capture_complete'):
            file=ROOT/saved['dem_file']
            assert hashlib.file_digest(file.open('rb'),'sha256').hexdigest()==saved['dem_sha256']
            print(json.dumps({'capture_reused':True,'dem_file':saved['dem_file'],'scene_source_replaced':False}));return
    original=json.loads((ROOT/'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json').read_text(encoding='utf8'))
    capture_id='aleph-geotiff-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    capture=ROOT/'world-reference/centro-lapa-tororo-fontenova/source'/capture_id;capture.mkdir(parents=True)
    code=ROOT/'artifacts/geographic-foundation/aleph-code';code.mkdir(parents=True,exist_ok=True)
    files=[]
    for name in ('common.py','geo.py','terrain.py'):
        url=f'https://raw.githubusercontent.com/Belluxx/Aleph/{PIN}/src/{name}'
        data=fetch(url);path=code/name;path.write_bytes(data)
        files.append({'file':name,'url':url,'sha256':hashlib.sha256(data).hexdigest()})
    package=types.ModuleType('boas_aleph_pinned');package.__path__=[str(code)];sys.modules[package.__name__]=package
    import importlib
    terrain=importlib.import_module('boas_aleph_pinned.terrain')
    tiles=[]
    for previous in sorted(original['terrain']['tiles'],key=lambda t:(t['y'],t['x'])):
        tile={'zoom':previous['z'],'x':previous['x'],'y':previous['y']}
        url=f"https://elevation-tiles-prod.s3.amazonaws.com/geotiff/{tile['zoom']}/{tile['x']}/{tile['y']}.tif"
        data=fetch(url);name=f"terrain_z{tile['zoom']}_x{tile['x']}_y{tile['y']}.tif";path=capture/name;path.write_bytes(data)
        with path.open('rb') as stream:terrain.validate(terrain.TIFF(stream),tile)
        tiles.append({**tile,'filename':name,'source_url':url,'sha256':hashlib.sha256(data).hexdigest()})
        print('GeoTIFF conferido',tile['x'],tile['y'],len(data),flush=True)
    grid={'columns':len({t['x'] for t in tiles}),'rows':len({t['y'] for t in tiles}),'x0':min(t['x'] for t in tiles),'y0':min(t['y'] for t in tiles),'zoom':tiles[0]['zoom']}
    dem=capture/'terrain.tif';terrain.merge(dem,capture,tiles,grid,lambda *args:None)
    old=ROOT/original['capture_folder']/'terrain.tif'
    with rasterio.open(dem) as fine,rasterio.open(old) as coarse:
        fine_values=fine.read(1,masked=True)
        # Comparação nos centros de pixels terrestres da fonte antiga, sem
        # confundir pixel menor com resolução nativa/precisão comprovadas.
        a=coarse.read(1,masked=True);row,col=np.nonzero((~np.ma.getmaskarray(a)) & (a>=0))
        selection=np.arange(0,len(row),max(1,len(row)//5000));row=row[selection];col=col[selection]
        x,y=rasterio.transform.xy(coarse.transform,row,col)
        b=np.array([float(v[0]) for v in fine.sample(zip(x,y),masked=True)])
        delta=b-a[row,col].data
        valid=np.isfinite(delta) & (np.abs(b)<10000)
        comparisons={'samples':int(np.sum(valid)),'median_abs_delta_m':float(np.median(np.abs(delta[valid]))),'p95_abs_delta_m':float(np.percentile(np.abs(delta[valid]),95)),'max_abs_delta_m':float(np.max(np.abs(delta[valid]))),'coarse_pixel_projected_m':coarse.res[0],'fine_pixel_projected_m':fine.res[0]}
        metadata={'shape':[fine.height,fine.width],'crs':str(fine.crs),'pixel_projected_m':list(fine.res),'nodata':fine.nodata,'min_m':float(fine_values.min()),'max_m':float(fine_values.max())}
    record={'schema':'boas/aleph-dem-candidate-v1','capture_id':capture_id,'capture_complete':True,'method':'Aleph terrain.validate/merge do commit pinado; aquisição de terrain GeoTIFF apenas, OSM atual preservado','aleph_commit':PIN,'aleph_code':files,'tiles':tiles,'capture_folder':capture.relative_to(ROOT).as_posix(),'dem_file':dem.relative_to(ROOT).as_posix(),'dem_sha256':hashlib.file_digest(dem.open('rb'),'sha256').hexdigest(),'metadata':metadata,'comparison_to_existing_terrarium':comparisons,'vertical_datum_verified':False,'native_source_resolution_verified':False,'scene_source_replaced':False,'historical_capture_recovered':False,'decision':'GeoTIFF Float32 sem quantização Terrarium e com pixel menor adotado para auditoria candidata; não substituir geometria/altimetria sem fechar o fit vertical e a margem do Dique.','usage_class':'PENDENTE_VERIFICACAO','source_registry':'https://registry.opendata.aws/terrain-tiles/','attribution':'https://github.com/tilezen/joerd/blob/master/docs/attribution.md'}
    (capture/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    summary_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'dem':record['dem_file'],'metadata':metadata,'comparison':comparisons,'scene_source_replaced':False},ensure_ascii=False))


if __name__=='__main__':main()
