"""Localiza apenas as amostras sem suporte após a partição."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];config=json.loads((root/'prototypes/threejs-water-lab/public/data/urban_slice.json').read_text());road=next(o for o in bpy.data.collections['41 GAMEPLAY | URBAN SLICE'].objects if o['boas_role']=='road');road.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in road.data.vertices],[list(t.vertices) for t in road.data.loop_triangles],all_triangles=True);missing=[]
for route in config['routes']:
    for a,b in zip(route['points'],route['points'][1:]):
        p=Vector((a[0],-a[2],a[1]));q=Vector((b[0],-b[2],b[1]));d=q-p;d.z=0;n=Vector((-d.y,d.x,0)).normalized();length=d.length
        for i in range(math.ceil(length)+1):
            r=p.lerp(q,i/math.ceil(length))
            for offset in [-1,0,1]:
                s=r+n*offset;hit=tree.ray_cast(Vector((s.x,s.y,150)),Vector((0,0,-1)),300)[0]
                if hit is None:
                    near=tree.find_nearest(s);missing.append({'route':route['id'],'segment':[a,b],'point':list(s),'nearest':list(near[0]) if near else None,'distance':near[3] if near else None})
(root/'artifacts/urban-slice/terrain_missing.json').write_text(json.dumps(missing,indent=2));print(json.dumps(missing))
