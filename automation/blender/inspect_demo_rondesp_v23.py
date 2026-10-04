"""Diagnóstico dos controles e da visualização na única janela."""
import bpy,json,hashlib,os
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pid':os.getpid(),'frame':s.frame_current,'range':[s.frame_start,s.frame_end],'engine':s.render.engine,'autoexec_fail':getattr(bpy.app,'autoexec_fail',None),'autoexec_message':getattr(bpy.app,'autoexec_fail_message',None),'windows':[],'doors':[],'light_materials':[],'light_objects':[],'controls':dict(s.objects['RDP01_ROOT | viatura'].items())}
for w in bpy.context.window_manager.windows:
 row={'screen':w.screen.name,'playing':w.screen.is_animation_playing,'viewports':[]}
 for a in w.screen.areas:
  if a.type=='VIEW_3D':
   sp=a.spaces.active
   row['viewports'].append({'mode':sp.shading.type,'scene_lights':sp.shading.use_scene_lights,'scene_world':sp.shading.use_scene_world,'view':sp.region_3d.view_perspective,'compositor':getattr(sp.shading,'use_compositor',None)})
 out['windows'].append(row)
for o in s.objects:
 if 'abertura_graus' in o:
  out['doors'].append({'pivot':o.name,'opening':o['abertura_graus'],'rotation':list(o.rotation_euler),'children':[c.name for c in o.children],'drivers':[{'path':f.data_path,'expression':f.driver.expression,'valid':f.driver.is_valid} for f in o.animation_data.drivers] if o.animation_data else []})
 if o.get('boas_light_role') or (o.type=='LIGHT' and o.name.startswith('HILUX22')):
  out['light_objects'].append({'name':o.name,'type':o.type,'hidden':o.hide_get(),'viewport':o.hide_viewport,'render':o.hide_render,'visible':o.visible_get(),'energy':o.data.energy if o.type=='LIGHT' else None})
for m in bpy.data.materials:
 if m.name.startswith('HILUX22') and m.use_nodes:
  n=m.node_tree.nodes.get('Principled BSDF')
  if n:
   out['light_materials'].append({'name':m.name,'emission':n.inputs['Emission Strength'].default_value,'color':list(n.inputs['Emission Color'].default_value),'drivers':[{'path':f.data_path,'expression':f.driver.expression,'valid':f.driver.is_valid} for f in m.node_tree.animation_data.drivers] if m.node_tree.animation_data else []})
out['studio_lights']=[{'name':o.name,'energy':o.data.energy,'visible':o.visible_get()} for o in s.objects if o.type=='LIGHT' and not o.name.startswith('HILUX22')]
p=r/'artifacts/vehicles/rondesp/v23-demo-before.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
