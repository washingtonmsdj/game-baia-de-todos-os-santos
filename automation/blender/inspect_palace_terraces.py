"""Lê controles existentes entre a fachada marítima, encosta e ladeira."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
r=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));T=Matrix(r['palace']['frame_world']);up=Vector((0,0,1))
plan=[Vector((*p,70)) for p in r['palace']['footprint_before_world']];p,q=plan[0],plan[1];u=(q-p).normalized();n=Vector((-u.y,u.x,0));length=(q-p).length
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix'];o=scene.objects['MVP | terreno corrigido | colisão estática'];M=wm(o);me=o.data;me.calc_loop_triangles();tri=list(me.loop_triangles)
b=BVHTree.FromPolygons([M@v.co for v in me.vertices],[list(t.vertices) for t in tri],all_triangles=True)
rows=[]
for fraction in (.05,.25,.5,.75,.95):
    values=[]
    for d in range(-2,53,2):
        c=p+u*(fraction*length)+n*d;hit=b.ray_cast(Vector((c.x,c.y,140)),Vector((0,0,-1)),250)
        values.append({'outward_m':d,'z':hit[0].z if hit[0] else None,'material':me.materials[me.polygons[tri[hit[2]].polygon_index].material_index].name if hit[0] else None})
    rows.append({'along_fraction':fraction,'samples':values})
result={'file':bpy.data.filepath,'scene':scene.name,'origin_world':list(p),'along_world':list(u),'outward_world':list(n),'length_m':length,'palace_base_m':70,'samples':rows,'source':'Controles do footprint OSM 402383814 herdado e mesh atual; não levantamento adicional'}
out=root/'artifacts/palacio-rio-branco/terrace_controls.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
