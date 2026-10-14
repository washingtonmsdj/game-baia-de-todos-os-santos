"""Inventário read-only dos dois conjuntos e ligações, na única sessão visível."""
import bpy, json, os, runpy
from pathlib import Path
from mathutils import Matrix

root = Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name == 'salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend'
frame = Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']).inverted()
world_matrix = runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
rows = []
for scene in bpy.data.scenes:
    for obj in scene.objects:
        name = obj.name.casefold()
        if not any(t in name for t in ('cabine', 'cabina', 'túnel', 'tunel', 'saguão', 'saguao', 'torre |', 'apoio oposto')):
            continue
        bounds = None
        if obj.type == 'MESH' and obj.data.vertices:
            points = [frame @ world_matrix(obj) @ vertex.co for vertex in obj.data.vertices]
            bounds = [[min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]]
        rows.append({'scene':scene.name,'object':obj.name,'type':obj.type,'collections':[c.name for c in obj.users_collection], 'bounds_local':bounds, 'properties':dict(obj.items())})
result = {'pid':os.getpid(),'file':Path(bpy.data.filepath).name,'scene_changed':False,'objects':rows,
          'warning':'Contagem de peças/portas não é contagem de equipamentos. Identificação física exige posição e conjunto, não nome isolado.'}
output = root/'docs/reports/blender/lacerda-proportions-b85/four_elevators_inventory.json'
output.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf8')
print(json.dumps({'pid':os.getpid(),'objects':len(rows),'scene_changed':False},ensure_ascii=False))
