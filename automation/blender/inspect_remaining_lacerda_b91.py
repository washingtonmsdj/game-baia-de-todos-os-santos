"""Peças legadas fora da seleção B88; triagem explícita, sem correção em massa."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b91_integridade_malha_e_apoios.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
inv=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']).inverted()
prior=json.loads((root/'docs/reports/blender/lacerda-massing-b88/before.json').read_text())
r88=json.loads((root/'docs/reports/blender/lacerda-massing-b88/application.json').read_text());r91=json.loads((root/'docs/reports/blender/lacerda-mesh-b91/application.json').read_text())
known={r['object'] for r in r88['changes']+r88['added']+r91['changes']+r91['added']}
names={r['name'] for r in prior['rows'] if r['visible'] and r['name'] not in known}
names.update(o.name for o in bpy.context.scene.objects if o.name.startswith('CALIBRADO |'))
rows=[]
for name in sorted(names):
 o=bpy.context.scene.objects.get(name)
 if o is None or not o.visible_get() or o.type!='MESH':continue
 p=[inv@wm(o)@v.co for v in o.data.vertices]
 rows.append({'object':name,'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'collections':[c.name for c in o.users_collection],'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))},'signature':sig(o)})
path=root/'docs/reports/blender/lacerda-mesh-b91/remaining-legacy.json';path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'visible_remaining':len(rows),'structural':[{k:r[k] for k in ('object','bounds','collections')} for r in rows if any(s in r['object'].casefold() for s in ['calibrado','cobertura','piso','parede','apoio','estrutura','intradorso'])],
 'proxy_changed_source_bindings':[{'object':o.name,'key':k,'source':o[k]} for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects for k in ('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object') if isinstance(o.get(k),str) and o[k] in {r['object'] for r in r91['changes']}]},ensure_ascii=False))
