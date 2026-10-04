"""Remove pequenos módulos legados acima do sinalizador substituído na V08."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='marrom_v08.blend'
targets=[]
for o in scene.objects:
    if o.type!='MESH' or 'HILUX08' in o.name:continue
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    lo=Vector(tuple(min(v[k] for v in p) for k in range(3)));hi=Vector(tuple(max(v[k] for v in p) for k in range(3)));c=(lo+hi)/2;size=hi-lo
    if abs(c.x)<.65 and -.4<c.y<.6 and 1.985<c.z<2.12 and max(size)<.18:
        targets.append(o)
assert len(targets)<=16,'Revisar seleção de módulos antes de remover.'
removed=[o.name for o in targets]
for o in targets:bpy.data.objects.remove(o,do_unlink=True)
out=Path(bpy.data.filepath);bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
rp=repo/'docs/reports/blender/rondesp_marrom_v08.json';r=json.loads(rp.read_text(encoding='utf-8'))
r['legacy_light_modules_removed']=removed;r['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=repo/'world/vehicles/catalog.json';d=json.loads(cp.read_text(encoding='utf-8'));v=next(v for v in d['vehicles'] if v['asset_id']=='vehicle-rondesp-pickup')
v['authoring_base']['sha256']=r['sha256'];v['variants'][0]['sha256']=r['sha256']
cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
