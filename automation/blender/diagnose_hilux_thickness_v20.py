"""Compara superfície, espessura e normais na mesma cena visível, sem salvar."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
o=s.objects['HILUX | CARROCERIA PRINCIPAL'];cam=s.camera
orig=o.data;tmp=orig.copy();o.data=tmp
saved_matrix=cam.matrix_world.copy();saved_type=cam.data.type;saved_zoom=cam.data.ortho_scale
saved_engine=s.render.engine;saved_res=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)
saved_light=s.display.shading.light;saved_studio=s.display.shading.studio_light
solid=[(m,m.show_viewport,m.show_render,m.offset,m.use_quality_normals,m.use_even_offset,m.solidify_mode) for m in o.modifiers if m.type=='SOLIDIFY']
created=[]
sh=s.display.shading
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=False;sh.show_specular_highlight=True
cam.location=(3.5,6,3.65);cam.rotation_euler=(Vector((0,.72,1.50))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.6
def render(name):
 bpy.context.view_layer.update();s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v20-diagnostic-{name}.png');bpy.ops.render.render(write_still=True)
try:
 render('espessura-original')
 for m,*_ in solid:m.offset=-1.;m.use_quality_normals=False
 render('chapa-para-dentro')
 for m,*_ in solid:m.use_quality_normals=True
 render('chapa-para-dentro-normais')
 for m,*_ in solid:m.offset=0.;m.use_quality_normals=True
 render('normais-qualidade')
finally:
 o.data=orig;bpy.data.meshes.remove(tmp)
 for m,a,b,off,qual,even,mode in solid:m.show_viewport=a;m.show_render=b;m.offset=off;m.use_quality_normals=qual;m.use_even_offset=even;m.solidify_mode=mode
 cam.matrix_world=saved_matrix;cam.data.type=saved_type;cam.data.ortho_scale=saved_zoom
 s.render.engine=saved_engine;s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=saved_res
 sh.light=saved_light;sh.studio_light=saved_studio
print('Comparações de superfície publicadas; geometria original restaurada')
