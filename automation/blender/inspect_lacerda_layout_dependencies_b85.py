"""Inspeção limitada das peças visíveis do marco, sem mutação."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend'
frame=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame'])
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
rows=[]
for obj in bpy.context.scene.objects:
    col=[c.name for c in obj.users_collection]
    if not (obj.get('boas_location_id')=='elevador-lacerda' or any(c.startswith(('11 ELEVADOR','12 LACERDA','13 LACERDA','30 LACERDA','31 LACERDA','HERO | Lacerda')) for c in col)):continue
    if obj.type!='MESH':continue
    points=[frame.inverted()@wm(obj)@v.co for v in obj.data.vertices]
    rows.append({'name':obj.name,'visible':obj.visible_get(view_layer=bpy.context.scene.view_layers[0]),'collections':col,'bounds':[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]], 'vertices':len(points),'constraints':[(c.name,c.type) for c in obj.constraints],'parent':obj.parent.name if obj.parent else None,'animated':bool(obj.animation_data),'source':obj.get('boas_derived_from_object')})
out=root/'docs/reports/blender/lacerda-layout-b86';out.mkdir(parents=True,exist_ok=True)
(out/'dependencies_before.json').write_text(json.dumps({'pid':os.getpid(),'file':bpy.data.filepath,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'pid':os.getpid(),'objects':len(rows),'visible':sum(r['visible'] for r in rows),'collections':sorted({c for r in rows if r['visible'] for c in r['collections']})},ensure_ascii=False))
