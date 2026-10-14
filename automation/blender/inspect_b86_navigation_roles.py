import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rows=[]
for obj in bpy.context.scene.objects:
    if obj.name=='NAV | passarela superior':
        rows.append({'name':obj.name,'type':obj.type,'display_type':obj.display_type,'hide_render':obj.hide_render,
                     'collections':[c.name for c in obj.users_collection],
                     'properties':{k:str(obj[k]) for k in obj.keys()}})
(root/'docs/reports/blender/lacerda-layout-b86/navigation_roles.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
