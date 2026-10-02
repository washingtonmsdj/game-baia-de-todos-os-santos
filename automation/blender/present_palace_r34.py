"""Enquadra o trabalho novo na janela adotada e preserva a vista no arquivo."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json'
r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
T=Matrix(r['palace']['frame_world']);target=T@Vector((-2,-8,11));eye=T@Vector((-60,44,36))
for o in bpy.context.selected_objects:o.select_set(False)
body=scene.objects[r['palace']['object']];body.select_set(True);bpy.context.view_layer.objects.active=body
areas=0
for area in bpy.context.screen.areas:
    if area.type!='VIEW_3D':continue
    space=area.spaces.active;space.clip_end=2500;space.clip_start=.05
    region=space.region_3d;region.view_location=target;region.view_rotation=(eye-target).to_track_quat('Z','Y');region.view_distance=(eye-target).length;region.view_perspective='PERSP'
    # Respeita o modo de visualização existente escolhido pelo usuário.
    if space.shading.type=='SOLID':space.shading.color_type='MATERIAL'
    area.tag_redraw();areas+=1
scene['architecture_review_status']='R30B.34 | modelagem candidata revista visualmente; gameplay pendente'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
r['presentation']={'viewport_areas':areas,'focus':'Palácio Rio Branco','saved_in_source':True}
r['visual_review']='pending_final_material_review'
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'focused_areas':areas,'source_after':r['source_after']},ensure_ascii=False))
