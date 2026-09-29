import bpy
print(hasattr(bpy.ops.export_scene, 'gltf'))
print([n for n in dir(bpy.ops.export_scene) if 'gltf' in n.lower()])
