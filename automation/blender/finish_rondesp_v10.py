"""Visibilidade do giroflex e fechamento da candidata V10."""
import bpy,ast,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='marrom_v10.blend'
assert not s.get('boas_v10_closed')
root=s.objects['RDP01_ROOT | viatura'];collections={g:bpy.data.collections['RDP01 | '+g] for g in ['LUZES','ACABAMENTOS']}
for fn in ast.parse((r/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8')).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=='box':exec(compile(ast.Module(body=[fn],type_ignores=[]),'<box>','exec'),globals())
led=bpy.data.materials['RDP01 | HILUX10 LED vermelho']
for side in [-1,1]:
    for front in [-1,1]:
        o=box('HILUX10 | Lente externa vermelha '+str((side,front)),(side*.385,.035+front*.116,1.95),(.30,.022,.044),led,'LUZES',.014)
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=6
    box('HILUX10 | Extremidade vermelha '+str(side),(side*.553,.035,1.95),(.021,.17,.044),led,'LUZES',.01)
# Enquadramento da traseira para conferir o principal pedido na janela.
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            v=a.spaces.active;v.shading.type='SOLID';v.shading.color_type='MATERIAL';v.overlay.show_overlays=False
            v.region_3d.view_rotation=(Vector((0,.16,1.04))-Vector((-7,8,3.3))).to_track_quat('-Z','Y');v.region_3d.view_location=(0,.16,1.04);v.region_3d.view_distance=5.8
s['boas_v10_closed']=True
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v10.blend';bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/rondesp_marrom_v10.json';d=json.loads(rp.read_text(encoding='utf-8'));d['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();d['source_reopened']=False;d['emblem_status']='simplificação vetorial candidata; não réplica aprovada';rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));d=json.loads(rp.read_text(encoding='utf-8'));d['source_reopened']=Path(bpy.data.filepath)==out;rp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
