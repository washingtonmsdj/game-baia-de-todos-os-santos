"""Estende a junta de topo B96 às duas laterais do mesmo corpo."""
import bpy,bmesh,json,hashlib,runpy,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96';r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());base=Path(bpy.data.filepath)
assert base.name==Path(r['file']).name and q['sha256']==r['sha256'] and q['body_checks']['passed'] and r['reopened']
assert bpy.context.preferences.filepaths.save_version>=1
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted();scene=bpy.context.scene
before=json.loads((out/'before.json').read_text());rows={v['object']:v for v in before['rows']};names=['SUPERIOR | lateral corpo elevado','SUPERIOR | lateral corpo elevado.001'];level=r['controls']['butt_joint_planes']['roof_bottom'];buffers={}
protected={v.name:sig(v) for v in scene.objects if v.type=='MESH' and v.name not in names and (v.get('boas_location_id')=='elevador-lacerda' or v.name=='MVP | terreno corrigido | colisão estática') and not v.constraints}
for name in names:
    o=scene.objects[name];assert sig(o)==rows[name]['signature'];data=o.data.copy();data.name='B96 | junta topo | '+name;T=inv@wm(o)
    for v in data.vertices:v.co=T@v.co
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=Vector((0.,0.,level)),plane_no=Vector((0.,0.,1.)),clear_outer=True,clear_inner=False)
    border=[e for e in bm.edges if e.is_boundary];assert all(all(abs(v.co.z-level)<1e-4 for v in e.verts) for e in border)
    bmesh.ops.holes_fill(bm,edges=border,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert not any(not e.is_manifold for e in bm.edges) and not any(f.calc_area()<1e-9 for f in bm.faces)
    bm.to_mesh(data);bm.free();back=wm(o).inverted()@M
    for v in data.vertices:v.co=back@v.co
    data.update();buffers[name]=data
# O checkpoint inicial tinha a face posterior antes da correção visual.
# O estado atual está reaberto/validado e será o novo backup nativo.
checkpoint=base.with_suffix('.blend1');assert checkpoint.resolve().parent==(root/'blender').resolve()
with checkpoint.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['intermediate_checkpoint']['sha256']
with base.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
oldcheckpoint={**r['intermediate_checkpoint'],'state':'removed_obsolete_in_progress_checkpoint_after_current_validation'};checkpoint.unlink()
assert shutil.disk_usage(root).free>base.stat().st_size*1.1
for name,data in buffers.items():
    o=scene.objects[name];o.data=data;o['boas_generated_revision']='R30B.96';o['boas_provenance_ids']=json.dumps(['derived:lacerda-upper-body-b96']);o['boas_joint_type']='BUTT_CONTACT_AT_ROOF';o['boas_joint_level']=level
    p=[inv@wm(o)@v.co for v in o.data.vertices]
    r['changes'].append({'object':name,'operation':'ROOF_BUTT_JOINT_CROP','before':{'signature':rows[name]['signature'],'bounds':rows[name]['bounds']},'after':{'signature':sig(o),'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]}})
assert all(sig(scene.objects[n])==s for n,s in protected.items())
r['intermediate_checkpoint_history']=[oldcheckpoint];r['intermediate_checkpoint']={'file':checkpoint.relative_to(root).as_posix(),'sha256':r['sha256'],'reason':'B96 em andamento: face posterior finalizada, antes de estender a junta ao topo das laterais.'};r['controls']['roof_side_joint_objects']=names;r['reopened']=False
(out/'roof-side-finalization.json').write_text(json.dumps({'objects':names,'roof_bottom':level,'removed_obsolete_checkpoint':oldcheckpoint,'preserved_next_checkpoint':r['intermediate_checkpoint']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'));bpy.ops.wm.save_as_mainfile(filepath=str(base),compress=True)
with checkpoint.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['intermediate_checkpoint']['sha256']
with base.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
for entry in [v for v in cat['revisions'] if v.get('file')==r['file']]+[cat['authoring_source'],cat['validation_source']]:entry['sha256']=r['sha256'];entry['notes']='B96 finalizada: juntas posteriores/laterais sob cobertura sem sobreposição exterior; envelopeXY candidato e cotas relativas.'
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B96','changed_total':len(r['changes']),'roof_side_joint_level':level,'sha256':r['sha256'],'latest_native_checkpoint_preserved':True}))
