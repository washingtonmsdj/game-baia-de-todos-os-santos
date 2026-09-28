import bpy

scene = bpy.context.scene
camera = bpy.data.objects.get('ORLA | vista aérea Mercado, praça e Baía')
if camera is not None:
    camera.hide_viewport = False
    scene.camera = camera

for obj in bpy.context.selected_objects:
    obj.select_set(False)
for name in ('BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro',
             'R30A8 | FOAM | linha costeira',
             'R30A8 | FOAM | halo costeiro'):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_viewport = False
        obj.select_set(True)

for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type != 'VIEW_3D':
        continue
    space = area.spaces.active
    try:
        space.shading.type = 'MATERIAL'
        space.overlay.show_overlays = False
        if camera is not None:
            space.region_3d.view_perspective = 'CAMERA'
    except Exception:
        pass
