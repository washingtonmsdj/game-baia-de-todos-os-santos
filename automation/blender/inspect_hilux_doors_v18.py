"""Inventário somente leitura dos conjuntos de portas, na sessão visível."""
import bpy,json,hashlib,struct,collections
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]; s=bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name=='hilux_carroceria_v17.blend'
body=s.objects['HILUX | CARROCERIA PRINCIPAL']
def fingerprint(ob):
 h=hashlib.sha256()
 if ob.type=='MESH':
  for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
  for p in ob.data.polygons:
   h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
def info(ob):
 bb=[ob.matrix_world@Vector(p) for p in ob.bound_box] if ob.type=='MESH' else [ob.matrix_world.translation]
 return {'name':ob.name,'type':ob.type,'collections':[c.name for c in ob.users_collection],'parent':ob.parent.name if ob.parent else None,
 'location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),
 'bounds':[[min(p[i] for p in bb),max(p[i] for p in bb)] for i in range(3)],
 'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,'faces':len(ob.data.polygons) if ob.type=='MESH' else None,
 'children':[c.name for c in ob.children],'modifiers':[(m.name,m.type) for m in ob.modifiers],
 'properties':{k:str(v) for k,v in ob.items()},'mesh_hash':fingerprint(ob)}
parts=[o for o in s.objects if any(word in o.name.lower() for word in ['porta','caixilh','maçan','macan','acabamento b','vidro lateral'])]
labels=json.loads(body['boas_panel_id_map']);attr=body.data.attributes['boas_panel_id']; borders={}
for name in ['HILUX15 | Batente dianteiro ligado ao contorno','HILUX15 | Batente traseiro ligado ao contorno']:
 pid=next(int(k) for k,v in labels.items() if v==name)
 counts=collections.Counter()
 for p in body.data.polygons:
  if attr.data[p.index].value==pid:
   vs=list(p.vertices)
   counts.update(tuple(sorted((a,b))) for a,b in zip(vs,vs[1:]+vs[:1]))
 edges=[list(e) for e,n in counts.items() if n==1];ids=sorted({v for e in edges for v in e})
 borders[name]={'edges':edges,'vertices':{str(v):list(body.data.vertices[v].co) for v in ids}}
data={'source_file':Path(bpy.data.filepath).relative_to(r).as_posix(),'scene':s.name,'body_hash':fingerprint(body),'parts':[info(o) for o in parts],
 'materials':[m.name for m in bpy.data.materials],'borders':borders,'protected_objects':{o.name:fingerprint(o) for o in s.objects if o.type=='MESH'}}
out=r/'artifacts/vehicles/rondesp/v18-doors-before.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'inventory':str(out.relative_to(r)),'parts':len(parts),'body_hash':data['body_hash']}))
