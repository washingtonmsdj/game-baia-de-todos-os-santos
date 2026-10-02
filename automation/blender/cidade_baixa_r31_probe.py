"""Estado mínimo do passe de modelagem; nenhuma mutação."""
import bpy,json
print(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'render_running':bpy.app.is_job_running('RENDER'),'facades':sum(o.name.startswith('BAIXA R31 |') for o in bpy.data.objects),'monument':bool(bpy.data.objects.get('MARIO CRAVO | Fonte da Rampa do Mercado'))}))
