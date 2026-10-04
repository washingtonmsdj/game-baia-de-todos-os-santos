"""Conclui os circuitos e os compartimentos das lanternas; mantém V22 em revisão."""
import bpy,bmesh,hashlib,json,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura'];out=Path(bpy.data.filepath)
assert not bpy.app.background and out.name=='marrom_v22_luzes.blend' and not bpy.app.is_job_running('RENDER')
assert not s.get('boas_v22_light_finish')
rp=r/'docs/reports/blender/rondesp_marrom_v22.json';report=json.loads(rp.read_text(encoding='utf8'))
checkpoint=r/'artifacts/vehicles/rondesp/v22-before-light-finish.blend';assert not checkpoint.exists();bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
expressions={'HILUX22 | Lanterna posicao vermelha':'.35*pos','HILUX22 | Lanterna e freio vermelhos':'.50*pos+2.4*freia','HILUX22 | Terceira luz freio':'2.4*freia','HILUX22 | Lente farol iluminada':'.04*aceso'}
for name,expr in expressions.items():
 mat=bpy.data.materials[name];mat.node_tree.animation_data.drivers[0].driver.expression=expr
 for cfg in report['lighting_materials']:
  if cfg['material']==name:cfg['expression']=expr
# Compartimento branco entre os segmentos vermelhos, seguindo o modelo existente.
clear=bpy.data.materials['RDP01 | Lentes transparentes'].copy();clear.name='HILUX22 | Compartimento claro lanterna'
bs=clear.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.44,.47,.48,1);bs.inputs['Roughness'].default_value=.16;bs.inputs['Metallic'].default_value=.10;bs.inputs['Transmission Weight'].default_value=.30;clear.diffuse_color=(.44,.47,.48,1)
segmented=[]
for side in [-1,1]:
 for key in ['Lente vermelha traseira','Retorno lanterna']:
  ob=s.objects[f'RDP01 | HILUX06 | {key} {side}'];mw=ob.matrix_world.copy();im=mw.inverted();bm=bmesh.new();bm.from_mesh(ob.data)
  for v in bm.verts:v.co=mw@v.co
  for height in [.898,.989]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,height)),plane_no=Vector((0,0,1)),clear_inner=False,clear_outer=False)
  for f in bm.faces:
   z=f.calc_center_median().z;f.material_index=0 if z>.989 else 2 if z>.898 else 1
  for v in bm.verts:v.co=im@v.co
  bm.to_mesh(ob.data);bm.free();ob.data.materials.clear()
  for material in [bpy.data.materials['HILUX22 | Lanterna e freio vermelhos'],bpy.data.materials['HILUX22 | Lanterna posicao vermelha'],clear]:ob.data.materials.append(material)
  ob.data.update();ob['boas_light_role']='upper tail/brake; middle clear compartment; lower position';segmented.append(ob.name)
# Forçar a atualização também dos drivers de potência dos faróis.
for ob in s.objects:
 if ob.type=='LIGHT' and ob.name.startswith('HILUX22'):
  for f in ob.data.animation_data.drivers:f.driver.expression=f.driver.expression
  ob.data.update_tag()
for m in bpy.data.materials:
 if m.name.startswith('HILUX22') and m.use_nodes and m.node_tree.animation_data:
  for f in m.node_tree.animation_data.drivers:f.driver.expression=f.driver.expression
  m.node_tree.update_tag();m.update_tag()
root.update_tag();s.frame_set(10);s.frame_set(9);bpy.context.view_layer.update()
head_energy={name:s.objects[name].data.energy for name in report['projection_lights'] if 'Feixe' in name}
assert all(power>0 for power in head_energy.values()),head_energy
s['boas_v22_light_finish']=True
report.update({'rear_lens_compartments':segmented,'headlight_energy_on':head_energy,'finish_note':'Lentes dianteiras com emissão discreta para preservar óptica. Lanternas divididas em vermelho/claro/vermelho, freio no segmento superior; potência dos feixes atualizada.'})
for cfg in report['lighting_materials']:
 mat=bpy.data.materials[cfg['material']]
 assert all(f.driver.is_valid for f in mat.node_tree.animation_data.drivers),mat.name
# Nova leitura dos parâmetros finais, incluindo faróis realmente projetados.
readings=[]
for frame,brake in [(1,0.),(11,0.),(9,1.)]:
 root['freio']=brake;root.update_tag();s.frame_set(frame);bpy.context.view_layer.update()
 readings.append({'frame':frame,'brake_control':brake,'materials':{cfg['material']:bpy.data.materials[cfg['material']].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for cfg in report['lighting_materials']},'lights':{name:s.objects[name].data.energy for name in report['projection_lights']}})
root['freio']=0.;root.update_tag();s.frame_set(9);bpy.context.view_layer.update();report['driver_readings_final']=readings
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False;rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Apresentação atualizada com os parâmetros finais, na única janela.
cam=s.camera;original_cam=cam.matrix_world.copy();original_scale=cam.data.ortho_scale;expo=s.view_settings.exposure;background=s.world.node_tree.nodes.get('Background');strength=background.inputs['Strength'].default_value
studio=[o.data for o in bpy.data.collections['RDP01 | APRESENTACAO'].objects if o.type=='LIGHT'];energies=[a.energy for a in studio]
try:
 s.render.filepath=str(r/report['preview_paths']['assembled']);bpy.ops.render.render(write_still=True)
 for light,power in zip(studio,energies):light.energy=power*.18
 background.inputs['Strength'].default_value=strength*.16;s.view_settings.exposure=0.
 for name,frame in [('blue_phase',1),('red_phase',11)]:
  s.frame_set(frame);s.render.filepath=str(r/report['preview_paths'][name]);bpy.ops.render.render(write_still=True)
 root['freio']=1.;root.update_tag();s.frame_set(9);bpy.context.view_layer.update()
 cam.location=(-7,8,3.25);cam.rotation_euler=(Vector((0,.25,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.7;s.render.filepath=str(r/report['preview_paths']['brake']);bpy.ops.render.render(write_still=True)
 for light,power in zip(studio,energies):light.energy=power
 background.inputs['Strength'].default_value=strength;s.view_settings.exposure=expo
 for key in ['giroflex_ligado','lanternas_ligadas','farois_ligados','freio']:root[key]=0.
 root.update_tag();s.frame_set(9);bpy.context.view_layer.update()
 cam.location=(-4,6,2.2);cam.rotation_euler=(Vector((0,2.55,1.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.6;s.render.filepath=str(r/report['preview_paths']['rear_fit']);bpy.ops.render.render(write_still=True)
finally:
 cam.matrix_world=original_cam;cam.data.ortho_scale=original_scale;s.view_settings.exposure=expo
 for light,power in zip(studio,energies):light.energy=power
 background.inputs['Strength'].default_value=strength
 for key in ['giroflex_ligado','lanternas_ligadas','farois_ligados']:root[key]=1.
 root['freio']=0.;root.update_tag();s.frame_set(9);bpy.context.view_layer.update()
print(json.dumps({'sha256':report['sha256'],'headlight_energy_on':head_energy,'compartments':segmented}))
