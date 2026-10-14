"""Bindings físicos e controles do apoio, antes da correção localizada."""
import bpy,json,runpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-proportions-b84'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b84_fechamento_envidracado.blend'
names=['LAC R30B08 | apoio oposto | '+s for s in ('corpo estrutural afunilado','capitel sob passarela','ressalto transversal')]
bindings=[]
for o in bpy.context.scene.objects:
    props={k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}
    if o.name in names or any(n in str(props) or (n in o.name and 'COLLISION' in o.name) for n in names):bindings.append({'object':o.name,'properties':props,'visible':o.visible_get(),'collection':[c.name for c in o.users_collection]})
r={'pid':os.getpid(),'bindings':bindings,'scene_changed':False}
(OUT/'support_bindings.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,ensure_ascii=False))
