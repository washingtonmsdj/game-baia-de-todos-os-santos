import bpy
print([o.name for o in bpy.context.scene.objects if o.name.startswith('BUS02 |') and any(w in o.name for w in ['frontal','brisa','limpador','Palheta','Letreiro'])])
