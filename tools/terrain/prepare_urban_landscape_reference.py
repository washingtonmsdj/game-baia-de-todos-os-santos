"""Extrai usos urbanos OSM da captura autorizada; não inventa dados ausentes."""
import json,math,hashlib,argparse,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--osm',type=Path,required=True);a=p.parse_args()
fit=json.loads((root/'artifacts/structural-pipeline/mvp-centro-lacerda/georef_fit.json').read_text())['robust_fit']
s=fit['scale_blender_units_per_meter'];r=math.radians(fit['rotation_epsg3857_to_blender_deg']);c,t=math.cos(r),math.sin(r);tx,ty=fit['translation_blender']
nodes={};features=[];roads=[]
for event,e in ET.iterparse(a.osm,events=('end',)):
 if e.tag=='node':
  lon,lat=float(e.attrib['lon']),float(e.attrib['lat']);x=6378137*math.radians(lon);y=6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2));nodes[int(e.attrib['id'])]=[s*(c*x-t*y)+tx,s*(t*x+c*y)+ty];e.clear()
 elif e.tag=='way':
  tags={x.attrib['k']:x.attrib['v'] for x in e.findall('tag')};refs=[int(x.attrib['ref']) for x in e.findall('nd')];xy=[nodes[n] for n in refs if n in nodes]
  if xy:
   b=[min(q[0] for q in xy),min(q[1] for q in xy),max(q[0] for q in xy),max(q[1] for q in xy)]
   inside=b[0]<545 and b[2]>-560 and b[1]<625 and b[3]>-510
   if inside and tags.get('highway'):roads.append({'osm_id':int(e.attrib['id']),'tags':tags,'bbox':b})
   selected=tags.get('natural') in ('beach','sand','scrub','wood','grassland') or tags.get('leisure') in ('park','garden','nature_reserve') or tags.get('landuse') in ('grass','recreation_ground','forest')
   if selected and inside:features.append({'osm_id':int(e.attrib['id']),'tags':tags,'closed':refs[0]==refs[-1],'missing_nodes':len(refs)-len(xy),'blender_xy':xy,'bbox':b})
  e.clear()
report={'schema':'boas/urban-landscape-source-v1','source_capture':'aleph-20260924T205631Z-aqqo7pkx','osm_sha256':hashlib.file_digest(a.osm.open('rb'),'sha256').hexdigest(),'fit_status':'candidate','real_widths_verified':False,'features':features,'roads':roads,'beach_count':sum(f['tags'].get('natural')=='beach' for f in features)}
(root/'artifacts/waterfront/urban_landscape_source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'landscape_features':len(features),'beaches':report['beach_count'],'roads':len(roads),'southwestern_roads':[r for r in roads if r['bbox'][1]<-285]}))
