import bpy,bmesh,json,runpy
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2]
frame=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text(encoding='utf8'))['measurement_frame']).inverted()
wm=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['world_matrix']
rows=[]
for name in ('SUPERIOR | parede lateral saguão.001','B86_STAGING | SUPERIOR | parede lateral saguão.001'):
    obj=bpy.data.objects.get(name)
    if not obj:continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    bad=[f for f in bm.faces if f.calc_area()<1e-8]
    rows.append({'object':name,'users_scene':len(obj.users_scene),'faces':len(bm.faces),'degenerate_faces':len(bad),
                 'bad_faces':[{'area':f.calc_area(),'verts':[list(frame@wm(obj)@v.co) for v in f.verts]} for f in bad[:12]],
                 'vertices':[list(frame@wm(obj)@v.co) for v in bm.verts]})
    bm.free()
result={'dirty':bpy.data.is_dirty,'rows':rows,'staging_objects':sum(o.name.startswith('B86_STAGING | ') for o in bpy.data.objects)}
(root/'docs/reports/blender/lacerda-layout-b86/staging_failure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
