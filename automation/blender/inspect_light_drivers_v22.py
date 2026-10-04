"""Inspeção read-only dos circuitos antes da apresentação."""
import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura'];data=[]
for m in bpy.data.materials:
 if not m.name.startswith('HILUX22') or not m.use_nodes:continue
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
 data.append({'name':m.name,'emission':bs.inputs['Emission Strength'].default_value,'drivers':[{'expression':f.driver.expression,'valid':f.driver.is_valid,'path':f.data_path,'mute':f.mute,'vars':[{'name':v.name,'id':v.targets[0].id.name if v.targets[0].id else None,'path':v.targets[0].data_path,'value':v.targets[0].id.path_resolve(v.targets[0].data_path) if v.targets[0].id else None} for v in f.driver.variables]} for f in nt.animation_data.drivers] if nt.animation_data else []})
(r/'artifacts/vehicles/rondesp/v22-light-driver-inspection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data,ensure_ascii=False))
