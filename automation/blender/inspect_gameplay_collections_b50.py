import bpy,json
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b50_encosta_sem_blockouts.blend"
rows=[]
for c in bpy.data.collections:
    if any(k in c.name.upper() for k in ("GAMEPLAY","RUNTIME","NAV","COLLISION","ROAD")):
        rows.append({"name":c.name,"hide_viewport":c.hide_viewport,"hide_render":c.hide_render,"objects":len(c.objects)})
print(json.dumps(rows,ensure_ascii=False))
