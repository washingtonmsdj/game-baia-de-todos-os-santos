"""Conferência local B68 reaberta e inventário da região costeira, sem mutações."""
import bpy,bmesh,json,hashlib,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cat=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf-8'));src=cat['validation_source']
assert src['revision']=='R30B.68' and Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
opened=json.loads((r/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf-8'))
assert opened['load_post_completed'] and opened['sha256']==src['sha256']
report=json.loads((r/'docs/reports/blender/pier_land_contacts_r30b68.json').read_text(encoding='utf-8'))
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
changed=[n for n,old in report['protected_signatures'].items() if sig(s.objects[n])!=old]
assert not changed
def tree(tris):
 vv=[Vector(p) for tri in tris for p in tri]
 return BVHTree.FromPolygons(vv,[(i,i+1,i+2) for i in range(0,len(vv),3)],all_triangles=True,epsilon=1e-7)
region=json.loads((r/report['source_region']).read_text(encoding='utf-8'))
gt=tree([tri for name,tris in region['meshes'].items() if not name.startswith('BAÍA') for tri in tris if abs((Vector(tri[1])-Vector(tri[0])).cross(Vector(tri[2])-Vector(tri[0])).z)>1e-8])
wt=tree(next(tris for name,tris in region['meshes'].items() if name.startswith('BAÍA')))
def hit(t,p):return t.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),300)[0]
probe=json.loads((r/'docs/reports/blender/pier_shore_contacts_b68_probe.json').read_text(encoding='utf-8'))
rows=[]
for contact,feature in zip(report['contacts'],probe['features']):
 assert contact['osm_id']==feature['osm_id']
 top=s.objects[contact['walkable']];visual=s.objects[contact['visual']];collision=s.objects[contact['collision']]
 assert sig(visual)==sig(collision)
 bm=bmesh.new();bm.from_mesh(visual.data);visual.data.calc_loop_triangles()
 qa={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'nonmanifold_vertices':sum(not v.is_manifold for v in bm.verts),'degenerate_triangles':sum(t.area<1e-9 for t in visual.data.loop_triangles),'finite':all(math.isfinite(c) for v in bm.verts for c in v.co),'volume':bm.calc_volume(signed=True)}
 bm.free();assert qa['nonmanifold_edges']==0 and qa['degenerate_triangles']==0 and qa['finite'] and qa['volume']>0
 top.data.calc_loop_triangles();tt=tree([[list(top.matrix_world@top.data.vertices[i].co) for i in tri.vertices] for tri in top.data.loop_triangles])
 edge=min(feature['edges'],key=lambda x:x['max_gap_xy']);a=Vector((*edge['samples'][0]['shore_xy'],0));b=Vector((*edge['samples'][-1]['shore_xy'],0));d=b-a;n=Vector((-d.y,d.x,0)).normalized()
 missing_before=0;missing_after=0;examples=[];total=0
 for k in range(1,81):
  p=a.lerp(b,k/81)
  for j in range(1,101):
   q=p+n*(j*.02);total+=1
   if hit(wt,q) is not None or hit(gt,q) is not None:continue
   missing_before+=1
   if hit(tt,q) is None:
    missing_after+=1
    if len(examples)<15:examples.append([q.x,q.y])
 rows.append({'osm_id':contact['osm_id'],'solid_qa':qa,'visual_collision_identical':True,'coverage_samples':total,'terrestrial_missing_before':missing_before,'terrestrial_missing_after':missing_after,'missing_examples':examples,'max_deck_land_difference_m':contact['max_deck_land_difference_m']})
out={'schema':'boas/pier-land-contacts-b68-validation-v1','source':src,'source_reopened':True,'protected_changes':changed,'contacts':rows,'local_geometry_checks_passed':True,'sampled_gap_coverage_passed':all(row['terrestrial_missing_after']==0 for row in rows),'visual_review':'pending_black_capture','gameplay_approved':False}
(r/'docs/reports/blender/pier_land_contacts_r30b68_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
surfaces=[]
for o in s.objects:
 if o.type!='MESH' or not o.visible_get():continue
 if not any(k in o.name.lower() for k in ('terreno','terrain','encosta','cais','piso contínuo')):continue
 bb=[o.matrix_world@Vector(p) for p in o.bound_box];o.data.calc_loop_triangles()
 largest=sorted((p for p in o.data.polygons if abs(p.normal.z)<.35),key=lambda p:p.area,reverse=True)[:12]
 surfaces.append({'name':o.name,'bounds':[[min(p[k] for p in bb) for k in range(3)],[max(p[k] for p in bb) for k in range(3)]],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'properties':{k:o[k] for k in o.keys() if k.startswith('boas_') and isinstance(o[k],(str,int,float,bool))},'largest_steep_faces':[{'index':p.index,'area':p.area,'center':list(o.matrix_world@p.center),'normal':list(p.normal)} for p in largest]})
(r/'docs/reports/blender/coastal_region_b68_inventory.json').write_text(json.dumps({'source':src,'surfaces':surfaces},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'coverage':out['sampled_gap_coverage_passed'],'contacts':rows,'visible_ground_surfaces':len(surfaces)}))
