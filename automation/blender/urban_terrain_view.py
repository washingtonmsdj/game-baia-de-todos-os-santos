"""Vistas da malha na mesma janela Blender para revisão visual."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas));area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';space.overlay.show_overlays=False;space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.shading.light='STUDIO'
directory=root/'artifacts/urban-slice';directory.mkdir(parents=True,exist_ok=True)
with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):
    if space.local_view:bpy.ops.view3d.localview(frame_selected=False)
    bpy.ops.object.select_all(action='DESELECT')
    objects=[scene.objects['MVP | terreno corrigido | colisão estática']]+[o for o in scene.objects if o.name.startswith(('SLICE | road | superfície','SLICE | walkable | superfície','SLICE | guias da malha'))]
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.view3d.localview(frame_selected=False)
for name,target,eye in [('terrain-overview',(-5,-98,67),(-47,-156,110)),('terrain-street',(-10,-100,67),(-17,-87,69))]:
    target=Vector(target);eye=Vector(eye);r=space.region_3d;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_distance=(target-eye).length;r.view_location=target;r.view_perspective='PERSP';scene.render.filepath=str(directory/(name+'.png'))
    r.update()
    with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.view3d.localview(frame_selected=False)
print(json.dumps({'source':bpy.data.filepath,'views':['artifacts/urban-slice/terrain-overview.png','artifacts/urban-slice/terrain-street.png']}))
