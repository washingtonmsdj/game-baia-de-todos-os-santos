"""Enquadramento rápido das fachadas existentes, sem render pesado."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];source=bpy.context.scene;out=root/'artifacts/cidade-baixa';out.mkdir(parents=True,exist_ok=True)
review=bpy.data.scenes.new('REVIEW TEMP | Fachadas R37');review.render.engine='BLENDER_WORKBENCH';review.display.shading.light='STUDIO';review.display.shading.color_type='MATERIAL';review.display.shading.show_shadows=True;review.display.shading.show_cavity=True;review.display.shading.cavity_type='BOTH';review.render.resolution_x=1100;review.render.resolution_y=650;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
ids={1263035780,1220650507,1220650503};r33=json.loads((root/'docs/reports/blender/cidade_baixa_r30b33.json').read_text(encoding='utf8'));names={b['body'] for b in r33['buildings']}|{n for n in r33['created_objects'] if any(str(i) in n for i in ids)}|{'MVP | terreno corrigido | colisão estática'}
if globals().get('r37_include_new'):
    rr=json.loads((root/'docs/reports/blender/cidade_baixa_r30b37.json').read_text(encoding='utf8'));names.update(rr['created_objects'])
for n in names:
    o=source.objects.get(n)
    if o and not o.hide_render:review.collection.objects.link(o)
camera=bpy.data.cameras.new('REVIEW TEMP | Camera R37');cam=bpy.data.objects.new(camera.name,camera);review.collection.objects.link(cam);review.camera=cam;camera.lens=48;camera.clip_end=600
views=[('conjunto',Vector((-117,91,26)),Vector((-67,37,15))),('frente',Vector((-119,83,16)),Vector((-71,36,14)))]
label='after' if globals().get('r37_include_new') else 'before'
try:
    bpy.context.window.scene=review
    for name,eye,target in views:
        cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(out/f'r30b37_{label}_{name}.png');bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene=source;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.scenes.remove(review)
    if not camera.users:bpy.data.cameras.remove(camera)
