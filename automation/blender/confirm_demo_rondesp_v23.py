"""Reabre a revisão da demonstração e captura a própria janela visível."""
import bpy, json, hashlib, struct
from pathlib import Path
r=Path(__file__).resolve().parents[2]
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend'
rp=r/'docs/reports/blender/rondesp_demonstracao_v23.json'
report=json.loads(rp.read_text(encoding='utf8'))
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert hashlib.sha256(out.read_bytes()).hexdigest()==report['sha256']
bpy.ops.wm.open_mainfile(filepath=str(out))
s=bpy.context.scene; root=s.objects['RDP01_ROOT | viatura']
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
doors=[o for o in s.objects if 'abertura_graus' in o]
assert all(abs(abs(o.rotation_euler.z)-1.1344640138)<.00001 for o in doors)
assert all(f.driver.is_valid for o in doors for f in o.animation_data.drivers)
report['source_reopened']=True;report['protected_meshes_verified_after_reopen']=True
report['source_sha256_after_reopen']=hashlib.sha256(out.read_bytes()).hexdigest()
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
report['rendered_viewport']=area.spaces.active.shading.type=='RENDERED'
report['viewport_compositor']=area.spaces.active.shading.use_compositor
shot=r/'artifacts/vehicles/rondesp/v23-portas-abertas-viewport.png'
try:
 with bpy.context.temp_override(window=window,area=area,region=region):
  bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
  bpy.ops.screen.screenshot(filepath=str(shot))
 report['viewport_capture']=shot.relative_to(r).as_posix()
except (RuntimeError,AttributeError) as ex:report['viewport_capture_note']=str(ex)
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'four_doors_open':True,'rendered':report['rendered_viewport'],'compositor':report['viewport_compositor'],'capture':report.get('viewport_capture'),'note':report.get('viewport_capture_note'),'sha256':report['sha256']}))
