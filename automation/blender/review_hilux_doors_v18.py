"""Vistas de encaixe fechado e abertura das portas na única sessão visível."""
import bpy, json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_portas_v18.blend'
rp=r/'docs/reports/blender/hilux_portas_v18.json';report=json.loads(rp.read_text(encoding='utf8'))
pivots=[s.objects[d['pivot']] for d in report['door_assemblies']]
cam=s.camera;old_matrix=cam.matrix_world.copy();old_type=cam.data.type;old_scale=cam.data.ortho_scale
old_engine=s.render.engine;old_res=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)
saved_angles=[p['abertura_graus'] for p in pivots]
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading
sh.color_type='OBJECT';sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=False
sh.background_type='WORLD';s.world.color=(.08,.08,.10)
s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
views=[
 ('lateral-fechadas',(8,.10,1.45),(0,.10,1.06),6.1,0),
 ('encaixe-portas',(8,.10,1.40),(0,.10,1.15),2.6,0),
 ('frente-fechadas',(7,-8,3.7),(0,.15,1.06),6.1,0),
 ('portas-abertas',(7,-7,4.7),(0,.20,1.03),6.1,65),
 ('interior-portas',(5,5,2.8),(.8,.12,1.12),3.5,65),
]
try:
 for name,pos,target,zoom,angle in views:
  for p in pivots:p['abertura_graus']=float(angle);p.update_tag(refresh={'OBJECT'})
  s.frame_set(s.frame_current);bpy.context.view_layer.update()
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.data.type='ORTHO';cam.data.ortho_scale=zoom
  s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v18-{name}.png')
  bpy.ops.render.render(write_still=True)
finally:
 for p,angle in zip(pivots,saved_angles):p['abertura_graus']=angle;p.update_tag(refresh={'OBJECT'})
 s.frame_set(s.frame_current);bpy.context.view_layer.update()
 cam.matrix_world=old_matrix;cam.data.type=old_type;cam.data.ortho_scale=old_scale
 s.render.engine=old_engine
 s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=old_res
report['visual_views']=[f'artifacts/vehicles/rondesp/v18-{v[0]}.png' for v in views]
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
