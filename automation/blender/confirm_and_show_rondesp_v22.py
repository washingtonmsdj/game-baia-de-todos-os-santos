"""Reabertura final e apresentação das piscadas na única janela."""
import bpy,json,hashlib,struct,os
from pathlib import Path
r=Path(__file__).resolve().parents[2];out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v22_luzes.blend';rp=r/'docs/reports/blender/rondesp_marrom_v22.json'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve() and not bpy.app.is_job_running('RENDER')
bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura'];report=json.loads(rp.read_text(encoding='utf8'))
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in report['protected_mesh_hashes'].items())
assert hashlib.sha256(out.read_bytes()).hexdigest()==report['sha256']
# Garantir atualização das dependências, sem modificar a expressão persistida.
for mat in bpy.data.materials:
 if mat.name.startswith('HILUX22') and mat.use_nodes and mat.node_tree.animation_data:
  for f in mat.node_tree.animation_data.drivers:f.driver.expression=f.driver.expression
  mat.node_tree.update_tag();mat.update_tag()
for ob in s.objects:
 if ob.type=='LIGHT' and ob.name.startswith('HILUX22'):
  for f in ob.data.animation_data.drivers:f.driver.expression=f.driver.expression
  ob.data.update_tag()
root.update_tag();s.frame_set(10);s.frame_set(9);bpy.context.view_layer.update()
assert all(s.objects[n].data.energy>0 for n in report['headlight_energy_on'])
report.update({'source_reopened':True,'source_sha256_after_reopen':hashlib.sha256(out.read_bytes()).hexdigest(),'protected_meshes_verified_after_reopen':True,'objects':len(s.objects),'visual_review':'Vistas finais de montagem, duas fases do giroflex, freio e encaixes inspecionadas; fidelidade fina permanece candidata.','live_session':{'pid':os.getpid(),'port':9876},'driver_dependencies_refreshed':True,'material_preview_enabled':all(a.spaces.active.shading.type=='MATERIAL' for sc in bpy.data.screens for a in sc.areas if a.type=='VIEW_3D')})
# Iniciar a animação visual das piscadas; a geometria do veículo fica estacionada.
playing=False
try:
 window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
 s.sync_mode='FRAME_DROP'
 if not window.screen.is_animation_playing:
  with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.screen.animation_play()
 playing=window.screen.is_animation_playing
except (RuntimeError,StopIteration,AttributeError) as ex:
 report['playback_note']=str(ex)
report['live_flashing_playback']=playing
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':str(out),'sha256':report['sha256'],'reopened':True,'body_and_doors_preserved':True,'flashing_playback':playing}))
