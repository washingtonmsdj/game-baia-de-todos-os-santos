"""Reabertura e leitura do perfil corrigido; sem captura OpenGL."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision']!='R30B.25':raise RuntimeError('Revisão R30B25 esperada')
bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']));o=bpy.context.scene.objects[c['export']['road_object']];o.data.calc_loop_triangles();tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
rows=[]
for x,y in [(-163.5,-171.14),(-165.48,-173.31),(-167.45,-175.48),(-169.43,-177.65)]:
    heights=[]
    for d in [-1,0,1]:
        p=tree.ray_cast(Vector((x-.74*d,y+.67*d,150)),Vector((0,0,-1)),250)[0];heights.append(p.z if p else None)
    rows.append({'xy':[x,y],'heights_m':heights,'crossfall_delta_m':abs(heights[2]-heights[0]) if all(z is not None for z in heights) else None})
path=root/'docs/reports/blender/terrain_junction_finish.json';r=json.loads(path.read_text());r['reopened']=True;r['cross_sections_after']=rows;r['visual_review']='pending; viewport positioned at junction, no OpenGL capture';path.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type=='VIEW_3D':
            target=Vector((-165,-172,58));eye=Vector((-192,-195,82));v=area.spaces.active.region_3d;v.view_location=target;v.view_distance=(eye-target).length;v.view_rotation=(target-eye).to_track_quat('-Z','Y');v.view_perspective='PERSP';v.update()
print(json.dumps({'reopened':True,'source':c['world_source'],'cross_sections':rows},ensure_ascii=False))
