import bpy

surface = bpy.data.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro']
volume = bpy.data.objects['BAÍA | volume de água no limite do recorte']
scene = bpy.context.scene

surface['boas_water_role'] = 'gameplay_surface_reference'
surface['boas_water_level_m'] = 0.35
surface['boas_surface_query_source'] = 'engine_runtime'
surface['boas_collision_source'] = False
surface['boas_visual_displacement_collision'] = False

volume['boas_water_role'] = 'swim_dive_volume'
volume['boas_swimmable'] = True
volume['boas_diveable'] = True
volume['boas_boats_supported'] = True
volume['boas_min_depth_m'] = -16.0
volume['boas_max_surface_m'] = 0.35
volume['boas_buoyancy_runtime'] = True
volume['boas_underwater_runtime'] = True
volume['boas_currents_runtime'] = True
volume['boas_runtime_engine_binding'] = 'unbound'
volume.hide_viewport = True
volume.hide_render = True

scene['boas_water_contract'] = 'bay-of-all-saints/water-runtime-contract-v1'
scene['boas_water_level_m'] = 0.35
scene['boas_water_swimming'] = True
scene['boas_water_diving'] = True
scene['boas_water_boats'] = True
scene['boas_water_runtime_binding'] = 'unbound'

bpy.ops.wm.save_mainfile()
print({'surface': surface.name, 'volume': volume.name, 'saved': bpy.data.filepath})
