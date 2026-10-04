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
solid=[(m,m.show_viewport,m.show_render) for m in o.modifiers if m.type=='SOLIDIFY']
created=[]
sh=s.display.shading
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
sh.light='STUDIO';sh.studio_light='paint.sl';sh.show_cavity=False;sh.show_shadows=False;sh.show_specular_highlight=True
cam.location=(3.5,6,3.65);cam.rotation_euler=(Vector((0,.72,1.50))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.6
def render(name):
 bpy.context.view_layer.update();s.render.filepath=str(r/f'artifacts/vehicles/rondesp/v20-diagnostic-{name}.png');bpy.ops.render.render(write_still=True)
try:
 render('original')
 for m,_,_ in solid:m.show_viewport=False;m.show_render=False
 render('sem-espessura')
 for m,a,b in solid:m.show_viewport=a;m.show_render=b
 bm=bmesh.new();bm.from_mesh(tmp);bm.normal_update();fl=bm.faces.layers.int['boas_panel_id']
 seam=[e for e in bm.edges if len(e.link_faces)==2 and {f[fl] for f in e.link_faces}=={88,92}]
 data={'roof_rear_edge_count':len(seam),'roof_rear_angles':[math.degrees(e.calc_face_angle()) for e in seam],
  'mods':[{'name':m.name,'type':m.type} for m in o.modifiers],
  'rear_header_face_normals':[{'center':list(f.calc_center_median()),'normal':list(f.normal),'area':f.calc_area()} for f in bm.faces if f[fl]==92 and f.calc_center_median().z>1.70]}
 (r/'artifacts/vehicles/rondesp/v20-ripple-diagnosis.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 for e in seam:e.smooth=False
 bm.to_mesh(tmp);bm.free();tmp.update();render('aresta-definida')
 # Candidato reversível: uma dobra contínua no encontro teto/painel traseiro.
 bm=bmesh.new();bm.from_mesh(orig);bm.normal_update();fl=bm.faces.layers.int['boas_panel_id']
 seam=[e for e in bm.edges if len(e.link_faces)==2 and {f[fl] for f in e.link_faces}=={88,92}]
 result=bmesh.ops.bevel(bm,geom=seam,offset=.010,segments=5,affect='EDGES',clamp_overlap=True,profile=.5)
 for f in result.get('faces',[]):f.smooth=True
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(tmp);bm.free();tmp.update();render('dobra-contínua')
finally:
 o.data=orig;bpy.data.meshes.remove(tmp)
 for m,a,b in solid:m.show_viewport=a;m.show_render=b
 cam.matrix_world=saved_matrix;cam.data.type=saved_type;cam.data.ortho_scale=saved_zoom
 s.render.engine=saved_engine;s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=saved_res
 sh.light=saved_light;sh.studio_light=saved_studio
print('Comparações de superfície publicadas; geometria original restaurada')
