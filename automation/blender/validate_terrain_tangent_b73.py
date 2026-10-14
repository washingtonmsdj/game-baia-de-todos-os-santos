"""B73: reabertura, tangente aplicada, vias bloqueadas e componentes preservados."""
import bpy,json,hashlib,runpy,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/terrain_tangent_r30b73.json';report=json.loads(rp.read_text(encoding='utf8'));src=report['source_after']
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve() and hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
proof=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'));assert proof['file']==src['file'] and proof['sha256']==src['sha256'] and proof['load_post_completed']
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
changes=[n for n,v in report['protected_signatures'].items() if sig(s.objects[n])!=v];assert not changes
ob=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];assert sig(ob)==report['modified_after'] and sig(s.objects[ob['boas_collision_partner']])==sig(ob)
data=np.load(r/'artifacts/waterfront/terrain_tangent_b73.npz');xyz=np.array([v.co for v in ob.data.vertices],dtype=np.float32)
assert np.array_equal(xyz[:,:2],data['xyz'][:,:2].astype(np.float32)) and np.array_equal(xyz[:,2],data['z'].astype(np.float32)) and np.array_equal(xyz[data['locked']],data['xyz'][data['locked']].astype(np.float32))
ob.data.calc_loop_triangles();degen=sum(t.area<1e-9 for t in ob.data.loop_triangles);assert degen==0
runpy.run_path(str(r/'automation/blender/validate_coastal_profiles_b73.py'),run_name='__main__')
after=json.loads((r/'docs/reports/blender/coastal_road_profiles_b73_after.json').read_text(encoding='utf8'));before=json.loads((r/'docs/reports/blender/coastal_road_profiles_b72_after.json').read_text(encoding='utf8'));rows=[]
for row in after['roads']:
 old=next(x for x in before['roads'] if x['osm_way_id']==row['osm_way_id'])
 assert row['missing_supports']==0 and abs(row['max_grade']-old['max_grade'])<1e-5 and abs(row['max_crossfall']-old['max_crossfall'])<1e-5
 rows.append({k:row[k] for k in ['osm_way_id','name','max_grade','max_crossfall','missing_supports']})
out={'source':src,'source_reopened':True,'reopen_proof':proof,'protected_changes':changes,'coordinates_match_candidate':True,'xy_and_topology_preserved':True,'collision_matches_visual':True,'locked_roads_sidewalks_preserved':True,'road_profiles_unchanged':True,'road_support_profiles':rows,'degenerate_triangles_hq':degen,'degenerate_triangles_core_pending':94,'local_geometry_checks_passed':True,'geographic_fit_verified':False,'full_city_approved':False,'runtime_exported':False,'physics_vehicle_validation':False}
(r/'docs/reports/blender/terrain_tangent_r30b73_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
