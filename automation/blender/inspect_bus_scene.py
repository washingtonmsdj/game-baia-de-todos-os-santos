import bpy
print(bpy.context.scene.name)
print([o.name for o in bpy.context.scene.objects if 'ROOT' in o.name or o.name.startswith('BUS03')][:20])
