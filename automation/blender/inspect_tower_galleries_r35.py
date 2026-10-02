"""Inspeção localizada de apoios e vãos na única sessão visível."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;rows=[]
bpy.context.view_layer.update()
for o in scene.objects:
    name=o.name.lower()
    if not any(k in name for k in ('lacerda','torre','apoio','passarela','galeria','superior','fachada poço','gal r34','rio r34 |')):continue
    if o.type not in ('MESH','CURVE','FONT'):continue
    pts=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else [o.matrix_world@Vector(p) for p in o.bound_box]
    if not pts:continue
    rows.append({'name':o.name,'collections':[c.name for c in o.users_collection],'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'matrix_world':[list(row) for row in o.matrix_world],'properties':{k:str(o[k]) for k in o.keys() if not k.startswith('_')},'hidden':o.hide_render})
p=root/'artifacts/palacio-rio-branco/tower_gallery_scope_r35.json';p.write_text(json.dumps({'file':bpy.data.filepath,'scene':scene.name,'objects':rows},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'objects':len(rows),'report':p.relative_to(root).as_posix()},ensure_ascii=False))
