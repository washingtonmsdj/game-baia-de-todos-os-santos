"""Atualização explícita das dependências dos circuitos recém-criados."""
import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
root.update_tag()
for m in bpy.data.materials:
 if not m.name.startswith('HILUX22') or not m.use_nodes:continue
 if m.node_tree.animation_data:
  for f in m.node_tree.animation_data.drivers:f.driver.expression=f.driver.expression
 m.node_tree.update_tag();m.update_tag()
for ob in s.objects:
 if ob.type=='LIGHT' and ob.name.startswith('HILUX22'):ob.data.update_tag()
s.frame_set(10);s.frame_set(9);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();dg.update();data=[]
for m in bpy.data.materials:
 if not m.name.startswith('HILUX22') or not m.use_nodes:continue
 ev=m.evaluated_get(dg);nt=ev.node_tree.evaluated_get(dg)
 data.append({'name':m.name,'original':m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value,'evaluated':nt.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value,'valid':[f.driver.is_valid for f in m.node_tree.animation_data.drivers]})
(r/'artifacts/vehicles/rondesp/v22-light-driver-refreshed.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data,ensure_ascii=False))
