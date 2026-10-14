"""Recupera apenas pranchas estruturais relevantes do anexo público SUCOP."""
import concurrent.futures,hashlib,json,re,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/research/lacerda-issue22'
DEST=ROOT/'world-reference/mvp-centro-lacerda/research-20261006-issue22'
inventory=json.loads((OUT/'sucop_annex_inventory.json').read_text(encoding='utf8'))
selected={3,4,8,12,13,17,21,22,23,24,31,34}
targets=[]
for r in inventory['items']:
    match=re.match(r'2301_RREL_PE_(\d+)_',r['name'])
    if not r['is_folder'] and r['name'].endswith('.pdf') and match and int(match.group(1)) in selected:targets.append(r)
def get(r):
    number=int(re.match(r'2301_RREL_PE_(\d+)_',r['name']).group(1));record=dict(r,prancha=number,retrieved_at=datetime.now(timezone.utc).isoformat(),evidence_class='OFFICIAL_DRAWING',revision='R00',as_built_verified=False)
    try:
        url='https://drive.google.com/uc?export=download&id='+r['id'];request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=40) as response:data=response.read(20*1024*1024+1)
        if not data.startswith(b'%PDF-'):raise ValueError('Resposta não é PDF; não tratar como prancha recuperada')
        if len(data)>20*1024*1024:raise ValueError('Limite de 20 MiB por documento')
        p=DEST/f'sucop-architectural-{number:02d}.pdf';p.write_bytes(data)
        record.update(status='pdf_recovered',download_url=url,raw_file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    except Exception as exc:record.update(status='unavailable',error=str(exc))
    print(json.dumps({'prancha':number,'status':record['status']}),flush=True);return record
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(get,targets))
    (OUT/'drawings_acquisition.json').write_text(json.dumps({'documents':rows,'selection':sorted(selected),'scene_changed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
