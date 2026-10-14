"""B71: aplicar encontro norte por controles da cena, mantendo XY e núcleo."""
import bpy,bmesh,json,hashlib,runpy,shutil,numpy as np,math
from pathlib import Path
from mathutils import Vector,Euler
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.70' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b71_encontro_norte_cais.blend';assert not out.exists()
assert shutil.disk_usage(r).free>(r/src['file']).stat().st_size*2+160*1024**2
candidate=json.loads((r/'docs/reports/blender/north_junction_b71_candidate.json').read_text(encoding='utf8'))
assert candidate['source']['sha256']==src['sha256'] and candidate['finite'] and candidate['floor_after']['above_200percent']==0 and candidate['floor_after']['maximum']<.65
data=np.load(r/'artifacts/waterfront/north_junction_b71.npz')
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];quay=s.objects['CAIS | contenção costeira alinhada à linha de costa']
modified=[fill,quay,s.objects[fill['boas_collision_partner']],s.objects[quay['boas_collision_partner']]]
previous=json.loads((r/'docs/reports/blender/coastal_junction_r30b70.json').read_text(encoding='utf8'))
names=set(previous['protected_signatures'])|{'B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','B62 | COLLISION | pavimento e costura limpa'}
names-=set(o.name for o in modified)
protected={n:sig(s.objects[n]) for n in sorted(names)}
before={o.name:sig(o) for o in modified}
prepared=[];qa=[]
for ob,key in [(fill,'fill'),(quay,'quay')]:
 col=s.objects[ob['boas_collision_partner']];assert sig(ob)==sig(col)
 xyz=np.array([list(v.co) for v in ob.data.vertices],float);assert np.array_equal(xyz,data[key+'_xyz'])
 coords=xyz.copy();coords[:,2]=data[key+'_z'];me=ob.data.copy();me.vertices.foreach_set('co',coords.astype(np.float32).ravel());me.update();me.calc_loop_triangles()
 bm=bmesh.new();bm.from_mesh(me)
 row={'object':ob.name,'vertices':len(me.vertices),'polygons':len(me.polygons),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'edges_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'boundary_edges':sum(e.is_boundary for e in bm.edges)}
 bm.free();assert row['degenerate_triangles']==0 and row['edges_more_than_two_faces']==0
 prepared.append((ob,col,me));qa.append(row)
for ob,col,me in prepared:
 ob.data=me;col.data=me.copy()
 for o in (ob,col):
  o['boas_revision']='R30B.71';o['boas_source_report']='docs/reports/blender/north_junction_r30b71.json';o['boas_height_status']='ADAPT_LOCAL_CORE_CONTACT_NOT_SURVEYED';o['boas_gameplay_approved']=False
changes=[n for n,old in protected.items() if sig(s.objects[n])!=old];assert not changes
s['boas_validation_revision']='R30B.71'
for win in bpy.context.window_manager.windows:
 for ar in win.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.overlay.show_extras=False
   sp.region_3d.view_location=Vector((-288,32,7.7));sp.region_3d.view_distance=35;sp.region_3d.view_rotation=Euler((math.radians(53),0,math.radians(32)),'XYZ').to_quaternion();sp.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={'schema':'boas/north-junction-r30b71-v1','source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.71','sha256':sha},'candidate':candidate,'modified_before':before,'modified_after':{o.name:sig(o) for o in modified},'protected_signatures':protected,'protected_changes':changes,'mesh_qa':qa,'xy_changed':False,'topology_changed':False,'core_changed':False,'hq_changed':False,'water_changed':False,'roads_changed':False,'real_altimetry_verified':False,'source_dem_changed':False,'approved':False,'runtime_exported':False,'source_reopened':False,'pending':['Níveis reais cais/água e fonte original Aleph','Demais inclinações/encosta e acabamento regional','Inspeção das conexões viárias OSM; larguras reais null','Circulação personagem/carro/NPC não aprovada']}
rp=r/'docs/reports/blender/north_junction_r30b71.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(r/'artifacts/waterfront/blender_revisions_before_b71.json').write_bytes(cp.read_bytes())
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Encontro norte do piso/cais vinculado ao núcleo existente; XY/vias/núcleo/água preservados; altura absoluta não verificada.'}
for e in cat['revisions']:
 if e['file']==src['file']:e['status']='superseded_validation'
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source':report['source_after'],'protected_changes':changes,'qa':qa}))
