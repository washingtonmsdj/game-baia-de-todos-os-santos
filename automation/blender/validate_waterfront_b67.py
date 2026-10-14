"""Conferência local read-only da B67 após reabertura; sem aprovação de altura/física."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parents[2];sc=bpy.context.scene
rep=json.loads((r/'docs/reports/blender/waterfront_piers_r30b67.json').read_text(encoding='utf-8'))
entry=rep['source_after'];file=r/entry['file']
assert Path(bpy.data.filepath).resolve()==file.resolve()
with file.open('rb') as h:assert hashlib.file_digest(h,'sha256').hexdigest()==entry['sha256']
proof=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf-8'))
assert proof['file']==entry['file'] and proof['sha256']==entry['sha256'] and proof['load_post_completed']
source=json.loads((r/'docs/reports/blender/coastal_osm_source_check.json').read_text(encoding='utf-8'))
features={f['osm_id']:f for f in source['features']}
def qa(ob):
 me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 result={'object':ob.name,'vertices':len(me.vertices),'faces':len(me.polygons),'degenerate_triangles':sum(t.area<1e-9 for t in me.loop_triangles),'finite':all(math.isfinite(c) for v in me.vertices for c in v.co),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)}
 bm.free();return result
def world(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
def xy(ob):return set((round(v.x,4),round(v.y,4)) for v in world(ob))
water=sc.objects['BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'];volume=sc.objects['BAÍA | volume de água no limite do recorte']
vq=qa(volume);assert vq['finite'] and not vq['degenerate_triangles'] and not vq['nonmanifold_edges'] and vq['signed_volume']>0
water_xy=xy(water);assert xy(volume)==water_xy
wz=[v.z for v in world(water)];vz=[v.z for v in world(volume)]
assert max(abs(z-.35) for z in wz)<1e-6 and abs(min(vz)+16)<1e-6 and abs(max(vz)-.35)<1e-6
rows=[]
for item in rep['new_closed_piers']:
 obs={k:sc.objects[item[k]] for k in ('visual','reference','surface','collision')}
 # Pontos de referência plana preservam o footprint; triangulação não introduz largura.
 expected_xy=features[item['osm_id']]['blender_xy'][:-1]
 assert xy(obs['visual'])==xy(obs['reference'])==xy(obs['surface'])==xy(obs['collision'])
 actual_xy=[(p.x,p.y) for p in world(obs['reference'])]
 source_xy_error=max([min(math.hypot(x-a,y-b) for a,b in actual_xy) for x,y in expected_xy]+[min(math.hypot(x-a,y-b) for a,b in expected_xy) for x,y in actual_xy])
 assert source_xy_error<1e-4,('Erro XY fonte salvo',item['osm_id'],source_xy_error)
 surf,coll=obs['surface'],obs['collision']
 assert [tuple(v.co) for v in surf.data.vertices]==[tuple(v.co) for v in coll.data.vertices]
 assert [tuple(p.vertices) for p in surf.data.polygons]==[tuple(p.vertices) for p in coll.data.polygons]
 checks=[qa(ob) for ob in obs.values()]
 assert all(c['finite'] and c['degenerate_triangles']==0 for c in checks)
 assert checks[0]['nonmanifold_edges']==0 and checks[0]['signed_volume']>0
 assert all(p.normal.z>.99 for p in surf.data.polygons)
 rows.append({'osm_id':item['osm_id'],'geometry':checks,'visual_reference_xy_equal':True,'source_xy_max_error_m':source_xy_error,'source_xy_tolerance_m':1e-4,'surface_collision_equal':True,'deck_z_candidate_m':item['deck_z_candidate_m'],'connection_approved':False,'height_surveyed':False})
pts=world(water);usage=Counter(tuple(sorted((a,b))) for p in water.data.polygons for a,b in zip(list(p.vertices),list(p.vertices)[1:]+list(p.vertices)[:1]))
xmin=min(p.x for p in pts);ymin=min(p.y for p in pts);ymax=max(p.y for p in pts)
def artificial(a,b):return (abs(a.x-xmin)<1e-5 and abs(b.x-xmin)<1e-5) or (abs(a.y-ymin)<1e-5 and abs(b.y-ymin)<1e-5) or (abs(a.y-ymax)<1e-5 and abs(b.y-ymax)<1e-5)
expected=set(tuple(sorted(((round(pts[a].x,4),round(pts[a].y,4)),(round(pts[b].x,4),round(pts[b].y,4))))) for (a,b),count in usage.items() if count==1 and not artificial(pts[a],pts[b]))
foam=[]
for name in ('R30A8 | FOAM | linha costeira','R30A8 | FOAM | halo costeiro'):
 ob=sc.objects[name];actual=set()
 for sp in ob.data.splines:
  coords=[ob.matrix_world@p.co.xyz for p in sp.points]
  for a,b in zip(coords,coords[1:]):actual.add(tuple(sorted(((round(a.x,4),round(a.y,4)),(round(b.x,4),round(b.y,4))))))
 assert actual==expected,(name,len(actual),len(expected))
 foam.append({'object':name,'coastline_segments':len(actual),'matches_current_water_boundary_excluding_clip':True})
result={'schema':'boas/waterfront-piers-b67-validation-v1','source':entry,'source_reopened':True,'reopen_proof':proof,'water_volume':vq,'volume_footprint_matches_water':True,'water_level_m':.35,'volume_range_m':[min(vz),max(vz)],'volume_is_bathymetry':False,'new_piers':rows,'foam':foam,'local_geometry_checks_passed':True,'real_fidelity_approved':False,'runtime_exported':False,'pending':rep['pending'],'geometry_changed':False}
(r/'docs/reports/blender/waterfront_piers_r30b67_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reopened':True,'piers_checked':len(rows),'volume_nonmanifold':vq['nonmanifold_edges'],'local_geometry_checks_passed':True}))
