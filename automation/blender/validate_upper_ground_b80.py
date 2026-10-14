"""Preservação B79, collider–piso e reabertura; não aprova movimento."""
import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller-b80'
r=json.loads((OUT/'scene_b80.json').read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(ROOT/r['source_after']['file']).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==r['source_after']['sha256']
open_proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert open_proof['sha256']==r['source_after']['sha256'] and open_proof['load_post_completed']
scene.frame_set(31978);bpy.context.view_layer.update();sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
baseline=json.loads((ROOT/'artifacts/lacerda-controller/protected_b79_b80.json').read_text(encoding='utf8'));changes=[]
for name,old in baseline.items():
    o=scene.objects.get(name)
    if not o:changes.append(name);continue
    try:s=sig(o)
    except RuntimeError:s={'type':o.type,'transform':[list(row) for row in o.matrix_world],'constraints':[(c.name,c.type) for c in o.constraints]}
    now={'signature':s,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],
      'hide_render':o.hide_render,'visible':o.visible_get(),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
    if json.loads(json.dumps(now))!=old:changes.append(name)
assert not changes,changes[:10]
scene.frame_set(65024);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
src=scene.objects[r['new_floor_source']];ev=src.evaluated_get(dg);mesh=ev.to_mesh()
try:
    mesh.calc_loop_triangles();points=[ev.matrix_world@v.co for v in mesh.vertices]
    tree=BVHTree.FromPolygons(points,[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
    proxy=scene.objects['B80 | COLLISION | passarela piso visual'];errors=[]
    for v in proxy.data.vertices:
        hit=tree.find_nearest(proxy.matrix_world@v.co);assert hit[0] is not None;errors.append(hit[3])
finally:ev.to_mesh_clear()
assert max(errors)<1e-4
catalog=json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'));protected=[]
for revision in ('R30B.76','R30B.77B','R30B.78','R30B.79'):
    entry=next(x for x in catalog['revisions'] if x['revision']==revision)
    with (ROOT/entry['file']).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
    assert actual==entry['sha256'];protected.append({'revision':revision,'sha256':actual})
assert hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
report={'source':r['source_after'],'reopened':True,'original_objects_preserved':len(baseline),'objects_after':len(scene.objects),
    'unauthorized_changes':changes,'floor_collider_max_vertex_distance_to_visual':max(errors),'protected_sources':protected,
    'B78_merged':False,'architecture_changed':False,'ssot_preserved':True,'physics_approved':False,'movement_controller_enabled':False,
    'status':'preservation_and_floor_binding_passed; upper_support_and_shaft_pending'}
(OUT/'validation_b80.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
