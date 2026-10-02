import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];r=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'));wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix'];out=[]
for name in r['terrain_names']:
    o=bpy.context.scene.objects[name];me=o.data;me.calc_loop_triangles();M=wm(o);tri=list(me.loop_triangles);b=BVHTree.FromPolygons([M@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True)
    rows=[]
    for s in r['galleries']['segments']:
        p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world'])
        for j in range(s['arch_count']):
            for depth in (.45,2.1,3.95):
                pos=p+u*((j+.5)*s['length_from_existing_controls_m']/s['arch_count'])-n*depth;hit=b.ray_cast(Vector((pos.x,pos.y,140)),Vector((0,0,-1)),250)
                if hit[0] is None or hit[0].z>=p.z-.12:
                    t=tri[hit[2]] if hit[0] else None;poly=me.polygons[t.polygon_index] if t else None
                    rows.append({'gallery':s['name'],'bay':j,'depth':depth,'terrain_z':hit[0].z if hit[0] else None,'material':me.materials[poly.material_index].name if poly and len(me.materials)>poly.material_index else None,'vertices':[list(M@me.vertices[i].co) for i in t.vertices] if t else [],'triangle_index':hit[2] if hit[0] else None})
    out.append({'object':name,'occupied':rows})
path=root/'artifacts/palacio-rio-branco/gallery_proxy_occupation_r35.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(out,ensure_ascii=False))
