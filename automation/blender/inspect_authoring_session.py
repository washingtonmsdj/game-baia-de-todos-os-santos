"""Inspeção mínima da janela indicada; não modifica nem salva cena."""
import bpy,json,os
print(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'unsaved_changes':bpy.data.is_dirty,'pid':os.getpid(),'render_running':bpy.app.is_job_running('RENDER')}))
