"""Painel dos quatro equipamentos na cena atual; temporário e separado da B82."""
import bpy,json,math,sys,time
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_four_lifts import Lift
CONFIG=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-four-lifts.json').read_text())
FRAME=Matrix(json.loads((ROOT/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])

def sync(state):
 for spec in CONFIG['equipment']:
  lift=state['lifts'][spec['id']];side=spec.get(str(lift.station)+'_side');ca,sa=math.cos(spec['angle_local']),math.sin(spec['angle_local'])
  for part in spec['parts']:
   o=bpy.data.objects.get(part['object'])
   if not o:continue
   dz=lift.z-spec['upper'] if part['tag'].startswith('cabin') else 0.
   opened=lift.openness if ((part['tag']=='landing_door' and part['landing']==lift.station) or
      (part['tag']=='cabin_door' and part['landing']==str(side))) else 0.
   dy=(part['leaf'] or 0)*spec.get('door_leaf_stroke',.62)*opened;shift=Vector((-sa*dy,ca*dy,dz));o.matrix_world=FRAME.copy();o.matrix_world.translation+=FRAME.to_3x3()@shift
   o['boas_equipment_state']=lift.state;o['boas_door_physical_enabled']=bool(opened<1.) if 'door' in part['tag'] else True
  scene=bpy.data.scenes.get(CONFIG['scene'])
  if scene:scene['boas_equipment_'+spec['id']]=lift.state+' / '+str(lift.station)+' / '+format(lift.z,'.3f')+'m'
 for w in bpy.context.window_manager.windows:
  for area in w.screen.areas:
   if area.type=='VIEW_3D':area.tag_redraw()

def tick():
 state=bpy.app.driver_namespace.get('boas_four_lifts')
 if not state or state['file']!=bpy.data.filepath:return None
 now=time.monotonic();dt=min(.1,now-state['time']);state['time']=now;n=max(1,math.ceil(dt*60))
 for _ in range(n):
  for lift in state['lifts'].values():lift.update(max(1e-6,dt/n))
 sync(state)
 if any(l.state in ('OPENING','CLOSING','MOVING') for l in state['lifts'].values()):return 1/60
 return None

def initialize():
 state={'file':bpy.data.filepath,'time':time.monotonic(),'lifts':{s['id']:Lift(s['id'],s['lower'],s['upper'],s['upper'],s['movement_enabled']) for s in CONFIG['equipment']}}
 bpy.app.driver_namespace['boas_four_lifts']=state;sync(state);return state

class BOAS_OT_four_lift_command(bpy.types.Operator):
 bl_idname='boas.four_lift_command';bl_label='Comandar elevador Lacerda';bl_description='Equipamento proxy da cena atual; mantém portas/CCD intertravados'
 equipment:bpy.props.StringProperty()
 action:bpy.props.StringProperty(default='DEPART')
 def execute(self,context):
  state=bpy.app.driver_namespace.get('boas_four_lifts') or initialize();lift=state['lifts'][self.equipment]
  approved=lift.depart() if self.action=='DEPART' else lift.request('upper' if self.action=='UPPER' else 'lower')
  if not approved:self.report({'WARNING'},'Comando bloqueado: estado ou CCD não permite');return {'CANCELLED'}
  state['time']=time.monotonic()
  if not bpy.app.timers.is_registered(tick):bpy.app.timers.register(tick,first_interval=1/60)
  return {'FINISHED'}

class BOAS_PT_four_lifts(bpy.types.Panel):
 bl_label='Lacerda · quatro elevadores';bl_idname='BOAS_PT_four_lifts';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='BOAS'
 @classmethod
 def poll(cls,context):return context.scene.name==CONFIG['scene']
 def draw(self,context):
  l=self.layout;l.label(text='GAMEPLAY_PROXY · dimensões provisórias')
  l.operator('boas.four_lift_inspect',text='Ver cabines / voltar ao mapa',icon='VIEWZOOM')
  state=bpy.app.driver_namespace.get('boas_four_lifts')
  for spec in CONFIG['equipment']:
   box=l.box();lift=state['lifts'][spec['id']] if state else None
   box.label(text=f"{spec['number']} · {spec['tower']} · {lift.state if lift else 'CLOSED'}")
   if not spec['movement_enabled']:box.label(text='Bloqueado pelo CCD',icon='ERROR');continue
   row=box.row(align=True)
   for label,action in (('Chamar alto','UPPER'),('Chamar baixo','LOWER'),('Viajar','DEPART')):
    op=row.operator('boas.four_lift_command',text=label);op.equipment=spec['id'];op.action=action
  l.label(text='Abrir: chamar o andar presente')
  l.label(text='Viajar: somente com cabine aberta')
  l.label(text='Rota pedonal dos quatro ainda não aprovada')

class BOAS_OT_four_lift_inspect(bpy.types.Operator):
 bl_idname='boas.four_lift_inspect';bl_label='BOAS Inspecionar quatro cabines';bl_description='Recorte de inspeção na mesma cena/arquivo; nenhum objeto é apagado ou deslocado'
 def execute(self,context):
  area=context.area;space=context.space_data;region=space.region_3d
  if space.local_view:
   bpy.ops.view3d.localview(frame_selected=False)
   previous=bpy.app.driver_namespace.pop('boas_four_lifts_previous_view',None)
   if previous:region.view_location=previous[0];region.view_rotation=previous[1];region.view_distance=previous[2];region.view_perspective=previous[3]
  else:
   bpy.app.driver_namespace['boas_four_lifts_previous_view']=(region.view_location.copy(),region.view_rotation.copy(),region.view_distance,region.view_perspective)
   bpy.ops.object.select_all(action='DESELECT')
   for s in CONFIG['equipment']:
    for p in s['parts']:bpy.data.objects[p['object']].select_set(True)
   context.view_layer.objects.active=bpy.data.objects[CONFIG['equipment'][0]['parts'][0]['object']]
   bpy.ops.view3d.localview(frame_selected=False);bpy.ops.object.select_all(action='DESELECT')
   region.view_location=FRAME@Vector((-30.,2.,CONFIG['equipment'][0]['upper']+1.4));region.view_distance=60.
   region.view_rotation=(FRAME.to_3x3()@Vector((-.6,-1.4,.8))).to_track_quat('Z','Y');region.view_perspective='ORTHO'
  region.update();area.tag_redraw();return {'FINISHED'}

def register():
 old=bpy.app.driver_namespace.pop('boas_four_lifts',None)
 for cls in (BOAS_OT_four_lift_command,BOAS_OT_four_lift_inspect,BOAS_PT_four_lifts):
  prev=getattr(bpy.types,cls.__name__,None)
  if prev:bpy.utils.unregister_class(prev)
  bpy.utils.register_class(cls)
 # Somente estados em memória. O registro não muda a geometria/salvamento.
 bpy.app.driver_namespace['boas_four_lifts']={'file':bpy.data.filepath,'time':time.monotonic(),'lifts':{s['id']:Lift(s['id'],s['lower'],s['upper'],s['upper'],s['movement_enabled']) for s in CONFIG['equipment']}}
 print('Painel BOAS: quatro elevadores independentes na cena atual')
register()
