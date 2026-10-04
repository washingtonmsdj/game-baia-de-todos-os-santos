"""Salva a etapa real das portas e reabre a fonte na mesma janela MCP."""
import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_portas_v18.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert s.get('boas_v18_front_hinge_finished') and not s.get('boas_v18_final_saved')
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
audit=json.loads((r/'artifacts/vehicles/rondesp/v18-doors-audit.json').read_text(encoding='utf8'))
assert audit['body_matches_authorized_change'] and audit['protected_meshes_unchanged']
assert audit['door_body_intersection_count']==0 and audit['door_pair_intersection_count']==0
assert all(not hits for hits in audit['self_intersections'].values())
assert all(not data[k] for data in audit['mesh_reviews'].values() for k in ['multi_edges','wire_edges','tiny_faces','inconsistent_winding'])
assert all(v==0 for v in audit['mirror_vertex_difference_m'].values())
assert len(audit['movement_samples'])==13
parent=r/report['parent'];assert hashlib.sha256(parent.read_bytes()).hexdigest()==report['parent_sha256']
for d in report['door_assemblies']:
 p=s.objects[d['pivot']];assert abs(p['abertura_graus'])<1e-9
 p['boas_opening_status']='candidate; 13 poses geometricamente conferidas, abertura independente 0 a 70 graus'
 assert p.animation_data.drivers[0].driver.is_valid
s['boas_v18_final_saved']=True
s['boas_authoring_mode']='body_and_doors'
s['boas_v18_control_help']='Selecione o pivo de cada porta e ajuste abertura_graus nas propriedades personalizadas: 0 a 70.'
body=s.objects['HILUX | CARROCERIA PRINCIPAL']
body['boas_editing']='Carroceria fixa com Mirror X. Portas independentes visiveis; coluna B recuada sob as folhas.'
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   sp=a.spaces.active;sp.shading.color_type='OBJECT';sp.shading.show_cavity=False;sp.shading.show_shadows=False
   sp.region_3d.view_rotation=(Vector((0,.15,1.05))-Vector((7,-8,3.8))).to_track_quat('-Z','Y')
   sp.region_3d.view_location=(0,.15,1.05);sp.region_3d.view_distance=5.5
s.render.filepath='//../../../../artifacts/vehicles/rondesp/v18-portas.png'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report.update({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_reopened':False,
 'visual_review':'reviewed_closed_and_open','door_rig_applied':True,'runtime_exported':False,
 'live_session':{'pid':os.getpid(),'transport':'BlendMCP 1.4.4 fallback','port':9877,'single_visible_window':True},
 'mesh_review_scope':'Folhas externas/internas e caixilhos; carroceria avaliada com Mirror e espessura para a amostragem angular.',
 'remaining':['Parâmetros autorais candidatos, sem dimensões industriais confirmadas.',
  'Vidros, acabamento de interior, rodas, chassi e equipamentos permanecem reservados para etapas seguintes.',
  'Amostragem de 13 poses não certifica varredura contínua nem a montagem de todos os componentes reservados.'],
 'geometry_review':audit,'visible_meshes':[o.name for o in s.objects if o.type=='MESH' and o.visible_get()]})
report['recovery_notes']='MCP principal perdeu o transporte e a janela anterior deixou de existir. Checkpoint V18 recuperado em uma única janela visível e alterações continuadas pelo fallback MCP. A rejeição de auditoria concorrente foi respeitada; nova conferência somente após recuperação e conclusão das mutações.'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def reopen():
 bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf8'))
 current=bpy.context.scene
 data['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
 data['reopened_observation']={'scene':current.name,'pid':os.getpid(),'objects':len(current.objects),
  'file_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
  'door_controls':{d['pivot']:current.objects[d['pivot']]['abertura_graus'] for d in data['door_assemblies']},
  'visible_meshes':[o.name for o in current.objects if o.type=='MESH' and o.visible_get()]}
 assert data['reopened_observation']['file_sha256']==data['sha256']
 assert all(v==0 for v in data['reopened_observation']['door_controls'].values())
 assert data['reopened_observation']['visible_meshes']==data['visible_meshes']
 rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return None
bpy.app.timers.register(reopen,first_interval=.5)
print(json.dumps({'file':out.relative_to(r).as_posix(),'sha256':report['sha256'],'doors':4}))
