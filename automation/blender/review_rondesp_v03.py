"""Reabertura read-only da fonte e vistas dos materiais na janela existente."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v03.blend'
assert Path(bpy.data.filepath).resolve()==out.resolve()
assert scene.name=='VIATURA | Rondesp picape marrom v03'
assert len(bpy.data.scenes)==1
path=repo/'docs/reports/blender/rondesp_marrom_v03.json'
report=json.loads(path.read_text(encoding='utf-8'))
assert report['sha256']==hashlib.sha256(out.read_bytes()).hexdigest()
report['reopened']={'ok':True,'scenes':1,'objects':len(scene.objects),'source':'v03','other_assets_present':False}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1000;scene.render.resolution_y=665
folder=repo/'artifacts/vehicles/rondesp';folder.mkdir(parents=True,exist_ok=True)
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(folder/'v03-frente-materiais.png')
bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(folder/'v03-traseira-materiais.png')
bpy.ops.render.render(write_still=True)
report['views']=['artifacts/vehicles/rondesp/v03-frente-materiais.png','artifacts/vehicles/rondesp/v03-traseira-materiais.png']
report['visual_review']='pending; render material para comparação'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    return None
bpy.app.timers.register(reopen,first_interval=.5)
