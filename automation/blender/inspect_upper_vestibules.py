"""Inventário espacial dos acessos superiores na sessão visível."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b96_encontro_corpo_cobertura.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.visible_get():continue
 p=[list(inv@wm(o)@Vector(v)) for v in o.bound_box];b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 if b[0][1]<.4 or b[0][0]>7 or b[1][1]<-11 or b[1][0]>11 or b[2][1]<70 or b[2][0]>74.2:continue
 if not any(t in o.name for t in ('SUPERIOR','B88','B94','EDIFICIO','guarda','pilar')):continue
 rows.append({'object':o.name,'bounds':b,'materials':[m.name if m else None for m in o.data.materials],'collections':[c.name for c in o.users_collection],'signature':h['signature'](o),'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}})
out=root/'docs/reports/blender/lacerda-vestibules-b97';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps({'file':bpy.data.filepath,'pid':os.getpid(),'dirty':bpy.data.is_dirty,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'object':r['object'],'bounds':r['bounds']} for r in rows],ensure_ascii=False))
