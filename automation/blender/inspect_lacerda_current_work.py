"""Reconcilia alterações da sessão e inventaria interfaces, sem editar a cena."""
import bpy,json,runpy,hashlib,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
cat=json.loads((root/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text());source=cat['authoring_source']
assert Path(bpy.data.filepath).resolve()==(root/source['file']).resolve(), 'Não mudar a fonte aberta'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
q=json.loads((root/'docs/reports/blender/lacerda-vestibules-b97/application.json').read_text());expected=dict(q['preserved_signatures'])
for row in q['added']:expected[row['object']]=row['after']['signature']
differences=[]
for name,s in expected.items():
 o=scene.objects.get(name)
 if o is None:differences.append({'object':name,'missing':True});continue
 actual=sig(o)
 if actual!=s:differences.append({'object':name,'changed_fields':[k for k in actual if actual[k]!=s.get(k)],'signature':actual})
rows=[]
for o in scene.objects:
 if o.type!='MESH' or not o.visible_get():continue
 if not any(t in o.name for t in ('FACHADA SUPERIOR','SUPERIOR |','EDIFICIO |','B97 |','B88 |','B94 |','B93 |')):continue
 p=[list(inv@wm(o)@v.co) for v in o.data.vertices];b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 row={'object':o.name,'bounds':b,'signature':sig(o),'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'modifiers':[(m.name,m.type) for m in o.modifiers]}
 if 'FACHADA SUPERIOR' in o.name or 'piso saguão' in o.name:row.update(vertices_local=p,faces=[list(f.vertices) for f in o.data.polygons])
 rows.append(row)
out=root/'docs/reports/blender/lacerda-completion-b98';out.mkdir(parents=True,exist_ok=True)
r={'file':source['file'],'registered_sha256':source['sha256'],'file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'pid':os.getpid(),'scene':scene.name,'frame':scene.frame_current,'dirty':bpy.data.is_dirty,'compared':len(expected),'session_geometry_delta':differences,'rows':rows}
(out/'before.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':r['file'],'hash_matches':r['file_sha256']==r['registered_sha256'],'dirty':r['dirty'],'session_delta':differences,'interfaces':[{'object':v['object'],'bounds':v['bounds']} for v in rows if not any(t in v['object'] for t in ('janela','lâmina','grade','folha','bandeira','rodap','lambr'))]},ensure_ascii=False))
runpy.run_path(str(root/'automation/blender/capture_current_map_view.py'),init_globals={'BOAS_CAPTURE_FILENAME':'current-user-session-before-b98.png'})
