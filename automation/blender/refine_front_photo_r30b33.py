"""Corrigir face frontal cinza e fechar empena do passe candidato, antes da entrega."""
import bpy,bmesh,json,hashlib,runpy,shutil
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/cidade_baixa_r30b33.json';report=json.loads(path.read_text(encoding='utf8'))
file=root/report['source_after']['file'];assert Path(bpy.data.filepath).resolve()==file.resolve()
assert not report.get('front_refinement'),'Correção já aplicada'
backup=root/'artifacts/cidade-baixa/r30b33_before_front_refinement.blend'
if not backup.exists():shutil.copy2(file,backup)
functions=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));signature=functions['signature']
ids={'1263035780','1220650503'};rows=[r for r in report['buildings'] if str(r['osm_way_id']) in ids];names=tuple(r['body'] for r in rows)
for n,expected in report['road_signatures'].items():assert signature(scene.objects[n])==expected
source=root/report['source_before']['file']
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==report['source_before']['sha256']
before_objects=set(bpy.data.objects)
with bpy.data.libraries.load(str(source),link=False) as (available,requested):requested.objects=list(names)
donors=dict(zip(names,requested.objects))
for name in names:
    target=scene.objects[name];donor=donors[name];target.data=donor.data.copy()
    target.matrix_world=functions['world_matrix'](donor)
for donor in set(bpy.data.objects)-before_objects:
    if not donor.users_scene:bpy.data.objects.remove(donor,do_unlink=True)
retained=[]
for name in report['created_objects']:
    o=scene.objects[name]
    if str(o.get('osm_way_id','')) in ids:
        data=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if data.users==0:bpy.data.meshes.remove(data)
    else:retained.append(name)
col=bpy.data.collections['ENVIRONMENT_FINAL | Cidade Baixa fotografia R33'];created=[]
def mesh(name,vv,ff,material,props,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(material);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o)
    if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    for k,v in props.items():o[k]=v
    created.append(o.name);return o
palette={key:bpy.data.materials['BAIXA R33 | '+label] for key,label in {'trim':'cornija clara','green':'esquadrias verdes','glass':'vidro de fachada','rose':'lona rosada do toldo','tile':'telha cerâmica','gray':'reboco cinza'}.items()}
white=bpy.data.materials['BAIXA R33 | reboco branco quente'];dark=bpy.data.materials['BAIXA R33 | vãos em sombra']
specs=[(1263035780,3,11.3,7,white,palette['green'],'white_green_rose_awning'),(1220650503,6,21.0,4,palette['gray'],dark,'gray_vertical_ribs')]
new=runpy.run_path(str(root/'automation/blender/photo_frontage_geometry.py'))['model_frontages'](scene,specs,palette,mesh,signature,report['reference_media_id'])
report['buildings']=[next((r for r in new if r['osm_way_id']==old['osm_way_id']),old) for old in report['buildings']]
report['created_objects']=retained+created
bpy.context.view_layer.update()
for name,expected in report['road_signatures'].items():assert signature(scene.objects[name])==expected
bpy.ops.wm.save_as_mainfile(filepath=str(file))
with file.open('rb') as stream:report['source_after']['sha256']=hashlib.file_digest(stream,'sha256').hexdigest()
report['reopened']=False
report['front_refinement']={'gray_front_edge':2,'gable_closed':True,'reason':'Revisão visual da própria modelagem: face anterior estava no lado oposto; empena ausente sob cobertura.','previous_draft_backup':backup.relative_to(root).as_posix()}
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'file':report['source_after']['file'],'gray_front_edge':2,'gable_closed':True,'sha256':report['source_after']['sha256']}))
