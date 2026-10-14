"""Inspeção dos contornos abertos e vínculos, sem mudar a cena."""
import bpy,bmesh,json,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b90_cotas_exteriores_consolidadas.blend'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix']
inv=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']).inverted()
names=['FACHADA SUPERIOR | corpo elevado','SUPERIOR | lateral corpo elevado','SUPERIOR | lateral corpo elevado.001','CALIBRADO | passarela piso 28.71 x 6.00m','SUPERIOR | cobertura corpo elevado','EDIFICIO | cobertura']
rows=[]
for n in names:
 o=bpy.context.scene.objects[n];bm=bmesh.new();bm.from_mesh(o.data);tr=inv@wm(o)
 rows.append({'object':n,'boundary_edges':[[list(tr@v.co) for v in e.verts] for e in bm.edges if not e.is_manifold],
  'modifiers':[(m.name,m.type) for m in o.modifiers], 'bindings':[{'object':p.name,'key':k} for p in bpy.context.scene.objects for k in ('boas_derived_from_object','boas_source_object','boas_collision_source_object','source_object') if p.get(k)==n],
  'mesh_name':o.data.name,'mesh_users':o.data.users,'parent':o.parent.name if o.parent else None,'roof_top_vertices':[list(tr@v.co) for v in bm.verts if (tr@v.co).z>84.12] if 'cobertura' in n else []})
 bm.free()
out=root/'docs/reports/blender/lacerda-mesh-b91';(out/'contacts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
