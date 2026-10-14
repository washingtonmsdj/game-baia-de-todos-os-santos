"""Confere arquivo reaberto, assinaturas, contexto e ausência de alterações."""
import bpy,json,hashlib,os,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102';file=Path(bpy.data.filepath)
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text())
assert file.name=='salvador_lacerda_r30b102_corpo_encosta_quatro_elevadores.blend' and not bpy.data.is_dirty
with file.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
assert sha==r['sha256']
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
for n,s in r['preserved_signatures'].items():assert sig(bpy.context.scene.objects[n])==s,n
for row in r['added']:assert sig(bpy.context.scene.objects[row['object']])==row['after']['signature'],row['object']
assert sig(bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_after_signature']
for n,s in r['proxy_b82_signatures'].items():assert sig(bpy.data.objects[n])==s,n
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
assert not bpy.context.scene['boas_historic_movement_enabled']
assert all(bpy.context.scene.objects[v['object']].hide_get() for v in r['archived'])
r['reopened']=True;q['reopened']=True;q['file']=r['file'];q['source_sha256']=sha
for name,value in [('application.json',r),('validation.json',q)]:
 (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'pid':os.getpid(),'reopened':True,'dirty':bpy.data.is_dirty,'preserved':len(r['preserved_signatures']),'added':len(r['added']),
 'terrain_visible':bpy.context.scene.objects['MVP | terreno corrigido | colisão estática'].visible_get(),'historic_movement_enabled':False}))
