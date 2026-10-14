"""Conferência local B72 após reabertura; não certifica toda a cidade."""
import bpy,json,hashlib,runpy,numpy as np
from array import array
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
report=json.loads((r/'docs/reports/blender/city_seam_r30b72.json').read_text(encoding='utf8'));src=report['source_after']
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
proof=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
assert proof['file']==src['file'] and proof['sha256']==src['sha256'] and proof['load_post_completed']
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
def cohash(me):
 a=array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
def tophash(me):
 h=hashlib.sha256()
 for table,key in [(me.loops,'vertex_index'),(me.polygons,'loop_start'),(me.polygons,'loop_total')]:
  a=array('i',[0])*len(table);table.foreach_get(key,a);h.update(a.tobytes())
 return h.hexdigest()
changes=[n for n,old in report['protected_signatures'].items() if sig(s.objects[n])!=old];assert not changes
pairs=[]
for n in report['modified_after']:
 o=s.objects[n];assert sig(o)==report['modified_after'][n]
 assert cohash(o.data)==report['coordinate_hash_after'][n] and tophash(o.data)==report['topology_hash_before'][n]
 partner=s.objects.get(o.get('boas_collision_partner',''))
 if partner:assert sig(o)==sig(partner);pairs.append([n,partner.name])
data=np.load(r/'artifacts/waterfront/manoel_transition_b72.npz')
o=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];xyz=np.array([v.co for v in o.data.vertices],dtype=np.float32)
assert np.array_equal(xyz[:,:2],data['xyz'][:,:2].astype(np.float32)) and np.array_equal(xyz[:,2],data['z'].astype(np.float32))
assert np.array_equal(xyz[data['locked']],data['xyz'][data['locked']].astype(np.float32))
runpy.run_path(str(r/'automation/blender/validate_coastal_profiles_b72.py'),run_name='__main__')
profiles=json.loads((r/'docs/reports/blender/coastal_road_profiles_b72_after.json').read_text(encoding='utf8'));metrics=[];pavement=[]
for row in profiles['roads']:
 expected=next(x for x in report['candidate']['profiles'] if x['osm_way_id']==row['osm_way_id'])
 assert row['missing_supports']==0 and abs(row['max_grade']-expected['max_grade_after'])<1e-5 and abs(row['max_crossfall']-expected['max_crossfall_after'])<1e-5
 metrics.append({k:row[k] for k in ['osm_way_id','name','missing_supports','max_grade','max_crossfall']})
 source=next(x for x in json.loads((r/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'))['roads'] if x['osm_way_id']==row['osm_way_id'])
 mat='VIAS | pavimento de pedra Rua Chile' if source.get('surface')=='sett' else 'MVP | asfalto da ladeira'
 missing=[{'xy':a['xy'],'material':a['center']['material_name'],'object':a['center']['object']} for a in row['samples'] if a['center']['material_name']!=mat]
 pavement.append({'osm_way_id':row['osm_way_id'],'axis_samples':len(row['samples']),'different_surface_samples':len(missing),'different_surface_examples':missing[:10]})
out={'source':src,'source_reopened':True,'reopen_proof':proof,'protected_changes':changes,'coordinates_match_saved_result':True,'xy_and_topology_preserved':True,'collision_pairs_identical':pairs,'locked_other_roads_and_sidewalks_preserved':True,'road_support_profiles':metrics,'road_surface_coverage':pavement,'preexisting_degenerate_triangles_core':94,'local_geometry_checks_passed':True,'geographic_fit_verified':False,'full_city_approved':False,'physics_vehicle_validation':False}
(r/'docs/reports/blender/city_seam_r30b72_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
