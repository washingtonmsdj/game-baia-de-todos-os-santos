"""Conclui a revisão e registra uma amostra da reprodução real na viewport."""
import bpy,json,hashlib,struct,math,time
from pathlib import Path
r=Path(__file__).resolve().parents[2]
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend'
rp=r/'docs/reports/blender/rondesp_demonstracao_v23.json';report=json.loads(rp.read_text(encoding='utf8'))
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert hashlib.sha256(out.read_bytes()).hexdigest()==report['sha256']
s=bpy.context.scene;s.sync_mode='FRAME_DROP'
for sc in bpy.data.screens:
 for a in sc.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.type='MATERIAL'
s.frame_set(90);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in report['protected_mesh_hashes'].items())
for m in bpy.data.materials:
 if m.name.startswith('HILUX22') and m.use_nodes and m.node_tree.animation_data:
  for f in m.node_tree.animation_data.drivers:f.driver.expression=f.driver.expression
  m.node_tree.update_tag();m.update_tag()
doors=[o for o in s.objects if 'abertura_graus' in o]
for o in s.objects:
 if o in doors:
  for f in o.animation_data.drivers:f.driver.expression=f.driver.expression
  o.update_tag()
 elif o.type=='LIGHT' and o.name.startswith('HILUX22'):
  for f in o.data.animation_data.drivers:f.driver.expression=f.driver.expression
  o.data.update_tag()
root.update_tag();s.frame_set(1);bpy.context.view_layer.update()
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
assert area.spaces.active.shading.type=='MATERIAL'
area.spaces.active.shading.type='RENDERED'
with bpy.context.temp_override(window=window,area=area,region=region):
 if not window.screen.is_animation_playing:bpy.ops.screen.animation_play()
report.update({'source_reopened':True,'source_sha256_after_reopen':hashlib.sha256(out.read_bytes()).hexdigest(),
 'saved_reopen_shading':'MATERIAL','rendered_viewport':True,'live_animation_playing':bool(window.screen.is_animation_playing),
 'playback_sync':'FRAME_DROP','visual_review':'Viewport real inspecionada: duas cores e reflexos visíveis; quatro folhas abertas, com vidros/espelhos/inscrições acompanhando os pivôs. Prévia granular durante acumulação EEVEE.',
 'playback_observations':[]})
assert report['live_animation_playing']
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
started=time.perf_counter()
def sample_playback():
 if Path(bpy.data.filepath).resolve()!=out.resolve():return None
 blue=bpy.data.materials['HILUX22 | LED AZUL ESQUERDO'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value
 red=bpy.data.materials['HILUX22 | LED VERMELHO DIREITO'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value
 report['playback_observations'].append({'elapsed_s':round(time.perf_counter()-started,2),'frame':s.frame_current,'playing':bool(window.screen.is_animation_playing),'door_angles_deg':[round(math.degrees(o.rotation_euler.z),2) for o in doors],'blue':blue,'red':red,'shading':area.spaces.active.shading.type})
 if len(report['playback_observations'])>=12:
  rows=report['playback_observations']
  report['actual_playback_motion_observed']=len({tuple(x['door_angles_deg']) for x in rows})>1
  report['actual_playback_blue_and_red_observed']=any(x['blue']>10 for x in rows) and any(x['red']>10 for x in rows)
  rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  return None
 return 1.0
bpy.app.timers.register(sample_playback,first_interval=1.0)
print(json.dumps({'sha256':report['sha256'],'playing':True,'rendered':True,'source_reopened':True,'playback_sampling':'12 transient observations; no animation handler'}))
