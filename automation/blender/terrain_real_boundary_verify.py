"""Apoio de quatro rodas na ligação real cortada, após reabertura da candidata."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terrain_real_boundary_extension.json';r=json.loads(rp.read_text());cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if Path(bpy.data.filepath).resolve()!=(root/r['candidate_file']).resolve():raise RuntimeError('Candidata não está aberta')
bpy.context.view_layer.update();s=bpy.context.scene.objects[c['export']['road_object']];p=bpy.context.scene.objects[c['export']['terrain_proxy']]
def tree(o):
    o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
st=tree(s);pt=tree(p)
g=json.loads((root/c['staging']['roads']).read_text());ns={n['id']:n for n in g['nodes']};e=next(e for e in g['edges'] if e['id']=='way-1075624458-seg-3');a=Vector((*ns[e['from']]['blender_xy'],0));b=Vector((*ns[e['to']]['blender_xy'],0));forward=(b-a).normalized();side=Vector((-forward.y,forward.x,0))
missing=[];maxerror=0;poses=[];nonplanar=[]
for i in range(41):
    center=a.lerp(b,i/40);zs=[]
    for u,v in [(0,0),(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84)]:
        q=center+forward*u+side*v;origin=Vector((q.x,q.y,160));z=st.ray_cast(origin,Vector((0,0,-1)),350)[0];pz=pt.ray_cast(origin,Vector((0,0,-1)),350)[0]
        if z is None or pz is None:missing.append({'pose':i,'xy':list(q.to_2d()),'source':z is not None,'proxy':pz is not None});continue
        maxerror=max(maxerror,abs(z.z-pz.z))
        if u or v:zs.append(z.z)
    if len(zs)==4:
        residual=abs(zs[0]+zs[3]-zs[1]-zs[2])/4
        if residual>.08:nonplanar.append({'pose':i,'residual_m':residual})
        poses.append({'pose':i,'center_xy':list(center.to_2d()),'wheel_heights':zs,'residual_m':residual})
out={'source_candidate':r['candidate_file'],'reopened':True,'edge_id':e['id'],'osm_way_id':e['osm_way_id'],'four_wheel_poses':len(poses),'probes':205,'missing':missing,'max_visual_collision_delta_m':maxerror,'nonplanar_review':nonplanar,'status':'pass_boundary_ground_support' if not missing and maxerror<=.05 else 'needs_review','widths_changed':False,'real_width_verified_m':None,'dynamic_physics_tested':False,'complete_route_approved':False,'conceicao_conflict_repaired':False,'poses':poses}
(root/'docs/reports/blender/terrain_real_boundary_verify.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
r['reopened']=True;r['verification_report']='docs/reports/blender/terrain_real_boundary_verify.json';r['verification_status']=out['status'];rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
if out['status']=='pass_boundary_ground_support':
    c['world_source'].update(file=r['candidate_file'],sha256=hashlib.file_digest((root/r['candidate_file']).open('rb'),'sha256').hexdigest(),revision='R30B.30',selection_reason='Derivada da R30B23; amplia localmente o recorte de terreno na conexão OSM real da Praça Castro Alves, sem mover vértices anteriores ou alterar larguras. Conceição permanece em revisão, sem circuito/ônibus aprovado.')
    cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;target=Vector((-225,-278,55));eye=target+Vector((17,-23,26));rv=sp.region_3d;rv.view_rotation=(target-eye).to_track_quat('-Z','Y');rv.view_location=target;rv.view_distance=(target-eye).length;rv.view_perspective='PERSP';rv.update();sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
print(json.dumps({k:v for k,v in out.items() if k!='poses'},ensure_ascii=False))
