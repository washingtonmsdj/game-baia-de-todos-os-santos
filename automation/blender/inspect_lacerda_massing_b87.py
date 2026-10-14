"""Inventário real da arquitetura atual, somente leitura na janela visível."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b87_pisos_e_fechamentos_superiores.blend'
frame=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=helpers['world_matrix']
rows=[]
for o in bpy.context.scene.objects:
    cols=[c.name for c in o.users_collection]
    if o.type!='MESH' or not (o.get('boas_location_id')=='elevador-lacerda' or any(c.startswith(('11 ELEVADOR','12 LACERDA','13 LACERDA','30 LACERDA','31 LACERDA','HERO | Lacerda')) for c in cols)):continue
    p=[frame.inverted()@wm(o)@v.co for v in o.data.vertices]
    rows.append({'name':o.name,'visible':o.visible_get(),'collections':cols,'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'vertices':len(p),'animated':bool(o.animation_data),'parent':o.parent.name if o.parent else None,'constraints':[(c.name,c.type) for c in o.constraints], 'properties':{k:o[k] for k in o.keys() if isinstance(o[k],(str,int,float,bool))}})
out=root/'docs/reports/blender/lacerda-massing-b88';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps({'pid':os.getpid(),'file':bpy.data.filepath,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pid':os.getpid(),'objects':len(rows),'visible':sum(r['visible'] for r in rows)}))
