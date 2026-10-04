"""Ajuste local do encontro A/teto, sem mover o veículo ou suas outras peças."""
import bpy,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v13.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert not s.get('boas_v13_roof_tip_aligned')
gi=next(g.index for g in o.vertex_groups if g.name=='HILUX06 | Montante A curvo 1')
n=0
for v in o.data.vertices:
    if not any(g.group==gi for g in v.groups) or v.co.y<=-.435:continue
    t=max(0,min(1,(v.co.y+.435)/.10));w=t*t*(3-2*t)
    v.co.x+=.008*w;v.co.y-=.004*w;v.co.z-=.020*w;n+=1
o.data.update();s['boas_v13_roof_tip_aligned']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
rp=r/'docs/reports/blender/hilux_carroceria_v13.json';report=json.loads(rp.read_text(encoding='utf-8'))
report['roof_tip_alignment']={'vertices':n,'scope':'Transição local da coluna A para a borda do teto; parâmetros candidatos.'}
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
