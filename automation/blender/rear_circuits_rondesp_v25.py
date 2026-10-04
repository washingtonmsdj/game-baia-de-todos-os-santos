"""Separa posição, freio e ré, reutilizando os compartimentos das lanternas existentes."""
import bpy,json,hashlib,struct,os,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
parent=r/'blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend'
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v25_lanternas_re.blend'
rp=r/'docs/reports/blender/rondesp_lanternas_v25.json'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==parent.resolve()
assert not out.exists() and not bpy.app.is_job_running('RENDER')
previous=json.loads((r/'docs/reports/blender/rondesp_farois_v24.json').read_text(encoding='utf8'))
assert hashlib.sha256(parent.read_bytes()).hexdigest()==previous['sha256']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in previous['protected_mesh_hashes'].items())
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
if window.screen.is_animation_playing:
 with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.screen.animation_cancel(restore_frame=False)
report={'asset_id':'vehicle-rondesp-pickup','status':'candidate','parent':parent.relative_to(r).as_posix(),'parent_sha256':previous['sha256'],'protected_mesh_hashes':previous['protected_mesh_hashes'],'geometry_unchanged':True,'diagnosis':'Compartimento claro V22 era estático e não possuía circuito de ré; posição forte reduzia contraste do freio.','factory_lamp_compartment_position':'needs_review; preservado compartimento claro existente, sem alegar correspondência de peça industrial','reference_search':{'toyota_manual_indexed':'https://media.toyota.com.br/5032742a-b1ae-4d27-aaac-134868b9da00.pdf','full_pdf':'403; ano/modelo e posição não verificados, sem uso como planta'},'changed_material_slots':[],'new_lights':[],'checks':[],'source_reopened':False,'runtime_exported':False,'visual_review':'pending'}
root['re_engatada']=0.
root.id_properties_ui('re_engatada').update(min=0.,max=1.,description='0: sem ré; 1: luzes brancas e iluminação para trás. Independente do freio.')
root['demo_re']=0.
root.id_properties_ui('demo_re').update(min=0.,max=1.,description='Canal automático da ré na demonstração; manual com demonstracao_ativa=0.')
for frame,value in [(1,0),(180,0),(190,1),(225,0),(240,0)]:
 root['demo_re']=float(value);root.keyframe_insert(data_path='["demo_re"]',frame=frame,group='Demonstracao portas e freio')
action=root.animation_data.action;curves=list(getattr(action,'fcurves',[]))
if not curves:
 for layer in action.layers:
  for strip in layer.strips:
   bag=strip.channelbag(root.animation_data.action_slot)
   if bag:curves.extend(bag.fcurves)
for f in curves:
 if f.data_path=='["demo_re"]':
  for point in f.keyframe_points:point.interpolation='CONSTANT'
assert any(f.data_path=='["demo_re"]' for f in curves)
def variable(driver,symbol,key):
 v=driver.variables.get(symbol) or driver.variables.new();v.name=symbol;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
brake='(freia*(1-demo)+auto_freio*demo)'
reverse='(re*(1-demo)+auto_re*demo)'
expressions={'HILUX22 | Lanterna posicao vermelha':'.12*pos','HILUX22 | Lanterna e freio vermelhos':'.18*pos+4.0*'+brake,'HILUX22 | Terceira luz freio':'4.0*'+brake}
for name,expr in expressions.items():
 m=bpy.data.materials[name];f=m.node_tree.animation_data.drivers[0]
 if 'Terceira' in name or 'Lanterna e freio' in name:
  for symbol,key in [('freia','freio'),('demo','demonstracao_ativa'),('auto_freio','demo_freio')]:variable(f.driver,symbol,key)
 f.driver.expression=expr;m.node_tree.update_tag();m.update_tag()
clear=bpy.data.materials['HILUX22 | Compartimento claro lanterna']
revmat=clear.copy();revmat.name='HILUX25 | Re branca independente'
bs=revmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.65,.66,.67,1);bs.inputs['Emission Color'].default_value=(1.,.98,.94,1)
bs.inputs['Roughness'].default_value=.18;bs.inputs['Transmission Weight'].default_value=.08
revmat.diffuse_color=(.65,.66,.67,1)
f=bs.inputs['Emission Strength'].driver_add('default_value');f.driver.type='SCRIPTED'
for symbol,key in [('re','re_engatada'),('demo','demonstracao_ativa'),('auto_re','demo_re')]:variable(f.driver,symbol,key)
f.driver.expression='5.0*'+reverse
rear_centers={}
for side in [-1,1]:
 points=[]
 for key in ['Lente vermelha traseira','Retorno lanterna']:
  ob=s.objects[f'RDP01 | HILUX06 | {key} {side}']
  for index,mat in enumerate(ob.data.materials):
   if mat==clear:
    selected=[p for p in ob.data.polygons if p.material_index==index]
    if not selected:
     report.setdefault('unused_clear_slots',[]).append({'object':ob.name,'slot':index})
     continue
    points.extend(ob.matrix_world@ob.data.vertices[v].co for p in selected for v in p.vertices)
    ob.data.materials[index]=revmat
    report['changed_material_slots'].append({'object':ob.name,'slot':index,'polygons':len(selected)})
  ob['boas_light_role']='upper red tail/brake; middle white reverse; lower red position'
 segment=s.objects[f'RDP01 | HILUX06 | Segmento lanterna {str((side,.943))}']
 points.extend(segment.matrix_world@v.co for v in segment.data.vertices)
 segment.data.materials[0]=revmat
 segment['boas_light_role']='reverse_lens'
 report['changed_material_slots'].append({'object':segment.name,'slot':0})
 assert points
 rear_centers[side]=Vector((sum(p.x for p in points)/len(points),max(p.y for p in points)+.06,sum(p.z for p in points)/len(points)))
lightscol=bpy.data.collections['RDP01 | LUZES']
def lamp(name,kind,color,position,expr,vars):
 data=bpy.data.lights.new(name,kind);data.color=color
 ob=bpy.data.objects.new(name,data);lightscol.objects.link(ob);ob.parent=root;ob.location=position
 f=data.driver_add('energy');f.driver.type='SCRIPTED'
 for symbol,key in vars:variable(f.driver,symbol,key)
 f.driver.expression=expr
 ob['boas_asset_id']='vehicle-rondesp-pickup';report['new_lights'].append(name)
 return ob
for side in [-1,1]:
 p=rear_centers[side]
 revlamp=lamp(f'HILUX25 | Feixe de re {side}','SPOT',(1.,.98,.94),p,'220*'+reverse,[('re','re_engatada'),('demo','demonstracao_ativa'),('auto_re','demo_re')])
 revlamp.data.spot_size=math.radians(78);revlamp.data.spot_blend=.55;revlamp.data.shadow_soft_size=.045
 revlamp.rotation_euler=(Vector((p.x+side*.20,p.y+5.,.10))-p).to_track_quat('-Z','Y').to_euler();revlamp['boas_light_role']='reverse_beam'
 spill=lamp(f'HILUX25 | Reflexo posicao e freio {side}','POINT',(1.,.002,.004),(p.x,p.y,1.08),'3*pos+30*'+brake,[('pos','lanternas_ligadas'),('freia','freio'),('demo','demonstracao_ativa'),('auto_freio','demo_freio')])
 spill.data.shadow_soft_size=.05;spill['boas_light_role']='rear_tail_brake_spill'
for name,frame in [('Ré branca ligada',190),('Ré desligada',225)]:
 m=s.timeline_markers.get(name) or s.timeline_markers.new(name,frame=frame);m.frame=frame
def refresh():
 root.update_tag()
 for m in bpy.data.materials:
  if m.name.startswith(('HILUX22','HILUX25')) and m.use_nodes and m.node_tree.animation_data:
   for f in m.node_tree.animation_data.drivers:f.driver.expression=f.driver.expression
   m.node_tree.update_tag();m.update_tag()
 for ob in s.objects:
  if ob.type=='LIGHT' and ob.name.startswith(('HILUX22','HILUX25')):
   for f in ob.data.animation_data.drivers:f.driver.expression=f.driver.expression
   ob.data.update_tag()
refresh()
saved={k:root[k] for k in ['demonstracao_ativa','freio','re_engatada','giroflex_ligado','lanternas_ligadas']}
root['demonstracao_ativa']=0.;root['giroflex_ligado']=0.
cam=s.camera;report['presentation_camera_before']={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale}
cam.location=(-6.2,8.,3.3);cam.rotation_euler=(Vector((0,1.05,1.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.0
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   sp=a.spaces.active;sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_camera_offset=(0.,0.);sp.region_3d.view_camera_zoom=20.
   sp.shading.type='RENDERED';sp.shading.use_compositor='ALWAYS';sp.shading.use_scene_lights=True;sp.shading.use_scene_world=True
report['preview_paths']={}
for index,(name,pos,stop,rev) in enumerate([('posicao',1.,0.,0.),('freio',1.,1.,0.),('re',1.,0.,1.),('freio-e-re',1.,1.,1.),('tudo-desligado',0.,0.,0.)]):
 root['lanternas_ligadas']=pos;root['freio']=stop;root['re_engatada']=rev;root.update_tag();s.frame_set(index+1);bpy.context.view_layer.update()
 values={m:bpy.data.materials[m].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for m in [*expressions,revmat.name]}
 powers={n:s.objects[n].data.energy for n in report['new_lights']}
 assert abs(values[revmat.name]-5*rev)<.0001
 assert abs(values['HILUX22 | Lanterna e freio vermelhos']-(.18*pos+4*stop))<.0001
 assert abs(values['HILUX22 | Terceira luz freio']-4*stop)<.0001
 assert all(abs(powers[f'HILUX25 | Feixe de re {side}']-220*rev)<.0001 for side in [-1,1])
 report['checks'].append({'state':name,'position':pos,'brake':stop,'reverse':rev,'emissions':values,'powers':powers})
 if index<4:
  shot=r/f'artifacts/vehicles/rondesp/v25-{name}-viewport.png'
  with bpy.context.temp_override(window=window,area=area,region=region):
   bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=3);bpy.ops.screen.screenshot(filepath=str(shot))
  report['preview_paths'][name]=shot.relative_to(r).as_posix()
for key,value in saved.items():root[key]=value
root.update_tag();s.frame_set(200);bpy.context.view_layer.update()
assert all(fingerprint(s.objects[n])==h for n,h in previous['protected_mesh_hashes'].items())
assert abs(revmat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value-5.)<.0001
s.name='VIATURA | Rondesp Hilux lanternas e re v25';s['boas_revision_parent']=parent.relative_to(r).as_posix()
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.type='MATERIAL'
notes=bpy.data.texts.get('HILUX25 | POSICAO FREIO E RE') or bpy.data.texts.new('HILUX25 | POSICAO FREIO E RE')
notes.clear();notes.write('Posição: vermelho discreto com lanternas_ligadas=1.\nFreio: setor vermelho superior mais intenso + terceira luz, freio=1. Funciona mesmo com posição desligada.\nRé: compartimento claro fica branco e dois feixes iluminam atrás, re_engatada=1. Funciona junto com o freio, sem apagar os vermelhos.\nManual: demonstracao_ativa=0 no root. Automático: demonstracao_ativa=1; frame 200 mostra ré e frame 160 mostra freio.\nCiclo das quatro portas e faróis reforçados V24 preservados. Compartimento claro reutilizado; desenho fino da lanterna ainda candidato.\nSem circuito de pisca traseiro ou integração runtime nesta revisão.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report.update({'file':out.relative_to(r).as_posix(),'scene':s.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'objects':len(s.objects),'live_session':{'pid':os.getpid(),'port':9876},'controls':{'position':'lanternas_ligadas','brake':'freio','reverse':'re_engatada','manual_override':'demonstracao_ativa=0'},'demo_reverse_frames':[190,224],'intensities_scope':'Parâmetros de aparência Blender; não medições fotométricas de fábrica.'})
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'sha256':report['sha256'],'states_checked':len(report['checks']),'clear_slots_changed':len(report['changed_material_slots']),'new_lights':len(report['new_lights']),'geometry_unchanged':True}))
