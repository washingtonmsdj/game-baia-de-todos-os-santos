"""Recupera memoriais oficiais do anexo SUCOP já inventariado, sem alterar cena."""
import json,hashlib,urllib.request,concurrent.futures
from pathlib import Path
from pypdf import PdfReader
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/reports/research/lacerda-issue22';dest=ROOT/'world-reference/mvp-centro-lacerda/research-20261006-issue22'
inventory=json.loads((out/'sucop_annex_inventory.json').read_text(encoding='utf8'))
targets=[r for r in inventory['items'] if r['name'] in ['2301_RREL_PE_Memorial Justificativo_R00.pdf','2301_RREL_PE_Caderno de Especificações_R00.pdf']]
def get(r):
 key='sucop-memorial' if 'Memorial' in r['name'] else 'sucop-specifications';u='https://drive.google.com/uc?export=download&id='+r['id'];row=dict(r,requested_url=u,retrieved_at=datetime.now(timezone.utc).isoformat(),evidence_class='OFFICIAL_TEXT',release_status='DEV_REFERENCE_ONLY')
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as response:data=response.read(20*1024*1024+1)
  assert data.startswith(b'%PDF-') and len(data)<=20*1024*1024
  p=dest/(key+'.pdf');p.write_bytes(data);pdf=PdfReader(p);text='\n'.join(f'\nPAGE {n+1}\n'+page.extract_text() for n,page in enumerate(pdf.pages))
  (ROOT/'artifacts/issue22/pdf'/f'{key}.txt').write_text(text,encoding='utf8')
  row.update(raw_file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),pages=len(pdf.pages),status='pdf_recovered')
  print(key,len(pdf.pages),[line[:200] for line in text.splitlines() if any(t in line.lower() for t in ['cabine','poço','soleira','elevadores','58,93','59 m','levantamento'])][:30],flush=True)
 except Exception as exc:row.update(status='unavailable',error=str(exc));print(row)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(get,targets))
(out/'memorial_acquisition.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
