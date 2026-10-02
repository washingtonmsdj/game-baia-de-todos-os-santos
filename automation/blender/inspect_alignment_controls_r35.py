import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted();rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    points=[I@wm(o)@v.co for v in o.data.vertices]
    if not('apoio oposto' in o.name or o.name=='OFICIAL | Terminal alto | apoio junto encosta' or (any(k in o.name.lower() for k in ('piso','cobertura','corpo elevado','parede','terminal')) and -20<sum(p.x for p in points)/len(points)<20 and 66<min(p.z for p in points)<76)):continue
    rows.append({'name':o.name,'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)],'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection]})
(root/'artifacts/palacio-rio-branco/alignment_controls_r35.json').write_text(json.dumps({'rotation':[list(row) for row in R],'objects':rows},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'objects':rows},ensure_ascii=False))
