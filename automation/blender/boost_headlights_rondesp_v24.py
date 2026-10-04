"""Reforça o feixe dos faróis preservando a demonstração e as malhas do veículo."""
import bpy,json,hashlib,struct,os
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;root=s.objects['RDP01_ROOT | viatura']
parent=r/'blender/assets/vehicles/rondesp-pickup/marrom_v23_demonstracao.blend'
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v24_farois.blend'
rp=r/'docs/reports/blender/rondesp_farois_v24.json'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==parent.resolve()
assert not out.exists() and not bpy.app.is_job_running('RENDER')
previous=json.loads((r/'docs/reports/blender/rondesp_demonstracao_v23.json').read_text(encoding='utf8'))
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:
  h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in previous['protected_mesh_hashes'].items())
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas))
area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(x for x in area.regions if x.type=='WINDOW')
playing=window.screen.is_animation_playing
if playing:
 with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.screen.animation_cancel(restore_frame=False)
original={'demonstracao_ativa':root['demonstracao_ativa'],'giroflex_ligado':root['giroflex_ligado'],'farois_ligados':root['farois_ligados']}
root['demonstracao_ativa']=0.;root['giroflex_ligado']=0.;root['farois_ligados']=1.;root.update_tag();s.frame_set(1);bpy.context.view_layer.update()
area.spaces.active.shading.type='RENDERED'
before_shot=r/'artifacts/vehicles/rondesp/v24-farois-antes-viewport.png'
with bpy.context.temp_override(window=window,area=area,region=region):
 bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=3);bpy.ops.screen.screenshot(filepath=str(before_shot))
root['intensidade_farois']=1.
root.id_properties_ui('intensidade_farois').update(min=0.,max=2.,description='Multiplicador da iluminação dos dois faróis. 1: potência reforçada V24. Sem equivalência com consumo elétrico do veículo.')
changed=[]
def strength_variable(driver):
 v=driver.variables.get('potencia') or driver.variables.new();v.name='potencia';v.type='SINGLE_PROP'
 v.targets[0].id=root;v.targets[0].data_path='["intensidade_farois"]'
for side in [-1,1]:
 ob=s.objects[f'HILUX22 | Feixe farol {side}'];f=ob.data.animation_data.drivers[0]
 changed.append({'object':ob.name,'expression_before':f.driver.expression,'power_before':ob.data.energy,'power_at_full_control':2400.,'ratio_to_v23':20.,'unit_scope':'Blender scene-light power; not electrical wattage or certified photometry'})
 strength_variable(f.driver);f.driver.expression='2400*aceso*potencia';ob.data.update_tag()
for name,factor in [('HILUX22 | Nucleo farol branco',16.),('HILUX22 | Guia optica branca',8.),('HILUX22 | Lente farol iluminada',.45)]:
 mat=bpy.data.materials[name]
 for f in mat.node_tree.animation_data.drivers:
  strength_variable(f.driver);f.driver.expression=f'{factor}*aceso*potencia'
 mat.node_tree.update_tag();mat.update_tag()
root.update_tag();s.frame_set(2);s.frame_set(1);bpy.context.view_layer.update()
checks=[]
for on in [0.,1.]:
 root['farois_ligados']=on;root.update_tag();s.frame_set(2 if on==0. else 1);bpy.context.view_layer.update()
 lights=[s.objects[f'HILUX22 | Feixe farol {side}'].data.energy for side in [-1,1]]
 assert all(abs(value-2400*on)<.001 for value in lights)
 checks.append({'on':on,'powers':lights})
after_shot=r/'artifacts/vehicles/rondesp/v24-farois-reforcados-viewport.png'
with bpy.context.temp_override(window=window,area=area,region=region):
 bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=3);bpy.ops.screen.screenshot(filepath=str(after_shot))
for key,value in original.items():root[key]=value
root.update_tag();s.frame_set(90);bpy.context.view_layer.update()
assert all(fingerprint(s.objects[n])==h for n,h in previous['protected_mesh_hashes'].items())
s.name='VIATURA | Rondesp Hilux farois v24';s['boas_revision_parent']=parent.relative_to(r).as_posix()
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.shading.type='MATERIAL'
notes=bpy.data.texts.get('HILUX24 | ILUMINACAO E RUNTIME') or bpy.data.texts.new('HILUX24 | ILUMINACAO E RUNTIME')
notes.clear();notes.write('Faróis V24: feixes 20 vezes o parâmetro de potência V23. Controle intensidade_farois no root; farois_ligados continua 0/1.\nO valor em Blender é parâmetro de iluminação da cena, não potência elétrica de uma lâmpada real.\nA demonstração automática de portas/freio é somente apresentação. Malhas, pivôs, materiais compatíveis, posições/cores das luzes e movimentos amostrados podem ser reaproveitados no jogo.\nDrivers Blender e halo de compositor não executam na engine. Runtime precisará controlar faróis/giroflex/freio a partir dos estados e entradas do veículo.\nAnimações das portas poderão ser exportadas amostrando transforms; luzes punctual podem ser exportadas por glTF se o importador suportar.\nSem integração, exportação ou engine definitiva nesta revisão.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'asset_id':'vehicle-rondesp-pickup','status':'candidate','parent':parent.relative_to(r).as_posix(),'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'file':out.relative_to(r).as_posix(),'scene':s.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'protected_mesh_hashes':previous['protected_mesh_hashes'],'geometry_unchanged':True,'door_demo_preserved':True,'headlight_changes':changed,'on_off_checks':checks,'source_reopened':False,'runtime_exported':False,'visual_review':'pending','preview_paths':{'before':before_shot.relative_to(r).as_posix(),'after':after_shot.relative_to(r).as_posix()},'live_session':{'pid':os.getpid(),'port':9876},'engine_boundary':{'presentation_cycle_only':True,'reuse_candidates':['geometry','door_pivots','compatible_materials','sampled_door_transforms','light_positions_and_colors'],'requires_engine_implementation':['vehicle_input_and_states','blink_control','brake_control','light_intensity_and_shadows','bloom_postprocess'],'export_or_import_not_verified':True}}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':str(out),'sha256':report['sha256'],'checks':checks,'meshes_preserved':True,'comparisons':report['preview_paths']}))
