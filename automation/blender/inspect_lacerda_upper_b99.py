"""Inventário das envoltórias superiores na B99 visível, sem mutação."""
import bpy,json,runpy,os,hashlib
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b99_subsolos_corpo_cidade_alta.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
prior=json.loads((root/'docs/reports/blender/lacerda-structure-b99/application.json').read_text());expected=dict(prior['preserved_signatures'])
for row in prior['added']:expected[row['object']]=row['after']['signature']
delta=[n for n,s in expected.items() if sig(scene.objects[n])!=s]
rows=[]
for n in expected:
 o=scene.objects[n]
 if o.type!='MESH' or not o.visible_get():continue
 p=[list(inv@wm(o)@v.co) for v in o.data.vertices];bb=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 if not (-24<bb[0][0]<7 and bb[2][1]>74.):continue
 rows.append({'object':n,'signature':sig(o),'bounds':bb,'visible':o.visible_get(),'vertices_local':p,'faces':[list(f.vertices) for f in o.data.polygons],'material_ids':[f.material_index for f in o.data.polygons],'materials':[m.name if m else None for m in o.data.materials],'collections':[c.name for c in o.users_collection],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}})
out=root/'docs/reports/blender/lacerda-upper-body-b100';out.mkdir(parents=True,exist_ok=True)
r={'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':scene.name,'pid':os.getpid(),'dirty':bpy.data.is_dirty,'session_geometry_delta':delta,'preserved_signatures':expected,'rows':rows}
(out/'before.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not delta,delta
print(json.dumps({'file':r['file'],'dirty':r['dirty'],'compared':len(expected),'rows':[{'object':v['object'],'bounds':v['bounds']} for v in rows if len(v['faces'])<50]},ensure_ascii=False))
