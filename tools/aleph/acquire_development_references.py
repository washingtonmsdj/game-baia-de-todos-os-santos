"""Captura limitada de imagens dev com Aleph pinado; nunca importa imagens como assets."""
import argparse,hashlib,importlib,json,sys,types,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
PIN='d24c61507481a91a0dd6afac4f97626a4e5ea780'
sys.path.insert(0,str(ROOT))
from tools.references.provenance import load_policy
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Bay-of-All-Saints-development-reference'}),timeout=20) as r:
        b=r.read(4_000_001)
    if len(b)>4_000_000:raise ValueError('Aquisição excedeu limite por arquivo')
    return b

def portable(value):
    if isinstance(value,dict):return {k:portable(v) for k,v in value.items()}
    if isinstance(value,list):return [portable(v) for v in value]
    if isinstance(value,str):
        normalized=value.replace('\\','/')
        prefix=ROOT.as_posix()+'/'
        if normalized.lower().startswith(prefix.lower()):return normalized[len(prefix):]
    return value
def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('satellite','streetview'),required=True);p.add_argument('--lat',type=float,required=True);p.add_argument('--lon',type=float,required=True);p.add_argument('--label',required=True);p.add_argument('--heading',type=float,default=0);p.add_argument('--look-at',type=float,nargs=2,metavar=('LAT','LON'));p.add_argument('--pano-id',help='Panorama previamente identificado; evita escolher a Cidade Baixa por proximidade XY');p.add_argument('--pitch',type=float,default=0);args=p.parse_args()
    assert -90<args.lat<90 and -180<args.lon<180 and args.label.replace('-','').isalnum()
    load_policy() # aquisição só existe com política central disponível
    code=ROOT/'artifacts/aleph-pinned/src';code.mkdir(parents=True,exist_ok=True)
    cached=code/'pinned.json'
    if cached.exists():
        index=json.loads(cached.read_text(encoding='utf8'));assert index['commit']==PIN
        hashes=index['files']
        for entry in hashes:assert hashlib.sha256((code/Path(entry['path']).name).read_bytes()).hexdigest()==entry['sha256']
    else:
        tree=json.loads(fetch(f'https://api.github.com/repos/Belluxx/Aleph/git/trees/{PIN}?recursive=1'));hashes=[]
        for entry in tree['tree']:
            path=entry['path']
            if not path.startswith('src/') or not path.endswith('.py') or path.count('/')!=1:continue
            payload=fetch(f'https://raw.githubusercontent.com/Belluxx/Aleph/{PIN}/{path}');dest=code/Path(path).name
            dest.write_bytes(payload);hashes.append({'path':path,'sha256':hashlib.sha256(payload).hexdigest()})
        cached.write_text(json.dumps({'commit':PIN,'files':hashes}),encoding='utf8')
    package=types.ModuleType('boas_aleph_dev');package.__path__=[str(code)];sys.modules[package.__name__]=package
    common=importlib.import_module('boas_aleph_dev.common');quick=importlib.import_module('boas_aleph_dev.quick')
    capture_id='aleph-dev-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+args.label
    folder=ROOT/'world-reference/mvp-centro-lacerda/aleph-dev'/capture_id;folder.mkdir(parents=True)
    client=common.Client(cache_dir=folder/'http-cache');requests=[]
    client.request_log=lambda verb,url,attempt,*rest:requests.append({'method':verb,'url':url,'attempt':attempt,'error':str(rest[0]) if rest else None})
    deadline=datetime.now(timezone.utc).timestamp()+75
    client.cancel=lambda:(_ for _ in ()).throw(TimeoutError('Limite de tempo da aquisição')) if datetime.now(timezone.utc).timestamp()>deadline else None
    report={'schema':'boas/aleph-development-reference-v1','capture_id':capture_id,'aleph_commit':PIN,'captured_at':datetime.now(timezone.utc).isoformat(),'kind':args.kind,'requested_coordinate':{'lat':args.lat,'lon':args.lon},'release_status':'DEV_REFERENCE_ONLY','code':hashes,'ssot':'world/geographic-reference.json','purpose':'Conferir acessos, alturas relativas e obstáculos do corredor; sem textura final ou reconstrução automática','status':'pending','images':[]}
    try:
        if args.kind=='satellite':result=quick.satellite(client,folder,lambda *a:None,at=(args.lat,args.lon),size=240,zoom=18)
        else:result=quick.street_photos(client,folder,lambda *a:None,at=None if args.pano_id else (args.lat,args.lon),pano_id=args.pano_id,look_at=tuple(args.look_at) if args.look_at else None,heading=args.heading,pitch=args.pitch,fov=85,radius=45)
        report['result']=portable(result);report['status']=result.get('status','complete')
    except Exception as exc:report['status']='unavailable';report['error']=str(exc)
    report['requests']=requests
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix.lower() in ('.png','.jpg','.jpeg','.tif'):
            report['images'].append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    out=ROOT/'docs/reports/aleph/mvp-centro-lacerda/development';out.mkdir(parents=True,exist_ok=True)
    path=out/(capture_id+'.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    registry=ROOT/'world/data-provenance.json';data=json.loads(registry.read_text(encoding='utf8'))
    if report['images']:
        photos=report.get('result',{}).get('photos',[])
        returned=[{'lat':p.get('lat'),'lon':p.get('lon'),'pano_id':p.get('pano_id'),'imagery_date':p.get('imagery_date')} for p in photos]
        data['resources'].append({'resource_id':'source:'+capture_id,'provider':'Google via Aleph pinado','dataset':args.kind,'release_status':'DEV_REFERENCE_ONLY','capture_id':capture_id,'capture_date':report['captured_at'],'bounds':report.get('result',{}).get('bounds'),'coordinates':returned[0] if len(returned)==1 else None,'returned_coordinates':returned,'requested_coordinate':report['requested_coordinate'],'raw_files':report['images'],'dependencies':[],'purpose':report['purpose'],'kind':'raw_reference','evidence':path.relative_to(ROOT).as_posix(),'derived_objects':[]})
        registry.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'images':len(report['images']),'report':path.relative_to(ROOT).as_posix()},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
