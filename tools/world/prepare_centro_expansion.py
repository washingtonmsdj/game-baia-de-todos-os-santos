"""Preparar referência da expansão; sem modificar o Blender ou promover o fit."""
from pathlib import Path
import json, sys, hashlib, subprocess
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'artifacts/geospatial-python'))
import numpy as np
import rasterio
from rasterio.transform import from_origin

def main():
    area='centro-lapa-tororo-fontenova'
    sp=ROOT/'docs/reports/world'/area/'source_summary.json'
    summary=json.loads(sp.read_text(encoding='utf8'))
    folder=ROOT/summary['capture_folder']
    manifest_path=folder/'manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf8'))
    for payload in (manifest, summary):
        payload['bounds_wgs84']=payload['requested_bounds_wgs84']
        payload['bounds_kind']='acquisition_window'
    raster=np.load(folder/'terrain.npz');values=raster['elevation']
    assert np.isfinite(values).all()
    transform=from_origin(float(raster['left']),float(raster['top']),float(raster['pixel_size']),float(raster['pixel_size']))
    tif=folder/'terrain.tif'
    with rasterio.open(tif,'w',driver='GTiff',height=values.shape[0],width=values.shape[1],count=1,dtype='float32',crs='EPSG:3857',transform=transform,compress='deflate') as dst:
        dst.write(values,1)
        dst.update_tags(provider='Mapzen Terrain Tiles',source_manifest='manifest.json',derivation='Lossless Terrarium RGB decode; no vertical adjustment')
    metadata={'file':'terrain.tif','sha256':hashlib.sha256(tif.read_bytes()).hexdigest(),'conversion':'Terrarium decode; same values/extent; no vertical adjustment','raw_tiles_preserved':True}
    manifest['terrain']['derived_geotiff']=metadata;summary['terrain']['derived_geotiff']=metadata
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    summary['manifest_sha256']=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    sp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    out=ROOT/'artifacts/structural-pipeline'/area;out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(ROOT/'tools/world/run_structural_pipeline.py'),'--osm',str(folder/'map.osm'),'--dem',str(tif),'--capture-id',summary['capture_id'],'--capture-bounds-source',str(manifest_path),'--hints',str(ROOT/'docs/reports/blender/r30a/georef_hints.json'),'--dem-statistics','--audit-road-profiles','--output-dir',str(out)]
    import os
    env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'artifacts/geospatial-python')
    env['PYTHONIOENCODING']='utf-8';env['PYTHONUTF8']='1'
    with (out/'pipeline.log').open('w',encoding='utf8') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    status={'area_id':area,'capture_id':summary['capture_id'],'source_summary':sp.relative_to(ROOT).as_posix(),'pipeline_returncode':result.returncode,'pipeline_log':(out/'pipeline.log').relative_to(ROOT).as_posix(),'source_scene':'blender/salvador_lacerda_r30b73_tangente_encosta_costura.blend','scene_merged':False,'world_anchor_verified':False,'vertical_fit_verified':False,'runtime_exported':False,'car_traversal_done':False}
    (ROOT/'docs/reports/world'/area/'preparation.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(status))
    if result.returncode:print((out/'pipeline.log').read_text(encoding='utf8',errors='replace')[-4500:]);raise SystemExit(result.returncode)

if __name__=='__main__':main()
