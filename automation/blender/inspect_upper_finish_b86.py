import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']).inverted()
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
rows=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    if obj.name.startswith(('NAV | passarela superior','SUPERIOR | parede lateral saguão','B77 | COLLISION | NAV |','B80 | COLLISION | passarela piso visual','LAC R30B | Passarela | piso paginado visual','PASSARELA EXTERNA | vidro','PASSARELA EXTERNA | caixilho.012')):
        points=[M@wm(obj)@v.co for v in obj.data.vertices]
        rows.append({'name':obj.name,'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
                     'collections':[c.name for c in obj.users_collection],'materials':[m.name for m in obj.data.materials if m],
                     'properties':{k:str(obj[k]) for k in obj.keys()},'visible':obj.visible_get()})
report={'dirty':bpy.data.is_dirty,'file':bpy.data.filepath,'rows':rows,
        'runtime_collections':[c.name for c in bpy.data.collections if 'RUNTIME' in c.name or c.name=='33.3 RUNTIME | WALKABLE']}
(root/'docs/reports/blender/lacerda-layout-b86/finish_before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
