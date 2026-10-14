"""Recuperação dirigida de plantas exteriores já listadas no anexo SUCOP."""
import json,re,hashlib,urllib.request,concurrent.futures
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];raw=root/'world-reference/mvp-centro-lacerda/research-20261006-issue22';out=root/'docs/reports/blender/lacerda-structure-b99';out.mkdir(parents=True,exist_ok=True)
inventory=json.loads((root/'docs/reports/research/lacerda-issue22/sucop_annex_inventory.json').read_text());selected={14,15,16,18,19,20}
targets=[]
for r in inventory['items']:
 m=re.match(r'2301_RREL_PE_(\d+)_',r['name'])
 if m and int(m.group(1)) in selected and not r['is_folder']:targets.append((int(m.group(1)),r))
assert {n for n,r in targets}==selected
def get(item):
 number,r=item;p=raw/f'sucop-architectural-{number:02}.pdf';url='https://drive.google.com/uc?export=download&id='+r['id']
 row={**r,'prancha':number,'download_url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),'purpose':'Contornos exteriores/subsolos, sem instalação dos ascensores','revision':'R00','as_built_verified':False}
 try:
  if p.exists():data=p.read_bytes()
  else:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(request,timeout=45) as response:data=response.read(20*1024*1024+1)
   assert data.startswith(b'%PDF-') and len(data)<=20*1024*1024,'Resposta não é PDF limitado'
   p.write_bytes(data)
  assert data.startswith(b'%PDF-')
  row.update(status='PDF_RECOVERED',raw_file=p.relative_to(root).as_posix(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 except Exception as e:row.update(status='UNAVAILABLE',error=str(e))
 print(json.dumps({'prancha':number,'status':row['status']}),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(get,targets))
(out/'drawings-acquisition.json').write_text(json.dumps({'documents':rows,'scene_changed':False,'origin_inventory':'docs/reports/research/lacerda-issue22/sucop_annex_inventory.json'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
provpath=root/'world/data-provenance.json';prov=json.loads(provpath.read_text());template=next(r for r in prov['resources'] if r['resource_id']=='source:lacerda-issue22-sucop-17')
for row in rows:
 if row['status']!='PDF_RECOVERED':continue
 resource=json.loads(json.dumps(template));resource.update(resource_id=f'source:lacerda-issue22-sucop-{row["prancha"]}',dataset=row['name'],capture_date='2023-07-10',raw_files=[{'path':row['raw_file'],'sha256':row['sha256'],'bytes':row['bytes'],'url':row['download_url']}],derived_files=['docs/reports/blender/lacerda-structure-b99/drawings-acquisition.json'],purpose='Referência arquitetônica exterior/subsolos. Projeto2023 R00, não as-built ou instalação da cabine.')
 resource['source_url']=row['download_url'];resource['retrieved_at']=row['retrieved_at'];resource['author']='Alexandre Prisco Paraíso Barreto / A+P Arquitetos Associados';resource['as_built_verified']=False
 resource['sheet']=row['prancha'];resource['scale']={'inspected':False,'scale_titleblock':None};resource['capture_id']='lacerda-basements-b99';resource['capture_date']=row['retrieved_at'][:10];resource['document_date']=None;resource['evidence']='docs/reports/blender/lacerda-structure-b99/drawings-acquisition.json'
 existing=next((r for r in prov['resources'] if r['resource_id']==resource['resource_id']),None)
 if existing:existing.update(resource)
 else:prov['resources'].append(resource)
provpath.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
