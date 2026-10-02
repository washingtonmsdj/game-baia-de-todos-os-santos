"""Recuperar modelagem autoral melhor da B23, sem reverter terreno/correções B30."""
import bpy,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];plan=json.loads((root/'docs/reports/blender/facade_regression_b23_b31.json').read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(root/plan['source_before']['file']).resolve()
functions=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));signature=functions['signature'];world_matrix=functions['world_matrix']
for name,expected in plan['road_signatures'].items():assert signature(scene.objects[name])==expected
source=root/plan['restore_source']
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==plan['restore_source_sha256']
def collection(name):
    col=bpy.data.collections.get(name)
    if col is None:col=bpy.data.collections.new(name)
    if col.name not in scene.collection.children:scene.collection.children.link(col)
    return col
archive=collection('REFERENCE | Substituições regressivas R31')
final=collection('ENVIRONMENT_FINAL | Comércio B23 preservado');final['boas_role']='visual_environment'
original=json.loads((root/'docs/reports/blender/cidade_baixa_r30b31.json').read_text(encoding='utf8'));ids={str(i) for i in plan['restore_osm_ids']};hidden=[];restored=[]
for name in original['created_facade_objects']:
    o=scene.objects.get(name)
    if o and str(o.get('osm_way_id','')) in ids:
        if o.name not in archive.objects:archive.objects.link(o)
        for col in list(o.users_collection):
            if col!=archive:col.objects.unlink(o)
        o.hide_render=True;o.hide_set(True);o['boas_archive_reason']='Regressão indicada pelo usuário: reutilizar fachada/toldo autorais B23, sem refazer.';hidden.append(name)
# Os componentes originais já estão conservados na cena; restaurar dados só se divergiram.
needed=plan['body_names']+plan['legacy_components_differing_from_source'];before_objects=set(bpy.data.objects);before_meshes=set(bpy.data.meshes)
requested_names=tuple(needed)
with bpy.data.libraries.load(str(source),link=False) as (available,requested):requested.objects=list(requested_names)
donors=dict(zip(requested_names,requested.objects))
for name in plan['body_names']:
    target=scene.objects[name];donor=donors[name];row=next(r for r in original['buildings'] if r['body']==name);xy=row['footprint_controls_xy'];N=len(donor.data.vertices)//2;mw=world_matrix(donor)
    oldxy=[(mw@v.co).to_2d() for v in list(donor.data.vertices)[:N]]
    assert max(min((p-Vector(q)).length for q in xy) for p in oldxy)<.001
    target.data=donor.data.copy();target.matrix_world=mw
    for key in list(target.keys()):
        if key.startswith(('boas_facade_reference','boas_height_candidate','boas_foundation_z_method')):del target[key]
    for key in donor.keys():
        if key!='_RNA_UI':target[key]=donor[key]
    target['boas_revision']='R30B.32';target['boas_model_restored_from']=plan['restore_source'];target['boas_restoration_reason']='Preservar modelagem autoral preferida pelo usuário; desfazer substituição regressiva de R31.'
    target['boas_footprint_controls']=json.dumps(xy)
for name in plan['legacy_component_names']:
    o=scene.objects[name]
    if name in donors:o.data=donors[name].data.copy();o.matrix_world=world_matrix(donors[name])
    if o.name not in final.objects:final.objects.link(o)
    for col in list(o.users_collection):
        if col!=final:col.objects.unlink(o)
    o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
    if 'boas_archive_reason' in o:del o['boas_archive_reason']
    o['boas_model_restored_from']=plan['restore_source'];o['boas_revision']='R30B.32';restored.append(name)
for o in set(bpy.data.objects)-before_objects:
    if not o.users_scene:bpy.data.objects.remove(o,do_unlink=True)
for me in set(bpy.data.meshes)-before_meshes:
    if me.users==0:bpy.data.meshes.remove(me)
bpy.context.view_layer.update()
for name,expected in plan['road_signatures'].items():assert signature(scene.objects[name])==expected
scene['boas_architectural_revision']='R30B.32 | Modelagem autoral B23 recuperada; terreno B30 preservado'
destination=root/'blender/salvador_lacerda_r30b32_comercio_preservado.blend';bpy.ops.wm.save_as_mainfile(filepath=str(destination))
report={'source_before':plan['source_before'],'source_after':{'file':destination.relative_to(root).as_posix(),'sha256':hashlib.file_digest(destination.open('rb'),'sha256').hexdigest(),'revision':'R30B.32','scene':scene.name},'restoration_source':plan['restore_source'],'restoration_source_sha256':plan['restore_source_sha256'],'restore_osm_ids':plan['restore_osm_ids'],'restored_bodies':plan['body_names'],'restored_existing_components':restored,'hidden_regressive_components':hidden,'terrain_and_collision_unchanged_from_b30':True,'road_signatures':plan['road_signatures'],'reopened':False,'runtime_exported':False,'car_tests_rerun':False,'status':'authoring_candidate','known_limitations':plan['known_road_limitations'],'visual_review':'pending_restored_author_geometry'}
(root/'docs/reports/blender/cidade_baixa_r30b32.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':report['source_after']['file'],'restored_existing_components':len(restored),'removed_from_final_regressive_components':len(hidden),'terrain_and_collision_equal_b30':True,'source_sha256':report['source_after']['sha256']},ensure_ascii=False))
