"""Validação read-only da revisão reaberta, com comparação integral à B76."""
import bpy,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/reports/blender/lacerda-corridor'
report=json.loads((out/'scene_b77.json').read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(ROOT/report['source_after']['file']).resolve()
frame=scene.frame_current;scene.frame_set(report['baseline_frame'])
snapshot=json.loads((ROOT/'artifacts/lacerda-corridor/protected_b76.json').read_text(encoding='utf8'))
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature'];differences=[]
for name,before in snapshot.items():
    ob=scene.objects.get(name)
    if not ob:differences.append({'object':name,'error':'missing'});continue
    try:now=sig(ob)
    except RuntimeError:now={'type':ob.type,'transform':[list(r) for r in ob.matrix_world],'data_name':ob.data.name if ob.data else None,'constraints':[(c.name,c.type) for c in ob.constraints]}
    # JSON transforma tuples em listas.
    now=json.loads(json.dumps(now))
    if now!=before['signature']:differences.append({'object':name,'error':'geometry_material_transform','before':before['signature'],'after':now})
    if (ob.parent.name if ob.parent else None)!=before['parent'] or [c.name for c in ob.users_collection]!=before['collections']:differences.append({'object':name,'error':'hierarchy'})
    if name not in report['changed_visibility'] and (ob.visible_get()!=before['visible'] or ob.hide_render!=before['hide_render']):differences.append({'object':name,'error':'visibility'})
    if name not in report['animated_existing_objects'] and (ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None)!=before['action']:differences.append({'object':name,'error':'action'})
collision=[]
for binding in report['collision_bindings']:
    ob=scene.objects[binding['object']];invalid=sum(not math.isfinite(value) for v in ob.data.vertices for value in v.co)
    bad_normals=sum(p.normal.z<.7 for p in ob.data.polygons)
    collision.append({**binding,'nonfinite':invalid,'bad_normals':bad_normals})
stops=[]
floor=scene.objects['FUNCIONAL | 3 piso'];t=report['timeline']
for f,expected in ((t['start'],70.11499786376953),(t['landing'],7.4059977531433105)):
    scene.frame_set(f);actual=max((floor.matrix_world@v.co).z for v in floor.data.vertices)
    stops.append({'frame':f,'expected_z':expected,'actual_z':actual,'error':abs(actual-expected)})
scene.frame_set(report['baseline_frame'])
runpy.run_path(str(ROOT/'automation/blender/probe_lacerda_portal_b77.py'))
portal=json.loads((out/'portal_probe_b77.json').read_text(encoding='utf8'))
ssot=hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest()
with (ROOT/report['source_before']['file']).open('rb') as stream:baseline_hash=hashlib.file_digest(stream,'sha256').hexdigest()
reopen=json.loads((ROOT/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert reopen['file']==report['source_after']['file'] and reopen['sha256']==report['source_after']['sha256'] and reopen['load_post_completed'], 'Reabertura da B77 ainda não comprovada'
result={'revision':'R30B.77','source_reopened':True,'reopen_evidence':reopen,'preserved_objects':len(snapshot),'object_count':len(scene.objects),'added_count':len(report['added_objects']),'differences':differences,'ssot_unchanged':ssot==report['ssot_sha256'],'b76_file_unchanged':baseline_hash==report['source_before']['sha256'],'collisions':collision,'stops':stops,'shaft_character_blocked':portal['shaft_character_blocked'],'portal_supported':all(p['support'] and p['blocker'] is None for p in portal['portal_probes']),'whole_cabin_swept_volume_verified':False,'engine_physics_verified':False,'absolute_altitude_verified':False}
result['passed']=not differences and result['ssot_unchanged'] and result['b76_file_unchanged'] and all(s['error']<.0001 for s in stops) and all(not c['nonfinite'] and not c['bad_normals'] for c in collision) and not portal['shaft_character_blocked'] and result['portal_supported']
result['revision']=report['revision'];result['lower_portal_supported']=all(p['support'] and p['blocker'] is None for p in portal['lower_portal_probes']);result['passed']=result['passed'] and result['lower_portal_supported']
(out/'validation_b77.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');scene.frame_set(frame)
print(json.dumps({k:result[k] for k in ('passed','preserved_objects','object_count','added_count','shaft_character_blocked','portal_supported')}));assert result['passed']
