"""Finaliza B96: junta de topo e cantos sem faces exteriores sobrepostas."""
import bpy,bmesh,json,runpy,hashlib,shutil
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96';base=Path(bpy.data.filepath);scene=bpy.context.scene
r=json.loads((out/'application.json').read_text());assert base.name==Path(r['file']).name and r['reopened']
assert bpy.context.preferences.filepaths.save_version>=1,'Preservar checkpoint nativo antes de finalizar'
assert shutil.disk_usage(root).free>base.stat().st_size*1.1
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature'];M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
name='EDIFICIO | parede posterior alta';o=scene.objects[name];row=next(v for v in r['changes'] if v['object']==name);assert sig(o)==row['after']['signature']
def bounds(obj):
    p=[inv@wm(obj)@v.co for v in obj.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
roof_bottom=bounds(scene.objects['SUPERIOR | cobertura corpo elevado'])[2][0];south_inner=bounds(scene.objects['SUPERIOR | lateral corpo elevado'])[1][1];north_inner=bounds(scene.objects['SUPERIOR | lateral corpo elevado.001'])[1][0]
protected={v.name:sig(v) for v in scene.objects if v.type=='MESH' and v.name!=name and (v.get('boas_location_id')=='elevador-lacerda' or v.name=='MVP | terreno corrigido | colisão estática') and not v.constraints}
data=o.data.copy();data.name='B96 | posterior | juntas sem sobreposição';T=inv@wm(o)
for v in data.vertices:v.co=T@v.co
bm=bmesh.new();bm.from_mesh(data)
for point,normal in [(Vector((0.,0.,roof_bottom)),Vector((0.,0.,1.))),(Vector((0.,south_inner,0.)),Vector((0.,-1.,0.))),(Vector((0.,north_inner,0.)),Vector((0.,1.,0.)))]:
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    border=[e for e in bm.edges if e.is_boundary]
    assert all(all(abs(normal.dot(v.co-point))<1e-4 for v in e.verts) for e in border),'Borda não veio deste corte'
    bmesh.ops.holes_fill(bm,edges=border,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert not any(not e.is_manifold for e in bm.edges) and not any(f.calc_area()<1e-9 for f in bm.faces)
bm.to_mesh(data);bm.free();back=wm(o).inverted()@M
for v in data.vertices:v.co=back@v.co
data.update();old=row['after'];o.data=data;o['boas_joint_type']='BUTT_CONTACT_AT_SIDEWALLS_AND_ROOF';o['boas_joint_planes']=json.dumps({'roof_bottom':roof_bottom,'south_inner':south_inner,'north_inner':north_inner})
assert all(sig(scene.objects[n])==s for n,s in protected.items())
row['intermediate_alignment']=old;row['operation']='COMMON_ALIGNMENT_THEN_BUTT_JOINT_CROP';row['after']={'signature':sig(o),'bounds':bounds(o)}
r['controls']['document_roof_top_z']=r['controls']['target_wall_levels'][1];r['controls']['target_wall_levels'][1]=roof_bottom
r['controls']['butt_joint_planes']={'roof_bottom':roof_bottom,'south_inner':south_inner,'north_inner':north_inner};r['controls']['joint_classification']='EXPECTED_CONTACT / PART_INTERFACE';r['intermediate_checkpoint']={'file':base.with_suffix('.blend1').relative_to(root).as_posix(),'sha256':r['sha256'],'reason':'B96 em andamento, antes da inspeção visual detectar sobreposição das faces exteriores.'};r['reopened']=False
(out/'joint-finalization.json').write_text(json.dumps({'object':name,'before':old,'after':row['after'],'joint_planes':r['controls']['butt_joint_planes'],'scene':scene.name,'classification':'ADAPT_LOCAL / PART_INTERFACE','production_ready':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
scene['lacerda_revision']='R30B.96 | encontro posterior e juntas sem sobreposição exterior';runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
bpy.ops.wm.save_as_mainfile(filepath=str(base),compress=True)
with base.with_suffix('.blend1').open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['intermediate_checkpoint']['sha256']
with base.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(catpath.read_text())
for entry in [v for v in cat['revisions'] if v.get('file')==r['file']]+[cat['authoring_source'],cat['validation_source']]:entry['sha256']=r['sha256'];entry['notes']='B96 finalizada com juntas de topo/cantos sem sobreposição exterior; envelopeXY candidato, cotas relativas documentais.'
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B96','finalized_joint_planes':r['controls']['butt_joint_planes'],'sha256':r['sha256'],'native_checkpoint_preserved':True}))
