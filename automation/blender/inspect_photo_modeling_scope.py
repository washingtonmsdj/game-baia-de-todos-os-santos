"""Implantação existente para ler a foto; inspeção sem alterações de cena."""
import bpy,json
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene;rows=[]
for o in scene.objects:
    text=o.name.lower()
    if (o.type=='MESH' and any(s in text for s in ('casca |','torre','ruína','ruina','encosta','cairu | pav','ladeira','palacio','palácio'))) or o.get('game_role')=='static_building_blockout':
        p=[o.matrix_world@Vector(c) for c in o.bound_box]
        if p and min(v.x for v in p)<100 and max(v.x for v in p)>-160 and min(v.y for v in p)<150 and max(v.y for v in p)>-90:
            rows.append({'name':o.name,'id':o.get('osm_way_id'),'bounds':[[round(min(v[i] for v in p),2),round(max(v[i] for v in p),2)] for i in range(3)],'collections':[c.name for c in o.users_collection],'visible':not o.hide_get() and not o.hide_render,'materials':[m.name if m else None for m in o.data.materials],'props':{k:o[k] for k in o.keys() if k.startswith(('source_','reference_','boas_location','classification'))}})
root=Path(__file__).resolve().parents[2];folder=root/'artifacts/cidade-baixa';folder.mkdir(exist_ok=True)
(folder/'photo_modeling_scope.json').write_text(json.dumps({'file':bpy.data.filepath,'mode':bpy.context.mode,'objects':rows},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'file':bpy.data.filepath,'objects':rows},ensure_ascii=False))
