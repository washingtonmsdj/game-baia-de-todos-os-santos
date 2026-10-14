"""Inventário físico do corpo antigo, apoios e interfaces do túnel; sem mutação."""
import bpy,json,runpy,hashlib,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b98_frente_superior_reconciliada.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
old=json.loads((root/'docs/reports/blender/lacerda-completion-b98/application.json').read_text());expected=dict(old['preserved_signatures'])
for v in old['added']:expected[v['object']]=v['after']['signature']
delta=[n for n,s in expected.items() if sig(scene.objects[n])!=s];assert not delta,delta
rows=[]
for o in scene.objects:
 if o.type!='MESH' or not o.visible_get() or o.constraints:continue
 if not (o.get('boas_location_id')=='elevador-lacerda' or any(c.name.startswith(('08 ELEVADOR','11 ELEVADOR','12 LACERDA','13 LACERDA','30 LACERDA','31 LACERDA','HERO | Lacerda')) for c in o.users_collection)):continue
 p=[list(inv@wm(o)@v.co) for v in o.data.vertices];b=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
 if b[0][1]<-26. or b[0][0]>8. or b[2][0]>74.2:continue
 r={'object':o.name,'bounds':b,'signature':sig(o),'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'materials':[m.name if m else None for m in o.data.materials],'collections':[c.name for c in o.users_collection]}
 if any(t in o.name for t in ('apoio oposto','alas estruturais','casca','CASCA','piso do saguão','cobertura do saguão','parede lateral')):r.update(vertices_local=p,faces=[list(f.vertices) for f in o.data.polygons])
 rows.append(r)
out=root/'docs/reports/blender/lacerda-structure-b99';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps({'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'pid':os.getpid(),'scene':scene.name,'dirty':bpy.data.is_dirty,'session_geometry_delta':delta,'preserved_signatures':expected,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'file':bpy.data.filepath,'session_delta':delta,'structure':[{'object':r['object'],'bounds':r['bounds']} for r in rows if any(t in r['object'] for t in ('apoio oposto','alas estruturais','CASCA','casca','piso do saguão','cobertura do saguão','parede lateral'))]},ensure_ascii=False))
