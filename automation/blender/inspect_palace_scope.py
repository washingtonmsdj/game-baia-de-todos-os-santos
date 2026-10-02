"""Inspeção limitada da arquitetura Cidade Alta, via MCP na sessão adotada."""
import bpy, json
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
bpy.context.view_layer.update()
rows=[]
for o in scene.objects:
    t=(o.name+' '+' '.join(c.name for c in o.users_collection)).lower()
    if any(s in t for s in ('rio branco','rio-branco','galeria','arcos','arcada','palácio','palacio','tomé','tome','praça alta','praca alta')):
        pts=[o.matrix_world@Vector(p) for p in o.bound_box] if o.type not in ('EMPTY','LIGHT','CAMERA') else [o.matrix_world.translation]
        rows.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],
            location=list(o.matrix_world.translation),rotation=list(o.rotation_euler),
            bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],
            materials=[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],
            properties={k:o[k] for k in o.keys() if isinstance(o[k],(str,int,float,bool))},
            hidden=o.hide_get() or o.hide_viewport or o.hide_render,
            vertices=len(o.data.vertices) if o.type=='MESH' else None))
path=Path(bpy.data.filepath).resolve().parents[1]/'artifacts/palacio-rio-branco/scope_before.json'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
details=[]
for o in scene.objects:
    if o.type=='MESH' and (o.name.startswith(('RIO BRANCO | corpo','RIO BRANCO | embasamento','RIO BRANCO | pavilhão','RIO BRANCO | tambor','RIO BRANCO | janela térrea','Encosta |','ENCOSTA |','LAC R30B08 | apoio','PRAÇA | OSM','OSM | Pal','OSM | Secretaria')) or o.get('osm_way_id') in ('402383814','1263035782')):
        details.append({'name':o.name,'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'properties':{k:o[k] for k in o.keys() if isinstance(o[k],(str,int,float,bool))},'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices] if len(o.data.vertices)<100 else None})
(path.parent/'architecture_frames.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(file=bpy.data.filepath,objects=len(rows),frames=[(o['name'],len(o['vertices'] or [])) for o in details]),ensure_ascii=False))
