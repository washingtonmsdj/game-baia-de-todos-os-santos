"""Inventário read-only da oficina para remontagem da viatura."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name in {'hilux_chapa_v20.blend','marrom_v21_montada.blend'}
def info(o):
 bb=[o.matrix_world@Vector(p) for p in o.bound_box] if o.type in {'MESH','CURVE','FONT'} else []
 return {'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,'hide_set':o.hide_get(),'visible':o.visible_get(),'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'bbox':[[min(p[i] for p in bb) for i in range(3)],[max(p[i] for p in bb) for i in range(3)]] if bb else None,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'properties':{k:str(v) for k,v in o.items() if k.startswith('boas')},'text':o.data.body if o.type=='FONT' else None}
d={'file':bpy.data.filepath,'pid':os.getpid(),'scene':s.name,'objects':[info(o) for o in s.objects],'collections':[{'name':c.name,'hide_viewport':c.hide_viewport,'hide_render':c.hide_render,'children':[ch.name for ch in c.children]} for c in bpy.data.collections],'images':[{'name':i.name,'file':i.filepath,'packed':bool(i.packed_file),'source':i.source,'size':list(i.size)} for i in bpy.data.images],'materials':[{'name':m.name,'color':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if getattr(n,'image',None) else None} for n in m.node_tree.nodes] if m.use_nodes else []} for m in bpy.data.materials]}
(r/'artifacts/vehicles/rondesp/v21-assembly-inventory.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pid':d['pid'],'objects':len(d['objects']),'materials':len(d['materials']),'images':len(d['images'])}))
