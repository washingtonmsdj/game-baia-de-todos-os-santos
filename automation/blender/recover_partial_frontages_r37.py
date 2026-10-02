"""Reverte somente o passe parcial de fachadas; não reabre ou muda a cena inteira."""
import bpy, json, runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rows=json.loads((root/'artifacts/cidade-baixa/frontage_controls_r37.json').read_text(encoding='utf8'))
names=[n for row in rows['buildings'] for n in [row['body'],*row['components']]]
for o in list(bpy.data.objects):
    if not o.users_scene and o.name.rsplit('.',1)[0] in names: bpy.data.objects.remove(o,do_unlink=True)
r36=json.loads((root/'docs/reports/blender/terracos_palacio_r30b36.json').read_text(encoding='utf8'))
source=root/r36['source_before']['file']; before=set(bpy.data.objects)
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))
with bpy.data.libraries.load(str(source),link=False) as (available,loaded): loaded.objects=list(names)
loaded_by_name=dict(zip(names,loaded.objects))
for row in rows['buildings']: assert helpers['signature'](loaded_by_name[row['body']])==row['before']
for name,original in zip(names,loaded.objects):
    o=bpy.context.scene.objects[name]; o.data=original.data.copy()
    for k in list(o.keys()): del o[k]
    for k,v in original.items(): o[k]=v
    for mod in list(o.modifiers):
        if mod.name=='Arestas de fachada R37': o.modifiers.remove(mod)
for o in set(bpy.data.objects)-before: bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.get('ENVIRONMENT_FINAL | Fachadas Cidade Baixa R37')
if col:
    for o in list(col.objects):
        assert o.name.startswith('BAIXA R37 |'); bpy.data.objects.remove(o,do_unlink=True)
for row in rows['buildings']: assert helpers['signature'](bpy.context.scene.objects[row['body']])==row['before']
print('Passe parcial revertido nos 18 componentes; fonte B36 preservada.')
