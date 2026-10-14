"""Só enquadramento na mesma cena; não altera a geometria."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name in ('salvador_lacerda_r30b89_conjunto_arquitetonico_niveis.blend','salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend')
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
mode=globals().get('BOAS_STRUCTURE_VIEW','exterior')
with bpy.context.temp_override(window=window,area=area,region=region):
    if mode=='map' and space.local_view:bpy.ops.view3d.localview(frame_selected=False)
    bpy.ops.object.select_all(action='DESELECT')
    if mode!='map' and not space.local_view:
        r=json.loads((root/'docs/reports/blender/lacerda-massing-b88/application.json').read_text())
        for row in r['changes']+r['added']:
            o=bpy.context.scene.objects[row['object']]
            if o.visible_get() and not any(t in o.name for t in ('COLLISION','COLISÃO')):o.select_set(True)
        bpy.context.view_layer.objects.active=bpy.context.scene.objects['TORRE | cornija galeria']
        bpy.ops.view3d.localview(frame_selected=False)
    space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=mode=='map'
    if mode=='plan':
        space.region_3d.view_location=M@Vector((-28.,4.,70.));space.region_3d.view_rotation=M.to_quaternion();space.region_3d.view_distance=72.
    else:
        target=M@Vector((-28.,3.,47.));eye=M.to_3x3()@Vector((-1.2,-1.7,.75))
        space.region_3d.view_location=target;space.region_3d.view_rotation=eye.to_track_quat('Z','Y');space.region_3d.view_distance=115. if mode=='exterior' else 125.
    space.region_3d.view_perspective='ORTHO';space.region_3d.update();area.tag_redraw()
    bpy.ops.object.select_all(action='DESELECT')
print(json.dumps({'view':mode,'scene':bpy.context.scene.name,'local_view':bool(space.local_view),'matrix':list(space.region_3d.view_matrix)},default=list))
