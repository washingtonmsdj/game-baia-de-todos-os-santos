"""Conferência da fonte reaberta e duas vistas para comparação fotográfica."""
import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector
repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
path=repo/'docs/reports/blender/rondesp_marrom_v01.json'
report=json.loads(path.read_text(encoding='utf-8'))
assert scene.name==report['scene']
assert Path(bpy.data.filepath).resolve()==(repo/report['file']).resolve()
assert len(bpy.data.scenes)==1
assert not any(o.name.startswith('TOR04') for o in scene.objects)
assert report['sha256']==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
wheels=[o for o in scene.objects if o.name.startswith('RDP01 | Eixo giro roda')]
doors=[o for o in scene.objects if o.name.startswith('RDP01 | Pivô porta')]
assert len(wheels)==4 and len(doors)==4
report['reopened']={'ok':True,'scenes':1,'objects':len(scene.objects),'wheel_pivots':4,'door_pivots':4,'vehicle_source_separate':True}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scene.render.engine='CYCLES'
scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.resolution_x=1100
scene.render.resolution_y=730
scene.render.resolution_percentage=100
out=repo/'artifacts/vehicles/rondesp'
out.mkdir(parents=True,exist_ok=True)
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(out/'frente-lateral.png')
bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.04))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(out/'traseira-lateral.png')
bpy.ops.render.render(write_still=True)
# Deixa a vista frontal na janela, sem mudar o hash da fonte conferida.
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active
            s.shading.type='MATERIAL'
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
            s.region_3d.view_location=(0,0,1)
            s.region_3d.view_distance=7
            s.region_3d.view_perspective='ORTHO'
report['visual_review']='duas vistas renderizadas para comparação; inspeção visual pendente'
report['views']=['artifacts/vehicles/rondesp/frente-lateral.png','artifacts/vehicles/rondesp/traseira-lateral.png']
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
