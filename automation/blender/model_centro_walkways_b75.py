"""B75: passeios derivados de larguras explícitas, encaixados na superfície B74."""
import hashlib
import json
from pathlib import Path
import runpy
import bpy
import numpy as np
from mathutils import Vector, Matrix

root = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
reports = root / 'docs/reports/blender/centro-expansion'
art = root / 'artifacts/structural-pipeline/centro-lapa-tororo-fontenova'
catalog_path = root / 'world/areas/mvp-centro-lacerda/blender-revisions.json'
catalog = json.loads(catalog_path.read_text(encoding='utf8'))
source = catalog['validation_source']
assert source['revision'] == 'R30B.74'
assert Path(bpy.data.filepath).resolve() == (root / source['file']).resolve()
output = root / 'blender/salvador_lacerda_r30b75_passeios_larguras_osm.blend'
assert not output.exists(), 'Não sobrescrever revisão existente'
derivation = json.loads((reports / 'walkways_b75_derivation.json').read_text(encoding='utf8'))
assert derivation['source']['sha256'] == source['sha256']
assert derivation['topology']['internal_open_edges'] == 0 and derivation['topology']['edges_more_than_two_faces'] == 0
mesh_path = root / derivation['mesh_file']
assert hashlib.file_digest(mesh_path.open('rb'),'sha256').hexdigest() == derivation['mesh_sha256']
data = np.load(mesh_path)
xyz = data['vertices']; faces = data['faces']; materials = data['materials']; owners = data['osm_way_ids']
b74 = json.loads((reports / 'scene_b74.json').read_text(encoding='utf8'))
ground = scene.objects[b74['terrain_object']]
original = np.load(art / 'candidate_terrain.npz')
coordinates = np.empty(len(ground.data.vertices)*3, np.float32)
ground.data.vertices.foreach_get('co', coordinates)
assert np.array_equal(coordinates.reshape(-1,3), original['vertices'])
assert np.array_equal(xyz[:len(original['vertices'])], original['vertices'])
assert ground.matrix_world == Matrix.Identity(4)
signature = runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
protected_names = list(b74['preservation_signatures']) + b74['target_objects']
protected = {n:signature(scene.objects[n]) for n in protected_names}
before_names = set(scene.objects.keys()); before_camera = scene.camera.name if scene.camera else None
collection = bpy.data.collections.get('41 | CENTRO | PASSEIOS CANDIDATOS B75')
if collection:
    assert not collection.objects and collection.get('boas_role')=='SIDEWALK_WALKABLE_CANDIDATE', 'Retomada exige coleção vazia deste passe'
else:
    collection=bpy.data.collections.new('41 | CENTRO | PASSEIOS CANDIDATOS B75')
    scene.collection.children.link(collection)
collection['boas_role'] = 'SIDEWALK_WALKABLE_CANDIDATE'
collection['boas_production_ready'] = False

def material(name, color):
    mat=bpy.data.materials.get(name)
    if mat: assert mat.users==0, 'Não alterar material já usado'
    else: mat=bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1); mat.use_nodes=True
    node=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if node is None:
        node=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output_node=next((n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(node.outputs['BSDF'],output_node.inputs['Surface'])
    node.inputs['Base Color'].default_value = (*color,1); node.inputs['Roughness'].default_value=.9
    return mat

mats = {1:material('B75 | concreto indicado OSM',(.43,.43,.40)),
        2:material('B75 | pavimentado acabamento pendente',(.49,.47,.43)),
        3:material('B75 | asfalto pedonal indicado OSM',(.085,.09,.095)),
        4:material('B75 | passeio superfície pendente',(.34,.33,.30))}

def mesh(name, selected_faces, mat):
    used, inverse = np.unique(selected_faces.flatten(), return_inverse=True)
    me = bpy.data.meshes.new(name)
    me.from_pydata(xyz[used].tolist(), [], inverse.reshape(-1,3).tolist()); me.update()
    me.materials.append(mat)
    return me, used

created = []; partitions = []
old_ground_data = ground.data
try:
    remaining, used = mesh('B75 | terreno recortado para passeios', faces[owners==0], old_ground_data.materials[0])
    partitions.append({'object':ground.name,'osm_id':0,'vertices':len(used),'triangles':int(np.sum(owners==0))})
    for feature in derivation['features']:
        way = feature['osm_id']; chosen = owners == way
        if not np.any(chosen): continue
        me, used = mesh('B75 | passeio OSM '+str(way),faces[chosen],mats[feature['material_index']])
        ob = bpy.data.objects.new(me.name,me); collection.objects.link(ob); created.append(ob)
        ob['boas_osm_id']=way; ob['boas_osm_type']=feature['osm_type']; ob['boas_revision']='R30B.75'
        ob['boas_source_capture_id']=derivation['source_capture_id']; ob['boas_source_width_m_tagged']=feature['width_m_tagged']
        ob['boas_width_blender_candidate']=feature['width_blender_candidate']; ob['boas_width_survey_verified']=False
        ob['boas_surface_source_tag']=feature['tags'].get('surface','pending'); ob['boas_role']='SIDEWALK_WALKABLE_CANDIDATE'
        ob['boas_walkability_approved']=False; ob['boas_production_ready']=False; ob['boas_classification']='ADAPT_LOCAL'
        ob['boas_terrain_surface']=True; ob['boas_vertical_absolute_approved']=False
        ob['boas_derivation']='docs/reports/blender/centro-expansion/walkways_b75_derivation.json'
        partitions.append({'object':ob.name,'osm_id':way,'vertices':len(used),'triangles':int(np.sum(chosen))})
    ground.data = remaining
    ground['boas_surface_partition_revision']='R30B.75'
    ground['boas_walkways_are_embedded_not_raised_overlay']=True
    changed = [n for n,v in protected.items() if signature(scene.objects[n])!=v]
    assert not changed and before_names <= set(scene.objects.keys())
    assert scene.camera.name == before_camera
    assert len(ground.data.polygons)+sum(len(o.data.polygons) for o in created)==len(faces)
    scene['boas_validation_revision']='R30B.75'
    text=bpy.data.texts.new('B75 | PASSEIOS | fontes e limites')
    text.write(json.dumps({'derivation':'docs/reports/blender/centro-expansion/walkways_b75_derivation.json','features':derivation['features'],
                           'notes':'Superfície subdividida B74: passeios removidos da base e encaixados por bordas compartilhadas. Sem planos elevados sobre o terreno. Larguras OSM candidatas; não levantamento. Escadas, travessias e conflitos excluídos; ruas finais e altimetria absoluta pendentes.'},ensure_ascii=False))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active; sp.region_3d.view_location=(750,-1120,35); sp.region_3d.view_distance=1250
                sp.region_3d.view_rotation=Vector((.4,-.8,1.3)).to_track_quat('Z','Y'); sp.region_3d.view_perspective='ORTHO'
                sp.shading.type='SOLID'; sp.shading.color_type='MATERIAL'; sp.overlay.show_overlays=False
    bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
except Exception:
    if Path(bpy.data.filepath).resolve() == (root/source['file']).resolve():
        ground.data=old_ground_data
        for ob in created: bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(collection)
    raise

after={'file':output.relative_to(root).as_posix(),'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),'revision':'R30B.75'}
report={'schema':'boas/centro-walkways-b75-scene-v1','source_before':source,'source_after':after,'derivation':'docs/reports/blender/centro-expansion/walkways_b75_derivation.json',
        'terrain_object':ground.name,'walkway_objects':[ob.name for ob in created],'walkway_count':len(created),'protected_signatures':protected,
        'protected_changes':changed,'partitions':partitions,'source_reopened':False,'motor_roads_built':False,'production_ready':False,
        'rondesp_replay_preserved':True,'driver_camera':before_camera,'rondesp_ground_probe_evidence':'docs/reports/blender/centro-expansion/rondesp_ground_probe_b74.json',
        'new_vehicle_physics_test_performed':False,'terrain_surface_geometry_preserved':'Subdivisão planar, controles originais idênticos; coerência numérica <=0,12 mm nos pontos inseridos'}
(reports/'scene_b75.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**after,'parent_file':source['file'],'status':'validation_candidate','evidence':'docs/reports/blender/centro-expansion/scene_b75.json',
       'notes':'Passeios com largura OSM explícita recortados na superfície candidata; ruas finais, altimetria e circulação pendentes.','source_reopened':False}
for e in catalog['revisions']:
    if e['file']==source['file']:e['status']='superseded_validation'
catalog['revisions'].append(entry);catalog['validation_source']=entry
catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source':after,'walkways':len(created),'protected_changes':changed,'roads_built':False},ensure_ascii=False))
