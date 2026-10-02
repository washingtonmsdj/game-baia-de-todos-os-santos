"""Confere persistência da revisão na mesma janela; não modifica a cena."""
import bpy,json,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['load_post_completed'] and proof['file']==r['source_after']['file'] and proof['sha256']==r['source_after']['sha256']
assert Path(bpy.data.filepath).resolve()==(root/proof['file']).resolve()
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
for entries in (r['protected_signatures'],r['final_scene_signatures']):
    assert all(sig(bpy.context.scene.objects[n])==s for n,s in entries.items()),'Componente mudou na reabertura'
for item in r['terrain']:assert sig(bpy.context.scene.objects[item['object']])==item['after']
r['saved_source_reopened']={**proof,'protected_components_checked':len(r['protected_signatures']),'new_components_checked':len(r['final_scene_signatures']),'terrain_visual_and_proxy_match':True}
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(r['saved_source_reopened'],ensure_ascii=False))
