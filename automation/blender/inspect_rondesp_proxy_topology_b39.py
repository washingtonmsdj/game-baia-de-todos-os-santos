import bpy,json,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
def check(ob):
    me=ob.data;me.calc_loop_triangles();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);xyz=a.reshape(-1,3).astype(np.float64)
    a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tri=a.reshape(-1,3)
    areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
    bad=np.flatnonzero(areas<1e-9)
    return {'vertices':len(me.vertices),'bad_triangles':len(bad),'examples':[{'polygon':me.loop_triangles[int(i)].polygon_index,'vertices':tri[int(i)].tolist(),'points':xyz[tri[int(i)]].tolist(),'area':float(areas[i])} for i in bad[:10]]}
current=s.objects[c['export']['terrain_proxy']];now=check(current)
with bpy.data.libraries.load(str(r/'blender/salvador_lacerda_r30b38_binding_conceicao.blend'),link=False) as (a,b):b.objects=[current.name]
baseline=b.objects[0];before=check(baseline);bpy.data.objects.remove(baseline,do_unlink=True)
report={'current':now,'baseline_b38':before};(r/'artifacts/roads/rondesp/proxy_degenerate_inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report))