"""Diagnóstico somente leitura da sessão e dimensões dos viewports."""
import bpy,json,os
print(json.dumps({'pid':os.getpid(),'background':bpy.app.background,'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'windows':[{'screen':w.screen.name,'areas':[{'type':a.type,'width':a.width,'height':a.height} for a in w.screen.areas]} for w in bpy.context.window_manager.windows]}))
