"""Confere fonte reaberta, apoios locais, câmera e passagem contínua."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/road_transport_b40.json';report=json.loads(rp.read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(r/report['source_after']['file']).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==report['source_after']['sha256']
assert hashlib.sha256((r/report['source_before']['file']).read_bytes()).hexdigest()==report['source_before']['sha256']
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
assert c['world_source']['revision']=='R30B.30'
ground=s.objects[c['export']['road_object']];proxy=s.objects[c['export']['terrain_proxy']]
def tree(ob):
    me=ob.data;me.calc_loop_triangles()
    xyz=np.array([list(ob.matrix_world@v.co) for v in me.vertices],dtype=np.float64)
    tri=np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
    return BVHTree.FromPolygons(xyz.tolist(),tri.tolist(),all_triangles=True),xyz,tri
gt,_,_=tree(ground);pt,xyz,tri=tree(proxy)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
assert np.isfinite(xyz).all() and not np.any(areas<1e-9)
items=json.loads((r/'artifacts/roads/rondesp/collision_priority_targets.json').read_text(encoding='utf8'))['targets'];local=[]
for item in items:
    point=Vector(item['point']);a=gt.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1)[0];b=pt.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1)[0]
    assert a is not None and b is not None
    local.append(abs(a.z-b.z))
assert max(local)<=.05
actor=s.objects['QA | RONDESP | veiculo na pista'];assert s.camera.parent==actor
assert s.camera.name=='QA | RONDESP | camera motorista'
a=json.loads((r/'docs/reports/blender/rondesp_network_current.json').read_text(encoding='utf8'))
plane_errors=[];proxy_errors=[];missing=0
for f in range(s.frame_start,s.frame_end+1):
    s.frame_set(f)
    for contact in a['vehicle_contacts_asset_local']:
        point=actor.matrix_world@Vector(contact)
        h=gt.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1)[0];ph=pt.ray_cast(point+Vector((0,0,.5)),Vector((0,0,-1)),1)[0]
        if h is None or ph is None:missing+=1
        else:plane_errors.append(abs(h.z-point.z));proxy_errors.append(abs(h.z-ph.z))
assert not missing and max(plane_errors)<.13
report['reopened_validation']={'local_targets':len(local),'local_maximum_difference_m':max(local),'finite_proxy':True,'degenerate_triangles':0,'proxy_vertices':len(proxy.data.vertices),'proxy_faces':len(proxy.data.polygons),'continuous_frames':s.frame_end-s.frame_start+1,'continuous_wheel_contacts':len(plane_errors),'continuous_missing_support':missing,'maximum_wheel_plane_error_m':max(plane_errors),'maximum_continuous_proxy_difference_m':max(proxy_errors),'dynamic_physics_tested':False}
assert not s.objects['QA B40 | GUIAS | direita no sentido da via'].get('boas_approved')
assert bpy.data.collections['QA B40 | FLUXOS CANDIDATOS'].hide_render
report['library_paths']=[lib.filepath for lib in bpy.data.libraries];report['source_reopened']=True
window=bpy.context.window;area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(a for a in area.regions if a.type=='WINDOW')
area.spaces.active.region_3d.view_perspective='CAMERA';s.frame_set(520)
with bpy.context.temp_override(window=window,area=area,region=region):
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
    bpy.ops.screen.screenshot(filepath=str(r/'artifacts/roads/rondesp/b40-driver.png'))
s.frame_set(s.frame_start);report['driver_screenshot']='artifacts/roads/rondesp/b40-driver.png'
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report['reopened_validation']))
