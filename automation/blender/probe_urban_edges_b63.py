import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene;wa=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];wa.data.calc_loop_triangles()
vv=[wa.matrix_world@v.co for v in wa.data.vertices];wt=BVHTree.FromPolygons(vv,[list(t.vertices) for t in wa.data.loop_triangles],all_triangles=True)
co=sc.objects['MVP | terreno corrigido | colisão estática'];stats={};points=[]
for f in co.data.polygons:
 p=co.matrix_world@f.center
 if not(-300<p.x<-100 and -150<p.y<400):continue
 h=wt.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)[0]
 if h and abs(h.z-.35)<.001:
  stats[f.material_index]=stats.get(f.material_index,0)+1
  if len(points)<8:points.append([p.x,p.y,p.z,f.material_index])
rows=[]
for ob in sc.objects:
 if ob.name.startswith('B63 | VISUAL |'):
  ob.data.calc_loop_triangles();rows.append({'name':ob.name,'faces':len(ob.data.polygons),'negative_upward_faces':sum(p.normal.z<-.01 for p in ob.data.polygons),'degenerate':sum(t.area<1e-9 for t in ob.data.loop_triangles)})
report={'source':Path(bpy.data.filepath).relative_to(r).as_posix(),'core_faces_in_water_by_material':stats,'examples':points,'generated_meshes':rows}
(r/'docs/reports/blender/urban_edges_b63_geometry_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
