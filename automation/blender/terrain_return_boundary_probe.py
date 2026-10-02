"""Seções da borda recortada nas conexões OSM reais; somente leitura."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
bpy.context.view_layer.update();o=bpy.context.scene.objects[c['export']['road_object']];m=o.data;m.calc_loop_triangles();ps=[o.matrix_world@v.co for v in m.vertices];tris=list(m.loop_triangles)
bvh=BVHTree.FromPolygons(ps,[list(t.vertices) for t in tris],all_triangles=True)
def hit(x,y):
    p,n,i,d=bvh.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),350)
    return [x,y,p.z if p else None,m.materials[tris[i].material_index].name if p else None]
out={'source':c['world_source'],'south_boundary_y':min(p.y for p in ps),'sections':[]}
for y in [-280,-281,-281.24,-279,-277,-274,-271]:out['sections'].append({'y':y,'samples':[hit(x,y) for x in range(-250,-200)]})
g=json.loads((root/c['staging']['roads']).read_text());ns={n['id']:n for n in g['nodes']};out['conceicao_nodes']=[]
for e in g['edges']:
    if e['osm_way_id']!=421206045:continue
    for id in (e['from'],e['to']):
        if any(r['node']==id for r in out['conceicao_nodes']):continue
        x,y=ns[id]['blender_xy'];out['conceicao_nodes'].append({'node':id,'hit':hit(x,y)})
out['width_sections']=[]
for eid,fraction in [('way-1075624458-seg-2',.3),('way-1075624458-seg-2',.6),('way-421206045-seg-2',.5),('way-421206045-seg-3',.5)]:
    e=next(e for e in g['edges'] if e['id']==eid);a=Vector((*ns[e['from']]['blender_xy'],0));b=Vector((*ns[e['to']]['blender_xy'],0));f=(b-a).normalized();side=Vector((-f.y,f.x,0));p=a.lerp(b,fraction)
    out['width_sections'].append({'edge':eid,'fraction':fraction,'samples':[[round(i*.1,2),*hit(*(p+side*i*.1).to_2d())[2:]] for i in range(-80,81)]})
(root/'docs/reports/blender/real_return_boundary_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'width_sections':[{'edge':s['edge'],'asphalt_offsets':[p[0] for p in s['samples'] if p[2] in c['export']['road_materials']]} for s in out['width_sections']]},ensure_ascii=False))
