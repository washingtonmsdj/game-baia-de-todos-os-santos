"""Inspeção da fonte ativa na única janela; preserva sessão prévia não salva."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
contract = json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
source = root / contract['world_source']['file']
if Path(bpy.data.filepath) != source:
    if bpy.data.is_dirty:
        backup = root/'artifacts/urban-slice/session-before.blend'
        backup.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(backup), copy=True)
    bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
result={'source':contract['world_source'],'scene':scene.name,'collections':[c.name for c in bpy.data.collections], 'objects':[]}
for o in scene.objects:
    if o.type not in {'MESH','CURVE'}:continue
    b=[o.matrix_world@Vector(v) for v in o.bound_box]
    lo=[min(v[i] for v in b) for i in range(3)]; hi=[max(v[i] for v in b) for i in range(3)]
    if hi[0]>-260 and lo[0]<40 and hi[1]>0 and lo[1]<220:
        result['objects'].append({'name':o.name,'bounds':[lo,hi],'visible':o.visible_get(),'materials':[m.name for m in o.data.materials if m], 'collections':[c.name for c in o.users_collection]})
p=root/'artifacts/urban-slice/inspection.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False))
print(json.dumps({'scene':scene.name,'nearby_objects':len(result['objects']),'report':str(p)}))
