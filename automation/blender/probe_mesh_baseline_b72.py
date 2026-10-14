import bpy,json,runpy,bmesh
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rows=[]
for name in ['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B63 | VISUAL | piso contínuo até o cais']:
 me=s.objects[name].data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 rows.append({'object':name,'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'edges_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges)});bm.free()
out={'file':bpy.data.filepath,'rows':rows}
(r/'docs/reports/blender/city_seam_b72_baseline.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
