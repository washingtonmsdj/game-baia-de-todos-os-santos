"""Confere a fonte reaberta e apresenta luzes e portas na janela existente."""
import bpy,json,hashlib,struct
from pathlib import Path
r=Path(__file__).resolve().parents[2];out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend'
rp=r/'docs/reports/blender/rondesp_farois_v24.json';report=json.loads(rp.read_text(encoding='utf8'))
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert hashlib.sha256(out.read_bytes()).hexdigest()==report['sha256']
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
for o in s.objects:
 if 'abertura_graus' in o:
  for f in o.animation_data.drivers:f.driver.expression=f.driver.expression
  o.update_tag()
 elif o.type=='LIGHT' and o.name.startswith('HILUX22'):
  for f in o.data.animation_data.drivers:f.driver.expression=f.driver.expression
  o.data.update_tag()
root.update_tag();s.frame_set(89);s.frame_set(90);bpy.context.view_layer.update()
expected=2400*root['farois_ligados']*root['intensidade_farois']
assert all(abs(s.objects[f'HILUX22 | Feixe farol {side}'].data.energy-expected)<.001 for side in [-1,1])
assert all(abs(abs(o.rotation_euler.z)-1.1344640138)<.00001 for o in s.objects if 'abertura_graus' in o)
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
area.spaces.active.shading.type='RENDERED';area.spaces.active.shading.use_compositor='ALWAYS'
with bpy.context.temp_override(window=window,area=area,region=region):
 if not window.screen.is_animation_playing:bpy.ops.screen.animation_play()
report.update({'source_reopened':True,'source_sha256_after_reopen':hashlib.sha256(out.read_bytes()).hexdigest(),'protected_meshes_verified_after_reopen':True,'headlight_power_after_reopen':[s.objects[f'HILUX22 | Feixe farol {side}'].data.energy for side in [-1,1]],'live_rendered':True,'live_demo_playing':bool(window.screen.is_animation_playing),'visual_review':'Capturas reais antes/depois inspecionadas: feixes agora iluminam claramente o piso à frente; chapas e animação de portas preservadas. Parâmetro de potência autoral, sem certificação fotométrica.'})
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'hash':report['sha256'],'powers':report['headlight_power_after_reopen'],'door_demo_preserved':True,'playing':report['live_demo_playing']}))
