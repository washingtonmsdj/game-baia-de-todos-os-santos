"""B66: orientação marítima das faces e resíduos numéricos detectados após reabertura."""
import bpy,bmesh,json,hashlib,shutil,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene;cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.65';assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve();assert hashlib.file_digest((r/src['file']).open('rb'),'sha256').hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b66_cais_normais_corrigidas.blend';assert not out.exists();assert shutil.disk_usage(r).free>400*1024**2
water=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];water.data.calc_loop_triangles();wt=BVHTree.FromPolygons([water.matrix_world@v.co for v in water.data.vertices],[list(t.vertices) for t in water.data.loop_triangles],all_triangles=True)
def wet(p):
 h=wt.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
 return h is not None and abs(h.z-.35)<.001
fill=sc.objects['B63 | VISUAL | piso contínuo até o cais'];quay=sc.objects['CAIS | contenção costeira alinhada à linha de costa']
flags=[f.index for f in fill.data.polygons if wet(fill.matrix_world@f.center)];area=sum(fill.data.polygons[i].area for i in flags);assert area<.01,('Resíduo não é desprezível; revisar clipping antes de excluir',area)
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
protected={o.name:sig(o) for o in [water,sc.objects['MVP | terreno corrigido | colisão estática'],sc.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa']]+[o for o in sc.objects if o.name.startswith(('B56 | COLLISION | PIER |','B57 | PIER VISUAL |'))]}
bm=bmesh.new();bm.from_mesh(fill.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in flags],context='FACES')
down=[f for f in bm.faces if f.normal.z<0];bmesh.ops.reverse_faces(bm,faces=down)
me=fill.data.copy();bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();assert not any(t.area<1e-9 for t in me.loop_triangles);fill.data=me
assert not any(wet(fill.matrix_world@f.center) for f in me.polygons),'Novo resíduo na precisão final'
wrong=[]
for f in quay.data.polygons:
 p=quay.matrix_world@f.center;n=quay.matrix_world.to_3x3().inverted().transposed()@f.normal;n.z=0;n.normalize()
 if not wet(p+n*.15) and wet(p-n*.15):wrong.append(f.index)
bm=bmesh.new();bm.from_mesh(quay.data);bm.faces.ensure_lookup_table();bmesh.ops.reverse_faces(bm,faces=[bm.faces[i] for i in wrong]);me=quay.data.copy();bm.to_mesh(me);bm.free();me.update();quay.data=me
remaining=0
for f in me.polygons:
 p=quay.matrix_world@f.center;n=quay.matrix_world.to_3x3().inverted().transposed()@f.normal;n.z=0;n.normalize()
 if not wet(p+n*.15) and wet(p-n*.15):remaining+=1
assert remaining==0
for ob in (fill,quay):
 ob['boas_revision']='R30B.66';partner=sc.objects[ob['boas_collision_partner']];partner.data=ob.data.copy();partner['boas_revision']='R30B.66'
assert all(sig(sc.objects[n])==h for n,h in protected.items())
sc['boas_validation_revision']='R30B.66';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
rep={'schema':'boas/coastal-orientation-b66-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.66','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},'removed_numeric_floor_faces':len(flags),'removed_numeric_area_blender_units2':area,'quay_faces_reversed_seaward':len(wrong),'wrong_outward_faces_after':remaining,'wet_floor_centroids_after':0,'collision_synchronized':True,'protected_changes':[],'road_width_changed':False,'runtime_exported':False,'real_fidelity_approved':False}
rp=r/'docs/reports/blender/coastal_orientation_r30b66.json';rp.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**rep['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Normais do cais voltadas à água e resíduos numéricos do piso removidos; sem alterar pistas, costa ou píeres; passarela e dimensões reais pendentes.'}
for x in cat['revisions']:
 if x['file']==src['file']:x['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();bak=r/'artifacts/waterfront/blender_revisions_before_b66.json';bak.write_bytes(cp.read_bytes());cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8');assert json.loads(cp.read_text(encoding='utf8'))['validation_source']['sha256']==entry['sha256']
print(json.dumps(rep,ensure_ascii=False))
