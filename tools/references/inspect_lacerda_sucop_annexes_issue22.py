"""Inventaria anexos públicos apontados pelo edital; não interpreta projeto como as-built."""
import hashlib,html,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'world-reference/mvp-centro-lacerda/research-20261006-issue22'
OUT=ROOT/'docs/reports/research/lacerda-issue22';START='1CNHoOgnQf4bmJAXPg_DobkX0BzrI4I3E'
queue=[(START,0)];seen=set();rows=[];attempts=[]
while queue and len(seen)<16:
    key,depth=queue.pop(0)
    if key in seen:continue
    seen.add(key);url='https://drive.google.com/drive/folders/'+key
    attempt={'folder_id':key,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:data=r.read(8*1024*1024)
        p=DEST/('sucop-folder-'+key+'.html');p.write_bytes(data);attempt.update(raw_file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),status='retrieved')
        for match in re.finditer(r'<tr data-selectable data-id="([^"]+)"(.*?)</tr>',data.decode('utf8'),re.S):
            item_id,body=match.groups();name=re.search(r'<strong class="DNoYtb">(.*?)</strong>',body,re.S)
            if not name:continue
            name=html.unescape(re.sub('<[^>]+>','',name.group(1)));is_folder='Shared folder' in body
            row={'id':item_id,'name':name,'parent_id':key,'is_folder':is_folder,'source_url':url,'status':'inventory_only','release_status':'DEV_REFERENCE_ONLY'};rows.append(row)
            if is_folder and depth<3:queue.append((item_id,depth+1))
            print(json.dumps(row,ensure_ascii=False),flush=True)
    except Exception as exc:attempt.update(status='unavailable',error=str(exc));print(json.dumps(attempt),flush=True)
    attempts.append(attempt)
(OUT/'sucop_annex_inventory.json').write_text(json.dumps({'official_parent':'Edital SUCOP 24/2023, pp.2/26','folder_attempts':attempts,'items':rows,'scene_changed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
