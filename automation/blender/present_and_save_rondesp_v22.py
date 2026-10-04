"""Salva V22 e apresenta circuitos ligados, duas fases do giroflex e freio."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v21_montada.blend' and s.get('boas_v22_lights_applied')
assert not bpy.app.is_job_running('RENDER')
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v22_luzes.blend';assert not out.exists()
rp=r/'docs/reports/blender/rondesp_marrom_v22.json';report=json.loads(rp.read_text(encoding='utf8'))
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in report['protected_mesh_hashes'].items())
s.name='VIATURA | Rondesp Hilux marrom v22';s['boas_revision_parent']=report['parent']
s['boas_authoring_notes']='V22: carroceria/portas V20 preservadas, montagem V21 mantida. Lanternas, puxador, terceira luz e suportes ajustados às superfícies atuais. Giroflex azul esquerdo/vermelho direito com drivers; faróis, lanternas e freio com controles no root. Sem runtime, testes gerais ou build.'
s['boas_review_status']='candidate; lighting and attachment review'
s.frame_set(9);root['freio']=0.;root['giroflex_ligado']=1.;root['farois_ligados']=1.;root['lanternas_ligadas']=1.
s.render.engine='BLENDER_EEVEE'
if hasattr(s,'eevee'):
 if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=96
 # Traçado habilitado para transmissão das lentes, quando suportado pelo motor.
 if hasattr(s.eevee,'use_raytracing'):s.eevee.use_raytracing=True
s.render.resolution_x=1280;s.render.resolution_y=850;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.exposure=.20
cam=s.camera;cam.location=(-7,-8,3.1);cam.rotation_euler=(Vector((0,.15,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.8
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_location=(0,.15,1.04);sp.region_3d.view_distance=7.;sp.region_3d.view_perspective='PERSP';sp.shading.type='MATERIAL';sp.shading.use_scene_lights=True;sp.shading.use_scene_world=True
bpy.context.view_layer.update()
# Leitura dos drivers nas duas fases e do circuito de freio.
readings=[]
for frame,brake in [(1,0.),(11,0.),(9,1.)]:
 root['freio']=brake;root.update_tag();s.frame_set(frame);bpy.context.view_layer.update()
 row={'frame':frame,'brake_control':brake,'materials':{},'lights':{}}
 for cfg in report['lighting_materials']:
  mat=bpy.data.materials[cfg['material']];sock=mat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'];row['materials'][mat.name]=sock.default_value
  assert all(not curve.driver.is_valid==False for curve in mat.node_tree.animation_data.drivers),mat.name
 for name in report['projection_lights']:row['lights'][name]=s.objects[name].data.energy
 readings.append(row)
root['freio']=0.;root.update_tag();s.frame_set(9);bpy.context.view_layer.update()
report.update({'file':out.relative_to(r).as_posix(),'scene':s.name,'source_reopened':False,'driver_readings':readings,'visual_review':'pending','live_session':{'port':9876},'preview_paths':{'assembled':'artifacts/vehicles/rondesp/v22-frente-completa.png','blue_phase':'artifacts/vehicles/rondesp/v22-giroflex-azul.png','red_phase':'artifacts/vehicles/rondesp/v22-giroflex-vermelho.png','brake':'artifacts/vehicles/rondesp/v22-traseira-freio.png','rear_fit':'artifacts/vehicles/rondesp/v22-encaixes-traseiros.png'}})
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Fonte V22 salva: '+report['sha256'])
original_cam=cam.matrix_world.copy();original_scale=cam.data.ortho_scale;expo=s.view_settings.exposure
background=s.world.node_tree.nodes.get('Background');worldstrength=background.inputs['Strength'].default_value
studio_lights=[o.data for o in bpy.data.collections['RDP01 | APRESENTACAO'].objects if o.type=='LIGHT'];energies=[a.energy for a in studio_lights]
try:
 s.frame_set(9);s.render.filepath=str(r/report['preview_paths']['assembled']);bpy.ops.render.render(write_still=True)
 # Iluminação de estúdio reduzida apenas durante as vistas de funcionamento.
 for light,power in zip(studio_lights,energies):light.energy=power*.18
 background.inputs['Strength'].default_value=worldstrength*.16;s.view_settings.exposure=0.
 for name,frame in [('blue_phase',1),('red_phase',11)]:
  s.frame_set(frame);s.render.filepath=str(r/report['preview_paths'][name]);bpy.ops.render.render(write_still=True)
 root['freio']=1.;root.update_tag();s.frame_set(9);bpy.context.view_layer.update()
 cam.location=(-7,8,3.25);cam.rotation_euler=(Vector((0,.25,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.7
 s.render.filepath=str(r/report['preview_paths']['brake']);bpy.ops.render.render(write_still=True)
 for light,power in zip(studio_lights,energies):light.energy=power
 background.inputs['Strength'].default_value=worldstrength;s.view_settings.exposure=expo
 root['freio']=0.;root['giroflex_ligado']=0.;root['lanternas_ligadas']=0.;root['farois_ligados']=0.;root.update_tag();s.frame_set(9)
 cam.location=(-4,6,2.2);cam.rotation_euler=(Vector((0,2.55,1.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.6
 s.render.filepath=str(r/report['preview_paths']['rear_fit']);bpy.ops.render.render(write_still=True)
finally:
 cam.matrix_world=original_cam;cam.data.ortho_scale=original_scale;s.view_settings.exposure=expo
 for light,power in zip(studio_lights,energies):light.energy=power
 background.inputs['Strength'].default_value=worldstrength
 root['freio']=0.;root['giroflex_ligado']=1.;root['lanternas_ligadas']=1.;root['farois_ligados']=1.;root.update_tag();s.frame_set(9)
print(json.dumps({'file':str(out),'views':list(report['preview_paths'].values()),'driver_readings':readings}))
