import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));R=Matrix(r['tower_alignment']['rotation_world'])
target=R@Vector((-32,4.25,48));eye=R@Vector((-128,70,50))
for o in bpy.context.selected_objects:o.select_set(False)
body=bpy.context.scene.objects[r['tower_alignment']['objects'][0]];body.select_set(True);bpy.context.view_layer.objects.active=body
for area in bpy.context.screen.areas:
    if area.type!='VIEW_3D':continue
    space=area.spaces.active
    if space.local_view:
        region=next(region for region in area.regions if region.type=='WINDOW')
        with bpy.context.temp_override(area=area,region=region):bpy.ops.view3d.localview(frame_selected=False)
    space.clip_start=.05;space.clip_end=2500;view=space.region_3d;view.view_location=target;view.view_rotation=(eye-target).to_track_quat('Z','Y');view.view_distance=(eye-target).length;view.view_perspective='PERSP';area.tag_redraw()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
r['presentation']='Apoio da Cidade Alta enquadrado na janela e no arquivo salvo.'
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_after':r['source_after']},ensure_ascii=False))
