"""Pesquisa geométrica delimitada de resíduos; não seleciona pela nomenclatura."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']).inverted();rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.visible_get() or not o.data.vertices or o.constraints:continue
 trans=M@h['world_matrix'](o);pts=[trans@Vector(v) for v in o.bound_box];b=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
 size=[v[1]-v[0] for v in b]
 if b[0][1]<-21 or b[0][0]>15 or b[1][1]<-15 or b[1][0]>15 or b[2][0]<69 or b[2][1]>76:continue
 if min(size)>.15 or max(size)<8:continue
 rows.append({'object':o.name,'bounds':b,'properties':dict(o.items()),'collections':[c.name for c in o.users_collection]})
(root/'docs/reports/blender/lacerda-exterior-b102/legacy-slivers.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps([{'object':r['object'],'bounds':r['bounds']} for r in rows],ensure_ascii=False))
