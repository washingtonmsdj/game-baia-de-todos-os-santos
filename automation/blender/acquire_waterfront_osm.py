"""Aquisição de referência costeira; não altera nem mescla a cena."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib,xml.etree.ElementTree as ET,datetime,math,gzip
r=Path(__file__).resolve().parents[2]
url='https://api.openstreetmap.org/api/0.6/map?bbox=-38.518,-12.977,-38.5135,-12.9705'
with urlopen(Request(url,headers={'User-Agent':'Bay-of-All-Saints/structural-review'}),timeout=25) as h:data=h.read(5000000)
tree=ET.fromstring(data);assert tree.tag=='osm'
nodes={int(n.get('id')):(float(n.get('lon')),float(n.get('lat'))) for n in tree.findall('node')}
fp=r/'artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json'
fit=json.loads(fp.read_text(encoding='utf-8-sig'))['robust_fit']
old=json.loads((r/'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json').read_text(encoding='utf-8-sig'))
records={f['osm_id']:f for f in old['features'] if f['osm_type']=='way'}
t=math.radians(fit['rotation_epsg3857_to_blender_deg']);s=fit['scale_blender_units_per_meter'];tx,ty=fit['translation_blender']
def xy(lon,lat):
 a=6378137*math.radians(lon);b=6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))
 return [s*(math.cos(t)*a-math.sin(t)*b)+tx,s*(math.sin(t)*a+math.cos(t)*b)+ty]
features=[];controls=[]
for w in tree.findall('way'):
 tags={v.get('k'):v.get('v') for v in w.findall('tag')}
 if not(tags.get('man_made') in ('pier','breakwater','groyne','quay') or tags.get('bridge') or tags.get('waterway')=='dock'):continue
 ids=[int(n.get('ref')) for n in w.findall('nd')];oid=int(w.get('id'));ll=[nodes[n] for n in ids];pts=[xy(*p) for p in ll]
 f={'osm_type':'way','osm_id':oid,'osm_version':int(w.get('version')),'osm_timestamp':w.get('timestamp'),'tags':tags,'node_refs':ids,'lonlat':ll,'blender_xy':pts,'closed':ids[0]==ids[-1],'real_width_m':None,'vertical_status':'pending'}
 features.append(f)
 if oid in records and len(pts)==len(records[oid]['blender_xy']):
  controls.append({'osm_id':oid,'points':len(pts),'max_xy_difference_blender_units':max(math.dist(a,b) for a,b in zip(pts,records[oid]['blender_xy']))})
assert len(controls)>=4 and max(c['max_xy_difference_blender_units'] for c in controls)<0.00005,controls
target=r/'artifacts/waterfront/osm_coastal_check_20261004.osm.gz';target.write_bytes(gzip.compress(data,mtime=0))
rep={'schema':'boas/coastal-osm-source-check-v1','source_url':url,'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bounds_wgs84':{'south':-12.977,'west':-38.518,'north':-12.9705,'east':-38.5135},'source_file':target.relative_to(r).as_posix(),'raw_sha256':hashlib.sha256(data).hexdigest(),'compressed_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'raw_bytes':len(data),'usage_class':'REFERENCIA_INTERNA','license':'ODbL-1.0','attribution':'OpenStreetMap contributors','license_url':'https://www.openstreetmap.org/copyright','fit_reference':fp.relative_to(r).as_posix(),'global_fit_status':'candidate_only','same_feature_controls':controls,'local_transform_reuse_checked':True,'automatic_scene_merge':False,'features':features}
(r/'docs/reports/blender/coastal_osm_source_check.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_file':rep['source_file'],'raw_sha256':rep['raw_sha256'],'controls':controls,'closed_piers':[{'id':f['osm_id'],'points':len(f['blender_xy']),'xy':f['blender_xy']} for f in features if f['tags'].get('man_made')=='pier' and f['closed']]},ensure_ascii=False))
