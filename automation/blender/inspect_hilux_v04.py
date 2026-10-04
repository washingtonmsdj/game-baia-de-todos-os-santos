import bpy,json
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
report=[]
for o in scene.objects:
    if o.type=='FONT' or any(t in o.name for t in ['roda','pneu','quebra','Quebra','Para-choque','sinalizador','Barra']):
        report.append({'name':o.name,'type':o.type,'loc':list(o.location),'parent':o.parent.name if o.parent else None,'bounds': [[min((o.matrix_world@Vector(p))[a] for p in o.bound_box),max((o.matrix_world@Vector(p))[a] for p in o.bound_box)] for a in range(3)]})
(Path(__file__).resolve().parents[2]/'artifacts/vehicles/rondesp/v04-inspect.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
