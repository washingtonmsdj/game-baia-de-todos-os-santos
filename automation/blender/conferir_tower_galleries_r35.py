"""Conferência da cena reaberta: encaixe, piso superior e ausência de solo nos vãos."""
import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
helpers=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=helpers['signature'];wm=helpers['world_matrix']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text(encoding='utf8'))
with (root/r['source_after']['file']).open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
assert sha==proof['sha256']==r['source_after']['sha256'] and proof['load_post_completed']
assert Path(bpy.data.filepath).resolve()==(root/proof['file']).resolve()
assert all(sig(scene.objects[n])==v for n,v in r['protected_signatures'].items()),'Objeto fora do escopo mudou'
assert all(sig(scene.objects[g['object']])==g['after'] for g in r['terrain_refinement']['geometry'])
I=Matrix(r['tower_alignment']['rotation_world']).inverted();body=scene.objects[r['tower_alignment']['objects'][0]];cap=scene.objects[r['tower_alignment']['objects'][1]]
points=[I@wm(body)@v.co for v in body.data.vertices];sea=min(p.x for p in points);cap_top=max((wm(cap)@v.co).z for v in cap.data.vertices)
assert abs(sea-r['tower_alignment']['sea_face_x_from_upper_wall_m'])<.00002
assert abs(cap_top-r['tower_alignment']['cap_top_from_floor_bottom_m'])<.00002
terrain=scene.objects[r['terrain_names'][0]];terrain.data.calc_loop_triangles();M=wm(terrain);bvh=BVHTree.FromPolygons([M@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
rooms=[]
for s in r['galleries']['segments']:
    p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);samples=[]
    for j in range(s['arch_count']):
        for depth in (.45,s['depth_candidate_m']/2,s['depth_candidate_m']-.25):
            pos=p+u*((j+.5)*s['length_from_existing_controls_m']/s['arch_count'])-n*depth
            hit=bvh.ray_cast(Vector((pos.x,pos.y,140)),Vector((0,0,-1)),240)
            assert hit[0] is not None and hit[0].z<p.z-.12,'Solo ainda ocupa o vão: '+s['name']+' '+str(j)
            samples.append({'bay':j,'depth_from_facade_m':depth,'terrain_z_m':hit[0].z,'floor_z_m':p.z})
    roof=scene.objects['GAL R34 | '+s['name']+' | Laje de apoio da praça'];roof_top=max((wm(roof)@v.co).z for v in roof.data.vertices)
    assert abs(roof_top-s['top_plaza_m'])<.00002
    rooms.append({'segment':s['name'],'samples':samples,'roof_top_m':roof_top,'floor_from_controls_m':p.z})
images=['artifacts/palacio-rio-branco/r30b35_'+name+'.png' for name in ('apoio','interior_palacio','interior_prefeitura')];assert all((root/p).is_file() for p in images)
r['localized_scene_review']={'reopened':proof,'protected_components_unchanged':len(r['protected_signatures']),'sea_face_alignment_m':sea,'cap_contact_z_m':cap_top,'terrain_clear_of_rooms':rooms,'visual_views':images,'runtime_test':False}
proxy=scene.objects[r['terrain_names'][1]];proxy.data.calc_loop_triangles()
PM=wm(proxy);pbvh=BVHTree.FromPolygons([PM@v.co for v in proxy.data.vertices],[list(t.vertices) for t in proxy.data.loop_triangles],all_triangles=True)
proxy_samples=0
for s in r['galleries']['segments']:
    p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world'])
    for j in range(s['arch_count']):
        for depth in (.45,s['depth_candidate_m']/2,s['depth_candidate_m']-.25):
            pos=p+u*((j+.5)*s['length_from_existing_controls_m']/s['arch_count'])-n*depth
            hit=pbvh.ray_cast(Vector((pos.x,pos.y,140)),Vector((0,0,-1)),240)
            assert hit[0] is not None and hit[0].z<p.z-.12,'Proxy ainda ocupa o vão: '+s['name']+' '+str(j)
            proxy_samples+=1
r['localized_scene_review']['proxy_clear_room_samples']=proxy_samples
if r.get('palace_facade_refinement'):
    for name,item in r['palace_facade_refinement']['updated_existing_objects'].items():assert sig(scene.objects[name])==item['after']
    p=r['palace_facade_refinement']['plaza'];assert sig(scene.objects[p['object']])==p['after']
    assert p['before']['geometry_sha256']==p['after']['geometry_sha256'] and p['before']['transform']==p['after']['transform']
    r['localized_scene_review']['palace_updated_components_preserved_on_reopen']=list(r['palace_facade_refinement']['updated_existing_objects'])
    r['localized_scene_review']['plaza_mesh_unchanged']=True
if r.get('palace_portal_correction'):
    for name,item in r['palace_portal_correction']['objects'].items():assert sig(scene.objects[name])==item['after']
if r.get('facade_final_correction'):
    item=r['facade_final_correction'];assert sig(scene.objects[item['object']])==item['after']
r['terrain_refinement']['visual_review']='reviewed_modeling_candidate'
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reopened':True,'preserved_components':len(r['protected_signatures']),'clear_room_samples':sum(len(v['samples']) for v in rooms),'aligned_sea_face_x':sea,'cap_contact_z':cap_top},ensure_ascii=False))
