"""Vistas da carroceria isolada; mantém a única janela em modo de modelagem."""
import bpy, json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_carroceria_v12.blend'
body=s.objects['HILUX | CARROCERIA PRINCIPAL'];old=s.render.engine;mat=s.camera.matrix_world.copy();scale=s.camera.data.ortho_scale
s.render.engine='BLENDER_WORKBENCH'
sh=s.display.shading;sh.color_type='OBJECT';sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=True;sh.background_type='WORLD'
s.world.color=(.08,.08,.10)
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
for name,pos in [('frente',(-7,-8,3.6)),('cacamba',(7,8,4.8))]:
    s.camera.location=pos;s.camera.rotation_euler=(Vector((0,.17,1.03))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.1
    s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v12-carroceria-{name}.png');bpy.ops.render.render(write_still=True)
s.render.engine=old;s.camera.matrix_world=mat;s.camera.data.ortho_scale=scale
rp=r/'docs/reports/blender/hilux_carroceria_v12.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['scene_observation']={'file':Path(bpy.data.filepath).relative_to(r).as_posix(),'visible_meshes':[o.name for o in s.objects if o.type=='MESH' and o.visible_get()],'body_base_vertices':len(body.data.vertices),'body_base_faces':len(body.data.polygons),'modifiers':[(m.name,m.type) for m in body.modifiers]}
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
