"""Corrige conversão de coordenadas da cobertura B100, sem duplicar geometria."""
import bpy,bmesh,json,runpy,hashlib,os,shutil
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-upper-body-b100';r=json.loads((out/'application.json').read_text());scene=bpy.context.scene;file=Path(bpy.data.filepath)
assert file.name=='salvador_lacerda_r30b100_corpo_superior_cobertura.blend' and os.getpid()==r['pid'] and not bpy.data.is_dirty
with file.open('rb') as f:oldhash=hashlib.file_digest(f,'sha256').hexdigest()
assert oldhash==r['sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
expected=dict(r['preserved_signatures'])
for row in r['changes']+r['added']:expected[row['object']]=row['after']['signature']
assert all(sig(scene.objects[n])==s for n,s in expected.items())
name='SUPERIOR | cobertura corpo elevado';o=scene.objects[name];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);T=wm(o).inverted()@M
backup=root/'artifacts/blender-sessions/salvador_lacerda_r30b100_cobertura_pre_qa.blend';assert not backup.exists();shutil.copy2(file,backup)
mesh=o.data.copy();mesh.name='B100 | cobertura frame local reconciliado'
for v in mesh.vertices:v.co=T@v.co
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh)
quality={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free();mesh.update()
assert quality['nonmanifold_edges']==quality['degenerate_faces']==quality['inconsistent_winding_edges']==0 and quality['volume']>0
old=sig(o);o.data.use_fake_user=True;o.data=mesh
for row in r['changes']:
 if row['object']==name:row['after']['signature']=sig(o);row['mesh']=quality
assert all(sig(scene.objects[n])==s for n,s in expected.items() if n!=name)
r['coordinate_frame_repair']={'object':name,'reason':'A cobertura reutiliza objeto com transform próprio: converter o contorno documental para o espaço local da mesh antes de atribuir','before_signature':old,'after_signature':sig(o),'pre_qa_file':backup.relative_to(root).as_posix(),'pre_qa_sha256':oldhash,'model_generator_corrected':True,'other_objects_changed':0}
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(compress=True)
with file.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
r['reopened']=False;(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
for entry in cat['revisions']:
 if entry['file']==r['file']:entry['sha256']=r['sha256']
for key in ('authoring_source','validation_source'):
 assert cat[key]['file']==r['file'];cat[key]['sha256']=r['sha256']
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'roof_frame_corrected':True,'other_objects_changed':0,'sha256':r['sha256'],'pre_qa_preserved':str(backup.relative_to(root))}))
