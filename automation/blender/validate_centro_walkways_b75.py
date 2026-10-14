"""Conferência das partições B75 após reabrir na janela única."""
import bpy,json,hashlib,runpy
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/centro-expansion'
report=json.loads((folder/'scene_b75.json').read_text(encoding='utf8'));after=report['source_after']
assert Path(bpy.data.filepath).resolve()==(root/after['file']).resolve()
assert hashlib.file_digest((root/after['file']).open('rb'),'sha256').hexdigest()==after['sha256']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==after['file'] and proof['load_post_completed']
derivation=json.loads((folder/'walkways_b75_derivation.json').read_text(encoding='utf8'))
data=np.load(root/derivation['mesh_file']);covered=[]
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
changed=[n for n,v in report['protected_signatures'].items() if signature(bpy.context.scene.objects[n])!=v];assert not changed
for part in report['partitions']:
    ob=bpy.context.scene.objects[part['object']];selected=np.flatnonzero(data['osm_way_ids']==part['osm_id']);used=np.unique(data['faces'][selected])
    actual=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',actual)
    assert np.array_equal(actual.reshape(-1,3),data['vertices'][used])
    loops=np.empty(len(ob.data.loops),np.int32);ob.data.loops.foreach_get('vertex_index',loops)
    assert np.array_equal(used[loops].reshape(-1,3),data['faces'][selected])
    assert len(np.unique(loops))==len(ob.data.vertices), 'Vértices órfãos'
    if part['osm_id']:assert ob['boas_osm_id']==part['osm_id'] and not ob['boas_walkability_approved']
    covered.extend(selected.tolist())
assert np.array_equal(np.sort(covered),np.arange(len(data['faces'])))
assert bpy.context.scene.camera.name==report['driver_camera']
result={'source':after,'source_reopened':True,'load_post_completed':True,'saved_partitions_exact':True,'orphan_vertices':0,
        'faces_covered_exactly_once':True,'protected_changes':changed,'walkway_count':report['walkway_count'],'topology':derivation['topology'],
        'driver_camera_preserved':True,'motor_roads_built':False,'new_physics_test':False,'walkability_approved':False,'production_ready':False}
(folder/'validation_b75.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
