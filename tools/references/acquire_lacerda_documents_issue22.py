"""Aquisição limitada de documentos públicos; não altera Blender ou referências B80."""
import concurrent.futures,hashlib,json,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'world-reference/mvp-centro-lacerda/research-20261006-issue22'
OUT=ROOT/'docs/reports/research/lacerda-issue22';OUT.mkdir(parents=True,exist_ok=True)
package=json.loads((ROOT/'docs/research/ELEVADOR_LACERDA_EVIDENCE_2026-10-06.json').read_text(encoding='utf8'))
targets=[r for r in package['sources'] if r['id'] in ('iphan-tombamento-1497-t-02','iphan-digital-archive','ufba-concreto-salvador-1919-1938','sucop-concorrencia-24-2023','sbqp-2025-restoration')]
def acquire(r):
    result={'id':r['id'],'requested_url':r['url'],'retrieved_at':datetime.now(timezone.utc).isoformat(),'evidence_class':r['class'],'release_status':'DEV_REFERENCE_ONLY','scene_mutation_authorized':False}
    try:
        request=urllib.request.Request(r['url'],headers={'User-Agent':'Mozilla/5.0 (research public documents)'})
        with urllib.request.urlopen(request,timeout=35) as response:
            result.update(final_url=response.geturl(),content_type=response.headers.get('Content-Type'),http_status=response.status)
            data=response.read(80*1024*1024+1)
        if len(data)>80*1024*1024:raise ValueError('Documento excede limite de 80 MiB')
        is_pdf=data.startswith(b'%PDF-')
        DEST.mkdir(parents=True,exist_ok=True);path=DEST/(r['id']+('.pdf' if is_pdf else '.html'))
        path.write_bytes(data)
        result.update(status='pdf_recovered' if is_pdf else 'non_pdf_response',raw_file=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    except Exception as exc:result.update(status='unavailable',error=str(exc))
    print(json.dumps({'id':r['id'],'status':result['status']},ensure_ascii=False),flush=True)
    return result
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(acquire,targets))
    (OUT/'acquisition.json').write_text(json.dumps({'sources':rows,'geometry_changed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
