"""Remove somente faces de área nula do colisor, preservando superfície útil."""
import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'));ob=s.objects[c['export']['terrain_proxy']]
def bad_faces():
    me=ob.data;me.calc_loop_triangles();xyz=np.array([list(v.co) for v in me.vertices],dtype=np.float64);tri=np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
    area=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
    return sorted({me.loop_triangles[int(i)].polygon_index for i in np.flatnonzero(area<1e-9)})
bad=bad_faces();before_vertices=len(ob.data.vertices);before_faces=len(ob.data.polygons)
bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
affected=[bm.faces[i] for i in bad]
bmesh.ops.triangulate(bm,faces=affected,quad_method='BEAUTY',ngon_method='EAR_CLIP')
zero=[f for f in bm.faces if f.calc_area()<1e-9]
bmesh.ops.delete(bm,geom=zero,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
# BMesh calc_area usa precisão simples; conferir e remover pelo cálculo float64.
extra_removed=0
for _ in range(4):
    remaining=bad_faces()
    if not remaining:break
    bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
    faces=[bm.faces[i] for i in remaining]
    bmesh.ops.triangulate(bm,faces=faces,quad_method='BEAUTY',ngon_method='EAR_CLIP')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    remaining=bad_faces()
    if not remaining:break
    bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
    faces=[bm.faces[i] for i in remaining]
    assert all(len(f.verts)==3 for f in faces),'Não remover polígono com superfície útil'
    extra_removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
remaining=bad_faces();assert not remaining,'Triângulos degenerados restantes'
report['proxy_topology_cleanup']={'classification':'ERROR','baseline_b38_degenerate_triangles':8,'before_affected_polygons':len(bad),'zero_area_faces_removed':len(zero)+extra_removed,'remaining_degenerate_polygons':len(remaining),'vertices_before':before_vertices,'vertices_after':len(ob.data.vertices),'faces_before':before_faces,'faces_after':len(ob.data.polygons),'method':'Triangulação somente das faces afetadas e remoção de faces com área <1e-9 m². Nenhum preenchimento ou deslocamento do terreno visual.'}
report['source_reopened']=False
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report['source_after']['sha256']=hashlib.sha256((r/report['source_after']['file']).read_bytes()).hexdigest()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['proxy_topology_cleanup']))