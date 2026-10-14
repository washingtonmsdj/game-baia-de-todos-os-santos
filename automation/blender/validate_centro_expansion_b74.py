"""Conferir reabertura B74 e preservação, sem modificar a cena."""
import bpy,json,numpy as np,hashlib,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/centro-expansion'
report=json.loads((folder/'scene_b74.json').read_text(encoding='utf8'));after=report['source_after']
assert Path(bpy.data.filepath).resolve()==(root/after['file']).resolve()
assert hashlib.file_digest((root/after['file']).open('rb'),'sha256').hexdigest()==after['sha256']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==after['file'] and proof['load_post_completed']
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
changed=[n for n,v in report['preservation_signatures'].items() if signature(bpy.context.scene.objects[n])!=v]
assert not changed
ground=bpy.context.scene.objects[report['terrain_object']]
xyz=np.empty(len(ground.data.vertices)*3,np.float32);ground.data.vertices.foreach_get('co',xyz);xyz=xyz.reshape(-1,3)
expected=np.load(root/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/candidate_terrain.npz')
faces=np.empty(len(ground.data.loops),np.int32);ground.data.loops.foreach_get('vertex_index',faces)
assert np.array_equal(xyz,expected['vertices']) and np.array_equal(faces.reshape(-1,3),expected['faces'])
bindings=[]
for name in report['target_objects']:
    ob=bpy.context.scene.objects[name];assert ob.get('boas_location_id') and ob.get('boas_osm_id')
    bindings.append({'object':name,'location_id':ob['boas_location_id'],'osm_id':ob['boas_osm_id'],'reference_only':bool(ob.get('boas_reference_only'))})
topology=json.loads((folder/'candidate_mesh_topology.json').read_text(encoding='utf8'))
assert topology['degenerate_triangles_after_float32']==0 and topology['edges_more_than_two_faces']==0 and topology['open_edges_off_expected_boundary_over_5mm']==0
result={'source':after,'source_reopened':True,'load_post_completed':True,'saved_arrays_exact':True,'protected_changes':changed,'target_bindings':bindings,'terrain_topology':topology,'driver_camera_exists':report['qa']['driver_camera'] in bpy.context.scene.objects,'local_geometry_checks_passed':True,'city_approval':False,'production_ready':False,'pending':['Altimetria absoluta e resolução nativa','Vias finais, pavimento, faixas e larguras reais','106 amostras com grade acima do critério candidato','Colisão volumétrica e física do veículo','Acessos aos locais e Hero assets']}
(folder/'validation_b74.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='terrain_topology'},ensure_ascii=False))
