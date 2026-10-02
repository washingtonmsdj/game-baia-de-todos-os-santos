"""Perfis e vistas do encontro Montanha/Pau da Bandeira na fonte selecionada."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Usar a janela com a fonte ativa; não reabrir outra composição')
o=bpy.context.scene.objects[c['export']['road_object']];o.data.calc_loop_triangles();ts=list(o.data.loop_triangles);tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in ts],all_triangles=True)
rows=[]
for x,y in [(-163.5,-171.14),(-165.48,-173.31),(-167.45,-175.48),(-169.43,-177.65)]:
    rows.append({'xy':[x,y],'cross_section':[]})
    for d in [-4,-3,-2,-1,0,1,2,3,4]:
        p=Vector((x-.74*d,y+.67*d,150));hits=[]
        for _ in range(4):
            q,n,index,dist=tree.ray_cast(p,Vector((0,0,-1)),200)
            if q is None:break
            hits.append([round(q.z,4),o.data.materials[ts[index].material_index].name]);p=q-Vector((0,0,.001))
        rows[-1]['cross_section'].append([d,hits])
directory=root/'artifacts/terrain-vehicle';(directory/'junction-profiles.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
scene=bpy.context.scene;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
window=next(w for w in bpy.context.window_manager.windows if any(a.type=='VIEW_3D' for a in w.screen.areas));area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active;space.overlay.show_overlays=False;space.shading.type='SOLID';space.shading.color_type='MATERIAL'
for label,eye in [('junction-before',(-192,-195,82)),('junction-top',(-164,-173,106))]:
    target=Vector((-165,-172,58));eye=Vector(eye);r=space.region_3d;r.view_location=target;r.view_distance=(eye-target).length;r.view_rotation=(target-eye).to_track_quat('-Z','Y');r.view_perspective='PERSP';r.update();scene.render.filepath=str(directory/(label+'.png'))
    with bpy.context.temp_override(window=window,screen=window.screen,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
print(json.dumps(rows,ensure_ascii=False))
