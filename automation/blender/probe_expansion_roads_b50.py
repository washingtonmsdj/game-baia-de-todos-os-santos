"""Audita presença das vias da expansão costeira na B50."""
import bpy,json
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b50_encosta_sem_blockouts.blend"
ids=[1321544428,154743329,456471269,978527848,1004133493,1004133494,1075624454]
rows=[]
for wid in ids:
    matches=[o for o in bpy.context.scene.objects if str(wid) in o.name or str(o.get("boas_osm_way_id",""))==str(wid) or str(o.get("osm_way_id",""))==str(wid)]
    rows.append({"osm_way_id":wid,"matches":[{"name":o.name,"type":o.type,"hide_viewport":o.hide_viewport,"hide_render":o.hide_render,"collections":[c.name for c in o.users_collection],"props":{k:o[k] for k in o.keys() if not k.startswith("_")}} for o in matches]})
print(json.dumps(rows,ensure_ascii=False))
