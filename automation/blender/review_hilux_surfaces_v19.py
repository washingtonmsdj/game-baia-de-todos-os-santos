"""Vistas de encaixe fechado e abertura das portas na única sessão visível."""
import bpy, json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name in {'hilux_portas_v18.blend','hilux_superficies_v19.blend'}
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
pivots=[s.objects[d['pivot']] for d in report['door_assemblies']]
cam=s.camera;old_matrix=cam.matrix_world.copy();old_type=cam.data.type;old_scale=cam.data.ortho_scale
old_engine=s.render.engine;old_res=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)
saved_angles=[p['abertura_graus'] for p in pivots]
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading
sh.color_type='OBJECT';sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=False
sh.background_type='WORLD';s.world.color=(.08,.08,.10)
s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
stage='before' if Path(bpy.data.filepath).name=='hilux_portas_v18.blend' else 'after'
views=[
 ('teto',(5,5,4.5),(0,.15,1.6),3.2,0),
 ('capo',(5,-6,4.5),(0,-1.54,1.2),3.4,0),
 ('geral',(7,-8,3.8),(0,.15,1.06),6.1,0),
]

try:
 for name,pos,target,zoom,angle in views:
  for p in pivots:p['abertura_graus']=float(angle);p.update_tag(refresh={'OBJECT'})
  s.frame_set(s.frame_current);bpy.context.view_layer.update()
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.data.type='ORTHO';cam.data.ortho_scale=zoom
  s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v19-{stage}-{name}.png')
  bpy.ops.render.render(write_still=True)
finally:
 for p,angle in zip(pivots,saved_angles):p['abertura_graus']=angle;p.update_tag(refresh={'OBJECT'})
 s.frame_set(s.frame_current);bpy.context.view_layer.update()
 cam.matrix_world=old_matrix;cam.data.type=old_type;cam.data.ortho_scale=old_scale
 s.render.engine=old_engine
 s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=old_res
