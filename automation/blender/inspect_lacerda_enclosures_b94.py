"""Envoltórias superiores existentes na B94, sem alteração geométrica."""
import bpy,json,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted();scene=bpy.context.scene
names=set()
for folder in ('lacerda-massing-b88','lacerda-massing-b89','lacerda-massing-b90','lacerda-mesh-b91','lacerda-bridge-b92','lacerda-lower-structure-b93','lacerda-closure-b94'):
    r=json.loads((root/f'docs/reports/blender/{folder}/application.json').read_text());names.update(v['object'] for v in r['changes']+r.get('added',[]))
rows=[]
for name in sorted(names):
    o=scene.objects.get(name)
    if o is None or o.type!='MESH' or not o.visible_get() or any(t in name for t in ('COLLISION','COLISÃO')):continue
    T=inv@wm(o);p=[list(T@v.co) for v in o.data.vertices]
    if not p:continue
    bounds=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
    rows.append({'object':name,'bounds':bounds,'signature':sig(o),'vertices_local':p,'faces':[list(f.vertices) for f in o.data.polygons],'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}})
out=root/'docs/reports/blender/lacerda-enclosure-b95';out.mkdir(parents=True,exist_ok=True)
(out/'before.json').write_text(json.dumps({'file':Path(bpy.data.filepath).relative_to(root).as_posix(),'pid':os.getpid(),'scene':scene.name,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{'object':r['object'],'bounds':r['bounds']} for r in rows if any(t in r['object'].lower() for t in ('parede lateral saguão','vidro lateral','passarela lateral','saguão passarela','fachada superior','caixilho','alas estruturais'))],ensure_ascii=False))
