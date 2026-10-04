"""Salva uma prévia de material persistente e ativa Renderizado depois da reabertura."""
import bpy,json,hashlib,struct
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend'
rp=r/'docs/reports/blender/rondesp_demonstracao_v23.json';report=json.loads(rp.read_text(encoding='utf8'))
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   sp=a.spaces.active;sp.shading.type='MATERIAL';sp.shading.use_scene_lights=True;sp.shading.use_scene_world=True
   sp.shading.use_compositor='ALWAYS';sp.region_3d.view_camera_offset=(0.,0.);sp.region_3d.view_camera_zoom=20.
report['rendered_reset_on_reopen_observed']=True
s.frame_set(90)
notes=bpy.data.texts['HILUX23 | COMO VER A DEMONSTRACAO']
notes.write('\nAo reabrir: Z → R ativa a iluminação completa. Blender pode resetar Renderizado para Sólido ao carregar.\nA fonte é salva em Prévia de material para manter as cores na reabertura.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in report['protected_mesh_hashes'].items())
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
report['saved_reopen_shading']=area.spaces.active.shading.type
for a in window.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.shading.type='RENDERED';a.spaces.active.shading.use_compositor='ALWAYS'
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
root.update_tag();report['viewport_captures']={}
for name,frame in [('azul-portas-fechadas',1),('vermelho-portas-fechadas',19),('portas-abertas',90)]:
 s.frame_set(frame);bpy.context.view_layer.update()
 with bpy.context.temp_override(window=window,area=area,region=region):
  bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=3)
  shot=r/f'artifacts/vehicles/rondesp/v23-{name}-viewport.png'
  bpy.ops.screen.screenshot(filepath=str(shot))
 report['viewport_captures'][name]=shot.relative_to(r).as_posix()
report['source_reopened']=True;report['source_sha256_after_reopen']=hashlib.sha256(out.read_bytes()).hexdigest()
report['protected_meshes_verified_after_reopen']=True;report['rendered_viewport']=area.spaces.active.shading.type=='RENDERED'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'sha256':report['sha256'],'reopened':True,'saved_reopen_shading':report['saved_reopen_shading'],'live_rendered':report['rendered_viewport'],'images':report['viewport_captures']}))
