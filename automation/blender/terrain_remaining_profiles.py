"""Inspeção localizada dos alertas de quatro rodas, sem modificar a cena."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
t=bpy.context.scene.objects[c['export']['road_object']];t.data.calc_loop_triangles();tris=list(t.data.loop_triangles)
tree=BVHTree.FromPolygons([t.matrix_world@v.co for v in t.data.vertices],[list(f.vertices) for f in tris],all_triangles=True)
def hit(p):
    q,n,i,d=tree.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)
    return {'xy':list(p.to_2d()),'z':q.z if q else None,'material':t.data.materials[tris[i].material_index].name if q else None,'normal':list(n) if q else None}
g=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in g['nodes']};edges={e['id']:e for e in g['edges']}
r=json.loads((root/'docs/reports/blender/terrain_vehicle_replay_r30b25.json').read_text());out=[]
for s in r['segments']:
    if not s['issues']:continue
    e=edges[s['edge_id']];a=Vector((*nodes[e['from']]['blender_xy'],0));b=Vector((*nodes[e['to']]['blender_xy'],0));f=(b-a).normalized();side=Vector((-f.y,f.x,0));steps=math.ceil((b-a).length/1.5)
    poses=[]
    for i in sorted({x['sample'] for x in s['issues']}):
        p=a.lerp(b,i/steps)
        poses.append({'sample':i,'center':hit(p),'wheels':[hit(p+f*u+side*v) for u,v in [(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84)]], 'longitudinal':[hit(p+f*u) for u in [-3,-2,-1,0,1,2,3]]})
    out.append({'edge_id':e['id'],'name':s['name'],'from':e['from'],'to':e['to'],'tags':e,'poses':poses})
report={'source':c['world_source'],'scene_changed':False,'segments':out}
(root/'docs/reports/blender/terrain_remaining_profiles.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
for s in out:
    if s['edge_id']=='way-421206045-seg-7':print(json.dumps(s,ensure_ascii=False))
print(json.dumps({'segments_inspected':len(out),'poses_inspected':sum(len(s['poses']) for s in out),'scene_changed':False}))
