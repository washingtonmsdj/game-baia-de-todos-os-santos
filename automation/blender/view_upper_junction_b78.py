"""Vista frontal da junção na janela atual; somente apresentação, sem salvar."""
import bpy, json
from mathutils import Vector
floor = bpy.context.scene.objects['SUPERIOR | piso saguão']
eye = floor.matrix_world @ Vector((2, 4.5, 1.775))
target = floor.matrix_world @ Vector((-6.5, 0, 1.9))
direction = target-eye
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        space.region_3d.view_perspective = 'PERSP'
        space.region_3d.view_rotation = direction.to_track_quat('-Z', 'Y')
        space.region_3d.view_location = target
        space.region_3d.view_distance = direction.length
        space.shading.type = 'SOLID'
        space.overlay.show_overlays = False
        area.tag_redraw()
print(json.dumps({'preview_only': True, 'saved': False}))
