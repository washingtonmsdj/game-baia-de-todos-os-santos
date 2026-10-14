"""Verifica reabertura, preservação e follow de proxies dinâmicos na B79."""
import bpy,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller'
scene=bpy.context.scene;r=json.loads((OUT/'scene_b79.json').read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(ROOT/r['source_after']['file']).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==r['source_after']['sha256']
scene.frame_set(r['baseline_frame']);bpy.context.view_layer.update()
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
baseline=json.loads((ROOT/'artifacts/lacerda-controller/protected_b77b_b79.json').read_text(encoding='utf8'));changes=[]
for name,old in baseline.items():
    o=scene.objects.get(name)
    if not o:changes.append({'object':name,'reason':'missing'});continue
    try:s=sig(o)
    except RuntimeError:s={'type':o.type,'transform':[list(row) for row in o.matrix_world],'constraints':[(c.name,c.type) for c in o.constraints]}
    now={'signature':s,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],
         'hide_render':o.hide_render,'visible':o.visible_get(),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None}
    if json.loads(json.dumps(now))!=old:changes.append({'object':name,'reason':'geometry_transform_material_parent_visibility_action'})
assert not changes,changes[:12]
dg=bpy.context.evaluated_depsgraph_get();proxy_tests=[]
for frame in (65000,65024,66737,66977,67025):
    scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for binding in r['bindings']:
        ob=scene.objects[binding['object']];src=scene.objects[binding['source']]
        if not binding['moving']:continue
        error=max(abs(ob.matrix_world[i][j]-src.matrix_world[i][j]) for i in range(4) for j in range(4))
        assert error<1e-5
        proxy_tests.append({'object':ob.name,'frame':frame,'source_matrix_error':error})
ssot=hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot==r['ssot_sha256']
protected=[]
for revision in ('R30B.76','R30B.77B','R30B.78'):
    entry=next(x for x in json.loads((ROOT/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['revisions'] if x['revision']==revision)
    with (ROOT/entry['file']).open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
    assert actual==entry['sha256'];protected.append({'revision':revision,'sha256':actual})
scene.frame_set(65024)
proof=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
report={'revision':'R30B.79','source':r['source_after'],'reopened':True,'open_evidence':'artifacts/blender-sessions/last-open.json',
        'original_objects_preserved':len(baseline),'unauthorized_changes':changes,'objects_after':len(scene.objects),
        'protected_sources':protected,'dynamic_binding_checks':len(proxy_tests),'dynamic_binding_max_matrix_error':max(x['source_matrix_error'] for x in proxy_tests),
        'ssot_preserved':True,'visual_geometry_changed':False,'engine_controller_verified':False,
        'status':'preservation_passed_geometry_blocked','trip_approved':False}
(OUT/'validation_b79.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
