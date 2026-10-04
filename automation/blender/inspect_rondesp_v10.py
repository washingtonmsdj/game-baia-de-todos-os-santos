"""Inventário para revisão traseira e inscrições; não altera geometria."""
import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]
rows=[]
for o in bpy.context.scene.objects:
    if any(c.name in ['RDP01 | CAPOTA','RDP01 | INSCRICOES','RDP01 | LUZES','RDP01 | ACABAMENTOS'] for c in o.users_collection):
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        rows.append({'name':o.name,'type':o.type,'location':list(o.location),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'text':o.data.body if o.type=='FONT' else o.get('boas_inscription_text'), 'visible':not o.hide_get()})
(r/'artifacts/vehicles/rondesp/v10-before.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
