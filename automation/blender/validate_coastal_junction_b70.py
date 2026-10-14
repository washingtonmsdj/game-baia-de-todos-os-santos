"""Conferência B70 reaberta: geometria local e controles preservados."""
import bpy,bmesh,json,hashlib,runpy,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json'
cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source']
assert src['revision']=='R30B.70' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
opened=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert opened['load_post_completed'] and opened['sha256']==src['sha256']
rp=r/'docs/reports/blender/coastal_junction_r30b70.json';report=json.loads(rp.read_text(encoding='utf8'))
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
changed=[n for n,old in report['protected_signatures'].items() if sig(s.objects[n])!=old]
assert not changed,changed
data=np.load(r/'artifacts/waterfront/coastal_junction_b70.npz')
rows=[];coordinates={}
for key,name in [('hq','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'),('fill','B63 | VISUAL | piso contínuo até o cais')]:
 ob=s.objects[name];col=s.objects[ob['boas_collision_partner']];me=ob.data
 assert sig(ob)==sig(col)==report['modified_after'][name]
 xyz=np.array([list(v.co) for v in me.vertices],dtype=float);coordinates[key]=xyz
 assert np.array_equal(xyz[:,:2],data[key+'_xyz'][:,:2])
 assert np.array_equal(xyz[:,2],data[key+'_z'].astype(np.float32).astype(float))
 me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 row={'object':name,'vertices':len(me.vertices),'polygons':len(me.polygons),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'finite':bool(np.isfinite(xyz).all()),'boundary_edges':sum(e.is_boundary for e in bm.edges),'edges_with_more_than_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),'xy_max_change_m':0,'visual_collision_identical':True}
 bm.free()
 assert row['finite'] and row['degenerate_triangles']==0 and row['edges_with_more_than_two_faces']==0
 assert row['vertices']==report['modified_before'][name]['vertices'] and row['polygons']==report['modified_before'][name]['polygons']
 rows.append(row)
assert np.array_equal(coordinates['hq'][data['locked']],data['hq_xyz'][data['locked']])
binding_errors=[]
for b in report['probe']['boundary_binding']:
 a,c=b['hq_edge'];t=b['edge_t']
 z=coordinates['hq'][a,2]*(1-t)+coordinates['hq'][c,2]*t
 binding_errors.append(abs(coordinates['fill'][b['fill_vertex'],2]-z))
assert max(binding_errors)<1e-5
fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];grades=[]
for tri in fill.data.loop_triangles:
 pts=coordinates['fill'][list(tri.vertices)]
 n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);assert abs(n[2])>1e-12
 grades.append(float(np.linalg.norm(n[:2])/abs(n[2])))
floor={'triangles':len(grades),'grade_over_200percent':sum(g>2 for g in grades),'grade_max':max(grades),'grade_p95':float(np.percentile(grades,95)),'vertices_below_nominal_water':int(np.sum(coordinates['fill'][:,2]<.35))}
assert floor['grade_over_200percent']==2 and floor['vertices_below_nominal_water']==0
out={'schema':'boas/coastal-junction-b70-validation-v1','source':report['source_after'],'source_reopened':True,'local_geometry_checks_passed':True,'protected_changes':changed,'mesh_qa':rows,'boundary_bindings':len(binding_errors),'boundary_max_height_difference_m':max(binding_errors),'locked_road_walkable_vertices':len(data['locked']),'locked_vertices_max_change_m':0,'floor':floor,'visual_review':'partial_region_review_remaining_diagonal_transition_and_unfinished_roads','visual_evidence':'artifacts/waterfront/b70-juncao-cais.png','absolute_altimetry_verified':False,'gameplay_approved':False,'approved':False,'runtime_exported':False,'pending':report['pending']}
vp=r/'docs/reports/blender/coastal_junction_r30b70_validation.json';vp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report['source_reopened']=True;report['validation_evidence']=vp.relative_to(r).as_posix()
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for entry in [cat['validation_source']]+cat['revisions']:
 if entry['file']==src['file']:
  entry.update(source_reopened=True,validation_evidence=vp.relative_to(r).as_posix(),local_geometry_checks_passed=True)
cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_reopened':True,'protected_changes':changed,'floor':floor,'boundary_max_height_difference_m':max(binding_errors),'locked_vertices':len(data['locked'])}))
